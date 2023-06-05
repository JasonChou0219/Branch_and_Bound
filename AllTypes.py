from typing import List, Tuple, Dict

class Machine:
    """
    Machine definition.
    """
    def __init__(self, id: int, T: int, name: str):
        self.id = id  # machine id
        self.T = T  # machine type
        self.name = name  # machine name

class Operation:
    """
    Operation definition.
    """
    def __init__(self, job_id: int, id: int, C: int, tau: int, note: str):
        self.job_id = job_id  # parent job id
        self.id = id  # operation id
        self.C = C  # compatible machine type
        self.tau = tau  # process time in sec.
        #S,E可能要变
        self.S = 0  # start time
        self.E = 0  # machine id to process this operation
        self.note = note  # note

    def end_time(self) -> int:
        """
        get end time of an operation
        """
        return self.S + self.tau if self.S != 0 else 0

class TCMB:
    """
    Time constraint by mutual boundaries
    """
    def __init__(self, operation_id_1: int, operation_id_2: int, alpha: int):
        self.operation_id_1 = operation_id_1  # operation id 1
        self.operation_id_2 = operation_id_2  # operation id 2
        self.alpha = alpha  # maximum difference in time between two boundaries

class Job:
    """
    Job definition, containing a series of operations, dependency graph among operations, and TCMB.
    """
    def __init__(self, id: int, operations: List[Operation], dag: List[Tuple[int, int]], constraints: List[TCMB], arrival_time: int, activate: bool):
        self.id = id  # job id
        self.operations = operations  # list of operations
        self.dag = dag  # operation dependency graph
        self.constraints = constraints  # time constraint by mutual boundaries
        self.arrival_time = arrival_time  # arrival time of the job
        self.activate = activate  # whether the job is activated

class Batch:
    """
    To schedule multiple jobs simultaneously, combine those jobs into a single Batch.
    """
    def __init__(self, jobs: List[Job]):
        # need to store info of unfinished : scheduled_operations in unfinished jobs
        self.jobs = jobs  # list of contained jobs
        self.operations = []  # all operations in the jobs in a single vector
        self.operation_indices = {}  # conversion table from (job_id, op_id_in_job) to op_id_in_batch
        self.unscheduled_operations = []    # unscheduled operations
        self.unfinished_jobs = []  # unfinished jobs
    
        # for job in jobs:
        #     for op in job.operations:
        #         self.operations.append(op)
        #         self.unscheduled_operations.append(op)
        #         #operation index is gloabl including shceudled operations
        #         #【job.id, op.id】 -> [0, len -1] map
        #         # len(self.opreations) change as new op added
        #         # start from 1 -> n-1
        #         self.operation_indices[job.id, op.id] = len(self.operations)
        #         # print (f"job_id : {job.id}")
        #         # print (f"op_id : {op.id}")
        #         # print (f"operation_indices : {self.operation_indices[job.id, op.id]}")
        #     # append unfished job into unfinished_jobs
        #     self.unfinished_jobs.append(job)
        

    def get_N(self) -> int:
        """
        get number of operations in a batch
        """
        return len(self.unscheduled_operations)
    
    def get_C(self) -> List[int]:
        """
        get machine type in a batch
        """
        return [op.C for op in self.unscheduled_operations]

    
    def get_tau(self) -> List[int]:
        """
        get processing time in a batch
        """
        return [op.tau for op in self.unscheduled_operations]

    def get_P(self) -> List[List[bool]]:
        """
        get operation dependency graph in a batch
        """
        P = [[False for _ in range(self.get_N())] for _ in range(self.get_N())]
        #iterate through all unfinished jobs, finish the code

        flag = False;

        for job in self.unfinished_jobs:
            # edge0 -> op1, edge1-> op2
            for edge in job.dag:
                # global index of operation
                # need to -1, starting from 1
                global_op1 = self.operation_indices[job.id, edge[0]] - 1
                op1 = self.operations[global_op1]
                global_op2 = self.operation_indices[job.id, edge[1]] - 1
                op2 = self.operations[global_op2]
                if op1 in self.unscheduled_operations and op2 in self.unscheduled_operations:
                    unshceduled_op1 = self.unscheduled_operations.index(op1)
                    unshceduled_op2 = self.unscheduled_operations.index(op2)
                    P[unshceduled_op1][unshceduled_op2] = True
                    # print(f"operaetion {global_op1} is precedent to operation {global_op2} !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    flag = True

        # if flag == False:
        #     print(f"the number of unfinished_jobs is {len(self.unfinished_jobs)} **********************************************")
            # print("Never reach here********************************************************")
        return P
    

    def get_constraints(self) -> List[TCMB]:
        """
        get constrains in a batch
        """
        constraints = []
        for job in self.unfinished_jobs:
            count = 0
            for con in job.constraints:
                key1 = (job.id, con.operation_id_1)
                key2 = (job.id, con.operation_id_2)
                # if key1 not in self.operation_indices:
                    # print(f"Key1 {key1} not found in operation_indices. count = {count}")
                    # print(f"job_id : {job.id}")
                    # print(f"op_id : {con.operation_id_1}")
                # if key2 not in self.operation_indices:
                    # print(f"Key2 {key2} not found in operation_indices. count = {count}  ")
                    # print(f"job_id : {job.id}")
                    # print(f"op_id : {con.operation_id_2}")
                    
                constraints.append(
                    TCMB(
                        self.operation_indices[key1],
                        self.operation_indices[key2],
                        con.alpha,
                    )
                )
                count += 1
        return constraints

    def set_schedule(self, S: List[int], E: List[int]):
        """
        get schedule plan including start and end time of operations in a batch
        """
        for a in range(self.get_N()):
            self.operations[a].S = S[a]
            self.operations[a].E = E[a]

    def update_batch(self, scheduled_jobs: List[Job], scheduled_operations: List[Operation]) -> None:
        """
        update batch after interval scheduling
        """
        # self.jobs = jobs , need to add new jobs
        #self.operations = []  need to add new operations based on job
        #self.operation_indices = {}  # conversion table from (job_id, op_id_in_job) same
        
        # remove scheduled jobs from unfinished_jobs
        for job in scheduled_jobs:
            if job in self.unfinished_jobs:
                self.unfinished_jobs.remove(job)
         # Remove scheduled operations from self.unscheduled_operations
        for op in scheduled_operations:
            if op in self.unscheduled_operations:
                self.unscheduled_operations.remove(op) 
    
    def activate_jobs(self, init_time: int, start_time:int) -> None:
        for job in self.jobs:
            if (job.arrival_time +int(init_time.timestamp())) <= int(start_time.timestamp()) and job.activate == False:
                job.activate = True
                for op in job.operations:
                    self.operations.append(op)
                    self.unscheduled_operations.append(op)
                    #operation index is gloabl including shceudled operations
                    #【job.id, op.id】 -> [0, len -1] map
                    # len(self.opreations) change as new op added
                    # start from 1 -> n-1
                    self.operation_indices[job.id, op.id] = len(self.operations)
                # append unfished job into unfinished_jobs
                print(f"the number of unscheduled_operations is {self.get_N()}")
                print(f"the compatible machines of unscheduled_operations is {self.get_C()}")
                print(f"the processing time of unscheduled_operations is {self.get_tau()}")
                self.unfinished_jobs.append(job)

    def all_activate(self) -> bool:
        for job in self.jobs:
            if job.activate == False:
                return False
        return True