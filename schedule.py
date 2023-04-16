from mip import Model, xsum, minimize, BINARY
from datetime import datetime
from typing import List, Optional

from AllTypes import Job, Batch, Machine, Operation, TCMB

import pulp

#set schedule according to reschedule interval
def set_schedule(batch: Batch, S: List[int], E: List[int]) -> None:
    for i, operation in enumerate(batch.operations):
        operation.S = S[i]
        operation.E = E[i]

# need scheduled opeartions
def schedule(batch: Batch,
             scheduled_jobs: List[Job],
             machines: List[Machine],
             order_time: datetime,
             beta: int, # time window for a machine, little gap between operations
             end_threads: int = 1,
             max_solutions: int = -1,
             big_m: float = 1e8 # large constant to enforce logical condition
             ) -> None:

    ################
    # Model
    ################

    scheduler = Model(solver_name="cbc")
    scheduler.max_seconds = end_threads

    ################
    # Constants
    ################

    # machines
    M = len(machines)
    T = [m.T for m in machines]

    # operations
    N = batch.get_N()
    P = batch.get_P()
    C = batch.get_C() # compitable machine type of operations
    tau = batch.get_tau()

    # TCMB
    constraints = batch.get_constraints()

    # convert order_time to epoch sec
    t0 = int(order_time.timestamp())

    # scheduled operations
    scheduled_operations = [op for job in scheduled_jobs for op in job.operations]
    N_scheduled = len(scheduled_operations)
    tau_schduled = [op.tau for op in scheduled_operations]
    S_scheduled = [op.S - t0 for op in scheduled_operations]
    E_scheduled = [op.E for op in scheduled_operations]

    ################
    # Variables
    ################

    # start time
    S = [scheduler.add_var(lb=0) for _ in range(N)]

    # binary notation of which machine to process an operation
    F = {}
    for op in range(N):
        for m in range(M):
            if C[op] == T[m]:
                F[op, m] = scheduler.add_var(var_type=BINARY)

    # shared-machine precedence relationship
    Q = {}
    for op1 in range(N):
        for op2 in range(N):
            for m in range(M):
                if op1 != op2 and C[op1] == C[op2] == T[m]:
                    Q[op1, op2, m] = scheduler.add_var(var_type=BINARY)

    # shared-machine precedence between a scheduled and an yet-to-be-scheduled operation
    # prime for scheduled operation
    R_precede = {}
    R_follow = {}
    for op in range(N):
        for op_scheduled in range(N_scheduled):
            if T[E_scheduled[op_scheduled]] == C[op]:
                R_precede[op, op_scheduled] = scheduler.add_var(var_type=BINARY)
                R_follow[op, op_scheduled] = scheduler.add_var(var_type=BINARY)

    # variable for detecting lastly processed operation's end time
    Omega = scheduler.add_var(lb=0, var_type="I")

    ################
    # Constraints
    ################

    # 1-1: the end time of the entire schedule must be larger than the end time of any operation
    for op in range(N):
        scheduler += Omega >= S[op] + tau[op]

    # 2-1: an operation is processed by and only by one machine
    for op in range(N):
        compatible = [m for m in range(M) if C[op] == T[m]]
        scheduler += xsum(F[op, m] for m in compatible) == 1

    #**
    # 2-2: a shared-machine precedence relationship exists between each pair of operations sharing the common machine
    for m in range(M):
        for op1 in range(N):
            #**
            for op2 in range(op1, N):
                if op1 != op2 and C[op1] == C[op2] == T[m]:
                    # AND circuit
                    # not quite sure yet
                    # op1 before op2 and op2 before op1 can not happend at the same time
                    scheduler += Q[op1, op2, m] + Q[op2, op1, m] <= F[op1, m]
                    scheduler += Q[op1, op2, m] + Q[op2, op1, m] <= F[op2, m]
                    scheduler += Q[op1, op2, m] + Q[op2, op1, m] >= F[op1, m] + F[op2, m] - 1

    # 2-3: the shared-machine precedence relationship between a certain pair of operations can exist for at most one machine
    for op1 in range(N):
        for op2 in range(N):
            if C[op1] == C[op2]:
                compatible = [m for m in range(M) if op1 != op2 and C[op1] == C[op2] == T[m]]
                scheduler += xsum(Q[op1, op2, m] for m in compatible) <= 1

    # 2-4: a shared-machine precedence relationship must not violate the operation dependency
    for op1 in range(N):
        for op2 in range(N):
            for m in range(M):
                if P[op1][op2] == 1 and C[op1] == C[op2] == T[m]:
                    scheduler += Q[op2, op1, m] == 0

    #***
    # 2-5: a machine can process at most one operation at a time
    for op1 in range(N):
        for op2 in range(N):
            for m in range(M):
                if op1 != op2 and C[op1] == C[op2] == T[m]:
                    #technique used in MIP to relax the constraint when Q[a, b, m] = 0
                    scheduler += S[op1] + tau[op1] + beta <= S[op2] + big_m * (1 - Q[op1, op2, m])

    # 2-6: the dependency among operations must hold
    for op1 in range(N):
        for op2 in range(N):
            if P[op1][op2] == 1:
                scheduler += S[op1] + tau[op1] <= S[op2]

    # **
    # 3-1: the absolute value of the difference between two operation boundaries is less than or equal to the maximum
    #      tolerable difference. There are four cases depending on the combination of boundaries
    for con in constraints:
        op1 = con.operation_id_1 - 1
        op2 = con.operation_id_2 - 1
        if con.boundary_1 == "start" and con.boundary_2 == "start":
            scheduler += S[op1] - S[op2] <= con.alpha
            scheduler += S[op2] - S[op1] <= con.alpha
        elif con.boundary_1 == "start" and con.boundary_2 == "end":
            scheduler += S[op1] - (S[op2] + tau[op2]) <= con.alpha
            scheduler += (S[op2] + tau[op2]) - S[op1] <= con.alpha
        elif con.boundary_1 == "end" and con.boundary_2 == "start":
            scheduler += (S[op1] + tau[op1]) - S[op2] <= con.alpha
            scheduler += S[op2] - (S[op1] + tau[op1]) <= con.alpha
        elif con.boundary_1 == "end" and con.boundary_2 == "end":
            scheduler += (S[op1] + tau[op1]) - (S[op2] + tau[op2]) <= con.alpha
            scheduler += (S[op2] + tau[op2]) - (S[op1] + tau[op1]) <= con.alpha

    # 4-1: a shared-machine precedence or following relationship must exist for any pair of operations sharing a
    #      common machine to process them, one of which is in a previously scheduled job and the other is in a new job
    for op1 in range(N):
        for op_scheduled in range(N_scheduled):
            if T[E_scheduled[op_scheduled]] == C[op1]:
                scheduler += R_precede[op1, op_scheduled] + R_follow[op1, op_scheduled] == F[op1, E_scheduled[op_scheduled]]

    # 4-2: a machine can process at most one operation at a time (case: an operation in a new job precedes another
    #      operation in a previously scheduled job)
    for op1 in range(N):
        for op_scheduled in range(N_scheduled):
            if T[E_scheduled[op_scheduled]] == C[op1]:
                scheduler += S[op1] + tau[op1] + beta <= S_scheduled[op_scheduled] + big_m * (1 - R_precede[a, op_scheduled])

    # 4-3: a machine can process at most one operation at a time (case: an operation in a new job follows another
    #      operation in a previously scheduled job)
    for op1 in range(N):
        for op_scheduled in range(N_scheduled):
            if T[E_scheduled[op_scheduled]] == C[op1]:
                scheduler += S_scheduled[op_scheduled] + tau_schduled[op_scheduled] + beta <= S[op1] + big_m * (1 - R_follow[op1, op_scheduled])
    ################
    # Objective
    ################

    # scheduler.setObjective(Omega, sense=pulp.LpMinimize)
    scheduler.objective = minimize(Omega)


    ################
    # Optimize
    ################

    # scheduler.solve()
    scheduler.optimize()


    ################
    # Out
    ################

    # Time to start each operation
    # S = [int(round(S[a].varValue)) + t0 for a in range(N)] 
    S = [int(round(S[a].x)) + t0 for a in range(N)]  # rounding might cause a bug in the future


    # Machines selected for each operation
    E = [0] * N
    for op in range(N):
        for m in range(M):
            if C[op] == T[m] and F[op, m].x == 1:
                E[op] = m

    set_schedule(batch, S, E)

    scheduled_jobs.extend(batch.jobs)

    # return pulp.value(Omega)
    return Omega.x



