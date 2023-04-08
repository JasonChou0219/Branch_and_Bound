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
    def __init__(self, operation_id_1: int, boundary_1: str, operation_id_2: int, boundary_2: str, alpha: int):
        self.operation_id_1 = operation_id_1  # operation id 1
        self.boundary_1 = boundary_1  # boundary of operation 1 (begin or end)
        self.operation_id_2 = operation_id_2  # operation id 2
        self.boundary_2 = boundary_2  # boundary of operation 2 (begin or end)
        self.alpha = alpha  # maximum difference in time between two boundaries

class Job:
    """
    Job definition, containing a series of operations, dependency graph among operations, and TCMB.
    """
    def __init__(self, id: int, operations: List[Operation], dag: List[Tuple[int, int]], constraints: List[TCMB]):
        self.id = id  # job id
        self.operations = operations  # list of operations
        self.dag = dag  # operation dependency graph
        self.constraints = constraints  # time constraint by mutual boundaries

class Batch:
    """
    To schedule multiple jobs simultaneously, combine those jobs into a single Batch.
    """
    def __init__(self, jobs: List[Job]):
        self.jobs = jobs  # list of contained jobs
        self.operations = []  # all operations in the jobs in a single vector
        self.operation_indices = {}  # conversion table from (job_id, op_id_in_job) to op_id_in_batch
        
        for job in jobs:
            for op in job.operations:
                self.operations.append(op)
                self.operation_indices[job.id, op.id] = len(self.operations)

    def get_N(self) -> int:
        """
        get number of operations in a batch
        """
        return len(self.operations)

    def get_P(self) -> List[List[bool]]:
        """
        get operation dependency graph in a batch
        """
        P = [[False for _ in range(self.get_N())] for _ in range(self.get_N())]
        for job in self.jobs:
            for edge in job.dag:

                # i = self.operation_indices[job.id, edge[0]] - 1
                # j = self.operation_indices[job.id, edge[1]] - 1
                # print(f"Trying to access P[{i}][{j}]")
                # P[i][j] = True
                P[self.operation_indices[job.id, edge[0]] - 1][self.operation_indices[job.id, edge[1]] - 1] = True
        return P
    
    def get_C(self) -> List[int]:
        """
        get machine type in a batch
        """
        return [op.C for op in self.operations]

    def get_tau(self) -> List[int]:
        """
        get processing time in a batch
        """
        return [op.tau for op in self.operations]

    def get_constraints(self) -> List[TCMB]:
        """
        get constrains in a batch
        """
        constraints = []
        for job in self.jobs:
            for con in job.constraints:
                constraints.append(
                    TCMB(
                        self.operation_indices[job.id, con.operation_id_1],
                        con.boundary_1,
                        self.operation_indices[job.id, con.operation_id_2],
                        con.boundary_2,
                        con.alpha,
                    )
                )
        return constraints

    def set_schedule(self, S: List[int], E: List[int]):
        """
        get schedule plan including start and end time of operations in a batch
        """
        for a in range(self.get_N()):
            self.operations[a].S = S[a]
            self.operations[a].E = E[a]
