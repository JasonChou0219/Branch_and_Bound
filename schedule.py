from mip import Model, xsum, minimize, BINARY
from datetime import datetime
from typing import List, Optional

from AllTypes import Job, Batch, Machine, Operation, TCMB

import pulp

def set_schedule(batch: Batch, S: List[int], E: List[int]) -> None:
    for i, operation in enumerate(batch.operations):
        operation.S = S[i]
        operation.E = E[i]


def schedule(batch: Batch,
             scheduled_jobs: List[Job],
             machines: List[Machine],
             order_time: datetime,
             beta: int, # time window for a machine, little gap between operations
             threads: int = 1,
             max_solutions: int = -1,
             big_m: float = 1e8 # large constant to enforce logical condition
             ) -> None:

    ################
    # Model
    ################

    scheduler = Model(solver_name="cbc")
    scheduler.max_seconds = threads

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
    N_prime = len(scheduled_operations)
    tau_prime = [op.tau for op in scheduled_operations]
    S_prime = [op.S - t0 for op in scheduled_operations]
    E_prime = [op.E for op in scheduled_operations]

    ################
    # Variables
    ################

    # start time
    S = [scheduler.add_var(lb=0) for _ in range(N)]

    # binary notation of which machine to process an operation
    F = {}
    for a in range(N):
        for m in range(M):
            if C[a] == T[m]:
                F[a, m] = scheduler.add_var(var_type=BINARY)

    # shared-machine precedence relationship
    Q = {}
    for a in range(N):
        for b in range(N):
            for m in range(M):
                if a != b and C[a] == C[b] == T[m]:
                    Q[a, b, m] = scheduler.add_var(var_type=BINARY)

    # shared-machine precedence between a scheduled and an yet-to-be-scheduled operation
    # prime for scheduled operation
    R_precede = {}
    R_follow = {}
    for a in range(N):
        for b_prime in range(N_prime):
            if T[E_prime[b_prime]] == C[a]:
                R_precede[a, b_prime] = scheduler.add_var(var_type=BINARY)
                R_follow[a, b_prime] = scheduler.add_var(var_type=BINARY)

    # variable for detecting lastly processed operation's end time
    Omega = scheduler.add_var(lb=0, var_type="I")

    ################
    # Constraints
    ################

    # 1-1: the end time of the entire schedule must be larger than the end time of any operation
    for a in range(N):
        scheduler += Omega >= S[a] + tau[a]

    # 2-1: an operation is processed by and only by one machine
    for a in range(N):
        compatible = [m for m in range(M) if C[a] == T[m]]
        scheduler += xsum(F[a, m] for m in compatible) == 1

    # 2-2: a shared-machine precedence relationship exists between each pair of operations sharing the common machine
    for m in range(M):
        for a in range(N):
            for b in range(a, N):
                if a != b and C[a] == C[b] == T[m]:
                    # AND circuit
                    # not quite sure yet
                    scheduler += Q[a, b, m] + Q[b, a, m] <= F[a, m]
                    scheduler += Q[a, b, m] + Q[b, a, m] <= F[b, m]
                    scheduler += Q[a, b, m] + Q[b, a, m] >= F[a, m] + F[b, m] - 1

    # 2-3: the shared-machine precedence relationship between a certain pair of operations can exist for at most one machine
    for a in range(N):
        for b in range(N):
            if C[a] == C[b]:
                compatible = [m for m in range(M) if a != b and C[a] == C[b] == T[m]]
                scheduler += xsum(Q[a, b, m] for m in compatible) <= 1

    # 2-4: a shared-machine precedence relationship must not violate the operation dependency
    for a in range(N):
        for b in range(N):
            for m in range(M):
                if P[a][b] == 1 and C[a] == C[b] == T[m]:
                    scheduler += Q[b, a, m] == 0

    # 2-5: a machine can process at most one operation at a time
    for a in range(N):
        for b in range(N):
            for m in range(M):
                if a != b and C[a] == C[b] == T[m]:
                    #technique used in MIP to relax the constraint when Q[a, b, m] = 0
                    scheduler += S[a] + tau[a] + beta <= S[b] + big_m * (1 - Q[a, b, m])

    # 2-6: the dependency among operations must hold
    for a in range(N):
        for b in range(N):
            if P[a][b] == 1:
                scheduler += S[a] + tau[a] <= S[b]


    # 3-1: the absolute value of the difference between two operation boundaries is less than or equal to the maximum
    #      tolerable difference. There are four cases depending on the combination of boundaries
    for con in constraints:
        a = con.operation_id_1 - 1
        b = con.operation_id_2 - 1
        if con.boundary_1 == "start" and con.boundary_2 == "start":
            scheduler += S[a] - S[b] <= con.alpha
            scheduler += S[b] - S[a] <= con.alpha
        elif con.boundary_1 == "start" and con.boundary_2 == "end":
            scheduler += S[a] - (S[b] + tau[b]) <= con.alpha
            scheduler += (S[b] + tau[b]) - S[a] <= con.alpha
        elif con.boundary_1 == "end" and con.boundary_2 == "start":
            scheduler += (S[a] + tau[a]) - S[b] <= con.alpha
            scheduler += S[b] - (S[a] + tau[a]) <= con.alpha
        elif con.boundary_1 == "end" and con.boundary_2 == "end":
            scheduler += (S[a] + tau[a]) - (S[b] + tau[b]) <= con.alpha
            scheduler += (S[b] + tau[b]) - (S[a] + tau[a]) <= con.alpha

    # 4-1: a shared-machine precedence or following relationship must exist for any pair of operations sharing a
    #      common machine to process them, one of which is in a previously scheduled job and the other is in a new job
    for a in range(N):
        for b_prime in range(N_prime):
            if T[E_prime[b_prime]] == C[a]:
                scheduler += R_precede[a, b_prime] + R_follow[a, b_prime] == F[a, E_prime[b_prime]]

    # 4-2: a machine can process at most one operation at a time (case: an operation in a new job precedes another
    #      operation in a previously scheduled job)
    for a in range(N):
        for b_prime in range(N_prime):
            if T[E_prime[b_prime]] == C[a]:
                scheduler += S[a] + tau[a] + beta <= S_prime[b_prime] + big_m * (1 - R_precede[a, b_prime])

    # 4-3: a machine can process at most one operation at a time (case: an operation in a new job follows another
    #      operation in a previously scheduled job)
    for a in range(N):
        for b_prime in range(N_prime):
            if T[E_prime[b_prime]] == C[a]:
                scheduler += S_prime[b_prime] + tau_prime[b_prime] + beta <= S[a] + big_m * (1 - R_follow[a, b_prime])
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
    for a in range(N):
        for m in range(M):
            if C[a] == T[m] and F[a, m].x == 1:
                E[a] = m

    set_schedule(batch, S, E)

    scheduled_jobs.extend(batch.jobs)

    # return pulp.value(Omega)
    return Omega.x



