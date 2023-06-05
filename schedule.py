from mip import Model, xsum, minimize, BINARY
from datetime import datetime
from typing import List, Optional

from AllTypes import Job, Batch, Machine, Operation, TCMB

import pulp
from typing import Tuple
import os

#set schedule according to reschedule interval
# def set_schedule(batch: Batch, S: List[int], E: List[int]) -> None:
#     for i, operation in enumerate(batch.operations):
#         operation.S = S[i]
#         operation.E = E[i]


# need scheduled opeartions
def schedule(batch: Batch,
             machines: List[Machine],
             scheduled_jobs: List[Job],
             scheduled_operations: List[Operation],
             init_time: datetime,
             start_time: datetime,
             beta: int, # time window for a machine, little gap between operations
             interval: int, # reschedule interval
             end_threads: int = 1,
             max_solutions: int = -1,
             big_m: float = 1e8 # large constant to enforce logical condition
             ) -> Tuple[int, List[Job], List[Operation]]:

    #*************************************************************************************
    # Model
    #*************************************************************************************
    print("Start scheduling... @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    scheduler = Model(solver_name="cbc")
    scheduler.verbose = 0
    #omit output
    scheduler.max_seconds = end_threads

    #*************************************************************************************
    # Constants
    #*************************************************************************************

    # machines
    M = len(machines)
    T = [m.T for m in machines]
    print(f"the machine type is {T}")

    # operations
    N = batch.get_N()
    P = batch.get_P()
    C = batch.get_C() # compitable machine type of operations
    tau = batch.get_tau()
    print(f"the size of unscheduled operations is {N}")
    print(f"the tau of unscheduled operations is {tau}")
    print(f"the C of unscheduled operations is {C}")
    print(f"the P of unscheduled operations is {P}")

    # TCMB
    constraints = batch.get_constraints()
    for con in constraints:
        print(f"the operation_id_1 is {con.operation_id_1}")
        print(f"the operation_id_2 is {con.operation_id_2}")
        print(f"the alpha is {con.alpha}")

    # convert start_time to epoch sec
    init = int(init_time.timestamp())
    start = int(start_time.timestamp())
    print(f"the init time is {init}")
    print(f"the start time is {start}")

    # scheduled operations
    scheduled_operations = [op for op in scheduled_operations]
    N_scheduled = len(scheduled_operations)
    tau_schduled = [op.tau for op in scheduled_operations]
    S_scheduled = [op.S - start for op in scheduled_operations]
    E_scheduled = [op.E for op in scheduled_operations]
    print(f"the size of scheduled operations is {len(scheduled_operations)}")
    print(f"the tau of scheduled operations is {tau_schduled}")
    print(f"the S of scheduled operations is {S_scheduled}")
    print(f"the E of scheduled operations is {E_scheduled}")

    #*************************************************************************************
    # Variables
    #*************************************************************************************

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

    #*************************************************************************************
    # Constraints
    #*************************************************************************************

    # 1-1: the end time of the entire schedule must be larger than the end time of any operation
    for op in range(N):
        scheduler += Omega >= S[op] + tau[op]

    # 2-1: an operation is processed by and only by one machine
    for op in range(N):
        compatible = [m for m in range(M) if C[op] == T[m]]
        scheduler += xsum(F[op, m] for m in compatible) == 1

    #??
    # 2-2: a shared-machine precedence relationship exists between each pair of operations sharing the common machine
    for m in range(M):
        for op1 in range(N):
            #??
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

    # 不是紧挨着的operation的precedence是否能被保证？
    # 2-4: a shared-machine precedence relationship must not violate the operation dependency
    for op1 in range(N):
        for op2 in range(N):
            for m in range(M):
                if P[op1][op2] == 1 and C[op1] == C[op2] == T[m]:
                    scheduler += Q[op2, op1, m] == 0

    #?? how to ensure the machine don't process ongoing operation and unshceduled operation
    # for op_schedule in range(N_scheduled):
    #     for op1 in range(N):
    #         for m in range(M):
                
    # 2-5: a machine can process at most one operation at a time
    for op1 in range(N):
        for op2 in range(N):
            for m in range(M):
                if op1 != op2 and C[op1] == C[op2] == T[m]:
                    #technique used in MIP to relax the constraint when Q[a, b, m] = 0
                    scheduler += S[op1] + tau[op1] + beta <= S[op2] + big_m * (1 - Q[op1, op2, m])

    # 2-6: the dependency among operations(both unscheduled) must hold
    for op1 in range(N):
        for op2 in range(N):
            if P[op1][op2] == 1:
                scheduler += S[op1] + tau[op1] <= S[op2]

    #remain to be completed
     # -7: the precedence relationship between a pair of operations (scheduled & unscheduled)in a job must not violate the precedence   
    for op_scheduled in range(N_scheduled):
        for op1 in range(N):
            if (batch.unscheduled_operations[op1].job_id == scheduled_operations[op_scheduled].job_id):
                # <= 两边都得是model变量
                scheduler += scheduled_operations[op_scheduled].S - start + tau_schduled[op_scheduled] - S[op1] <= 0

    # ??
    # 3-1: the absolute value of the difference between two operation boundaries is less than or equal to the maximum
    #      tolerable difference. There are four cases depending on the combination of boundaries
    for con in constraints:
        op1_gloabl = con.operation_id_1 - 1
        op2_global = con.operation_id_2 - 1
        print(f"the op1_gloabl is {op1_gloabl}")
        print(f"the op2_global is {op2_global}")
        op1 = batch.operations[op1_gloabl]
        op2 = batch.operations[op2_global]
        if op1 in batch.unscheduled_operations and op2 in batch.unscheduled_operations:
            op1_unschduled = batch.unscheduled_operations.index(op1)
            op2_unschduled = batch.unscheduled_operations.index(op2)
            print(f"the op1_unschduled is {op1_unschduled}")
            print(f"the op2_unschduled is {op2_unschduled}")
            #1
            #     scheduler += S[op1_unschduled] - S[op2_unschduled] <= con.alpha
            #     scheduler += S[op2_unschduled] - S[op1_unschduled] <= con.alpha
            # 2
            #     scheduler += S[op1_unschduled] - (S[op2_unschduled] + tau[op2_unschduled]) <= con.alpha
            #     scheduler += (S[op2_unschduled] + tau[op2_unschduled]) - S[op1_unschduled] <= con.alpha
            # 3
            #     scheduler += (S[op1_unschduled] + tau[op1_unschduled]) - S[op2_unschduled] <= con.alpha
            #     scheduler += S[op2_unschduled] - (S[op1_unschduled] + tau[op1_unschduled]) <= con.alpha
            # 4
            #     scheduler += (S[op1_unschduled] + tau[op1_unschduled]) - (S[op2_unschduled] + tau[op2_unschduled]) <= con.alpha
            #     scheduler += (S[op2_unschduled] + tau[op2_unschduled]) - (S[op1_unschduled] + tau[op1_unschduled]) <= con.alpha
            scheduler += (S[op1_unschduled] + tau[op1_unschduled]) - S[op2_unschduled] <= con.alpha
            scheduler += S[op2_unschduled] - (S[op1_unschduled] + tau[op1_unschduled]) <= con.alpha
        elif op1 in scheduled_operations and op2 in batch.unscheduled_operations:
            op2_unschduled = batch.unscheduled_operations.index(op2)
            scheduler += op1.S - start + op1.tau - S[op2_unschduled] <= con.alpha
            scheduler += S[op2_unschduled] - (op1.S - start + op1.tau) <= con.alpha



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
                scheduler += S[op1] + tau[op1] + beta <= S_scheduled[op_scheduled] + big_m * (1 - R_precede[op1, op_scheduled])

    # 4-3: a machine can process at most one operation at a time (case: an operation in a new job follows another
    #      operation in a previously scheduled job)
    for op1 in range(N):
        for op_scheduled in range(N_scheduled):
            if T[E_scheduled[op_scheduled]] == C[op1]:
                scheduler += S_scheduled[op_scheduled] + tau_schduled[op_scheduled] + beta - (S[op1] + big_m * (1 - R_follow[op1, op_scheduled])) <= 0
 
    #*************************************************************************************
    # Objective
    #*************************************************************************************

    # scheduler.setObjective(Omega, sense=pulp.LpMinimize)
    scheduler.objective = minimize(Omega)


    #*************************************************************************************
    # Optimize
    #*************************************************************************************

    # scheduler.solve()
    scheduler.optimize()


    #*************************************************************************************
    # Out
    #*************************************************************************************

    # Time to start each operation
    # S = [int(round(S[a].varValue)) + start for a in range(N)] 
    # S = [int(round(S[op].x)) + start for op in range(N)]  # rounding might cause a bug in the future
    S = [int(round(S[i].x)) for i in range(N)] 
    # # Machines selected for each operation
    # E = [0] * N
    # for op in range(N):
    #     for m in range(M):
    #         if C[op] == T[m] and F[op, m].x == 1:
    #             E[op] = m

    #interval schedule
    E = [0] * N
    for op in range(N):
        for m in range(M):
            if C[op] == T[m] and F[op, m].x == 1 and S[op] < interval:
                E[op] = m 
    S = [x + start for x in S]
    print("the start time S is : {S}")

    for op in range(N):
        for m in range(M):
            if C[op] == T[m]:
                F[op, m] = scheduler.add_var(var_type=BINARY)
    # for op in range(N):
    #     for m in range(M):
    #         if C[op] == T[m]:
    #             print(f"the F[op, m] is {F[op, m]}")
    
    # for op1 in range(N):
    #     for op2 in range(N):
    #         for m in range(M):
    #             if op1 != op2 and C[op1] == C[op2] == T[m]:
    #                 print(f"the Q[op1, op2, m] is {Q[op1, op2, m]}")

    for i, operation in enumerate(batch.unscheduled_operations):
        if (S[i] - start < interval):
            operation.S = S[i]
            scheduled_operations.append(operation)
            print(f"Operation scheduled: {i} .")
        operation.E = E[i]
    # print(f"the size of scheduled operations is {len(scheduled_operations)} .") 
    # set_schedule(batch, S, E)
    # for job in batch.unfinished_jobs:
    #     for op in job.operations:
    #         if (op not in scheduled_operations):
    #             continue
    #     # scheduled_jobs.extend(batch.jobs)
    #     # scheduled_jobs.extend(job)
    #     scheduled_jobs.append(job)


    for job in batch.unfinished_jobs:
        all_scheduled = True  # 布尔变量，初始值为 True
        for op in job.operations:
            if op not in scheduled_operations:
                all_scheduled = False  # 只要有一个 operation 没有被 schedule，就将 all_scheduled 设为 False
                break
        if all_scheduled:
            scheduled_jobs.append(job)
    
    # print (f"the size of scheduled jobs is {len(scheduled_jobs)} &&&&&&&&&&&&&&&&&&&&&")

    batch.update_batch(scheduled_jobs, scheduled_operations)
    # print(f"the size of scheduled operations is {len(scheduled_operations)} : schdule_end .") 
    # print(f"the size of scheduled jobs is {len(scheduled_jobs)} : schdule_end .")

    return Omega.x, scheduled_jobs, scheduled_operations



