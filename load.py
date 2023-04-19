import os
import pandas as pd
from typing import List, Tuple
from AllTypes import Machine, Batch, Operation, TCMB, Job
import re
import numpy as np

def is_non_negative(value):
    return (isinstance(value, int) or isinstance(value, np.int64)) and value >= 0
# def is_zero_or_one(value):
#     return (isinstance(value, int) or isinstance(value, np.int64)) and (value == 0 or value == 1)

# def is_non_negative(s: str) -> bool:
#     pattern = r"^\d+$"
#     return bool(re.match(pattern, s))


def is_machine_name_valid(name):
    return isinstance(name, str) and bool(re.match(r"^Machine [A-Za-z0-9\-]+$", name))

def check_config(df_config):
    if not is_non_negative(df_config.loc[0, "N_job"]):
        raise ValueError("Invalid input: N_job must be a positive integer")

    if not is_non_negative(df_config.loc[0, "Sequential"]):
        raise ValueError("Invalid input: Sequential must be 0 or 1")

    if not is_non_negative(df_config.loc[0, "Plot_range"]):
        raise ValueError("Invalid input: Plot_range must be a positive integer")

def check_machines(df_machines):
    for _, row in df_machines.iterrows():
        if not is_non_negative(row["Machine_type"]):
            raise ValueError("Invalid input: Machine_type must be a positive integer")

        if not is_machine_name_valid(row["Machine_name"]):
            raise ValueError("Invalid input: Machine_name must follow the format 'Machine ' + description")

def check_operations(df_operations):
    for _, row in df_operations.iterrows():
        if not is_non_negative(row["Operation_ID"]):
            raise ValueError("Invalid input: Operation_ID must be a positive integer")

        if not is_non_negative(row["Compatible_machine"]):
            raise ValueError("Invalid input: Compatible_machine must be a positive integer")

        if not is_non_negative(row["Processing_time"]):
            raise ValueError("Invalid input: Processing_time must be a positive integer")
def check_arrival_time(df_arrival_time):
    for _, row in df_arrival_time.iterrows():
        if not is_non_negative(row["Job_Arrival_Time"]):
            raise ValueError("Invalid input: Job_Arrival_time must be a positive integer")

def check_dependency(df_dependency):
    for _, row in df_dependency.iterrows():
        if not is_non_negative(row["Operation_ID_1"]):
            raise ValueError("Invalid input: Operation_ID_1 must be a positive integer")

        if not is_non_negative(row["Operation_ID_2"]):
            raise ValueError("Invalid input: Operation_ID_2 must be a positive integer")

def check_tcmb(df_tcmb):
    for _, row in df_tcmb.iterrows():
        if not is_non_negative(row["Operation_ID_1"]):
            raise ValueError("Invalid input: Operation_ID_1 must be a positive integer")

        if not is_non_negative(row["Operation_ID_2"]):
            raise ValueError("Invalid input: Operation_ID_2 must be a positive integer")

        if not is_non_negative(row["Time_constraint"]):
            raise ValueError("Invalid input: Time_constraint must be a positive integer")



def print_info(batch: Batch) -> None:
    for job in batch.jobs:
        print ("============================================================")
        print("Information of job_id:", job.id)
        op_str = "Operations: "
        for operation in job.operations:
            op_str += str(operation.id) + " "
        print (op_str)
        dag_str = "DAG: "
        for edge in job.dag:
            dag_str += "(" + str(edge[0]) + "," + str(edge[1]) + ")" + " "
        print (dag_str)
        con_str = "Constrains: \n"
        for constraint in job.constraints:
            con_str += "(" + str(constraint.operation_id_1) + "," + str(constraint.operation_id_2) + ")" + ":" + str(constraint.alpha) + " "
        print (con_str)
        print("arrival_time:", job.arrival_time)
        print("activate", job.activate)
        print ("============================================================")


# remain to be rewritten
def load_case(case_path: str) -> Tuple[List[Machine], List[Batch], int]:
    # config
    df_config = pd.read_csv(os.path.join(case_path, "config.tsv"), delimiter="\t")
    check_config(df_config)
    n_job = df_config.loc[0, "N_job"]
    is_sequential = df_config.loc[0, "Sequential"] == 1
    plot_range = df_config.loc[0, "Plot_range"]

    # machines
    df_machines = pd.read_csv(os.path.join(case_path, "machines.tsv"), delimiter="\t")
    check_machines(df_machines)
    machines = [Machine(i, row["Machine_type"], row["Machine_name"]) for i, row in df_machines.iterrows()]

    # job definitions
    df_operations = pd.read_csv(os.path.join(case_path, "operations.tsv"), delimiter="\t")
    check_operations(df_operations)

    df_arrival_time = pd.read_csv(os.path.join(case_path, f"job/arrival_time.tsv"), delimiter="\t")
    check_arrival_time(df_arrival_time)
    # df_dependency = pd.read_csv(os.path.join(case_path, "dependency.tsv"), delimiter="\t")
    # df_tcmb = pd.read_csv(os.path.join(case_path, "tcmb.tsv"), delimiter="\t")
    jobs = [Job(job_id, [], [], [], df_arrival_time.loc[job_id - 1 , "Job_Arrival_Time"] * 60, False) for job_id in range(1, n_job + 1)]

    # remain: a map between opration and job
    # for job_id in range(1, n_job + 1):
    #     df_operations 
    #     for _, row in df_operations.iterrows():
    #         jobs[job_id - 1].operations.append(
    #             Operation(
    #                 job_id,
    #                 row["Operation_ID"],
    #                 row["Compatible_machine"],
    #                 row["Processing_time"] * 60,
    #                 row["Note"],
    #             )
    #         )
    #     #for separate job
    #     for _, row in df_dependency.iterrows():
    #         jobs[job_id - 1].dag.append((row["Operation_ID_1"], row["Operation_ID_2"]))

    #     # only end -> start
    #     for _, row in df_tcmb.iterrows():
    #         jobs[job_id - 1].constraints.append(
    #             # TCMB(
    #             #     row["Operation_ID_1"],
    #             #     row["Point_1"],
    #             #     row["Operation_ID_2"],
    #             #     row["Point_2"],
    #             #     row["Time_constraint"] * 60,
    #             # )
    #             TCMB(
    #                 row["Operation_ID_1"],
    #                 row["Operation_ID_2"],
    #                 row["Time_constraint"]  *  60,
    #             )
    #         )
    for job_id in range(1, n_job + 1):
        df_dependency = pd.read_csv(os.path.join(case_path, f"job/dependency_{job_id - 1}.tsv"), delimiter="\t")
        check_dependency(df_dependency)
        df_tcmb = pd.read_csv(os.path.join(case_path, f"job/tcmb_{job_id - 1}.tsv"), delimiter="\t")
        check_tcmb(df_tcmb)

        operation_order = []
        for _, row in df_dependency.iterrows():
            operation_order.append(row["Operation_ID_1"])
        operation_order.append(df_dependency.iloc[-1]["Operation_ID_2"])

        for operation_id in operation_order:
            operation_row = df_operations.loc[df_operations["Operation_ID"] == operation_id].iloc[0]
            jobs[job_id - 1].operations.append(
                Operation(
                    job_id,
                    operation_row["Operation_ID"],
                    operation_row["Compatible_machine"],
                    operation_row["Processing_time"] * 60,
                    operation_row["Note"],
                )
            )

        for _, row in df_dependency.iterrows():
            jobs[job_id - 1].dag.append((row["Operation_ID_1"], row["Operation_ID_2"]))

        for _, row in df_tcmb.iterrows():
            # print (f"operation_id_1 is {row['Operation_ID_1']}")
            # print (f"operation_id_2 is {row['Operation_ID_2']}")
            # print (f"alpha is {row['Time_constraint'] * 60}")
            jobs[job_id - 1].constraints.append(
                TCMB(
                    row["Operation_ID_1"],
                    row["Operation_ID_2"],
                    row["Time_constraint"] * 60,
                )
            )


    batch = Batch(jobs)
    #schdule separate job sequentially
    # if is_sequential:
    #     for job_id in range(1, n_job + 1):
    #         batches.append(Batch([jobs[job_id - 1]]))
    # else:
    #     batches.append(Batch(jobs))
    # print_info(batches)
    print_info(batch)
    return machines, batch, plot_range


def main():
    case_path = "data/case_4/case_4_D"
    machines, batch, plot_range = load_case(case_path)
    # print("machines:", machines)
    # print("batches:", batches)
    # print("plot_range:", plot_range)

    # for batch in batches:
    #     for job in batch.jobs:
    #         print("job_id:", job.id)
    #         print("operations:")
    #         for operation in job.operations:
    #             print(operation.id)
    #         print("dag:")
    #         for edge in job.dag:
    #             print(edge)
    #         print("constraints:")
    #         for constraint in job.constraints:
    #             print(f"op1 is : {constraint.operation_id_1}")
    #             print(f"op2 is : {constraint.operation_id_2}")
    #             print(f"constraint is : {constraint.alpha}")
        #     for value in row:
        #         print(value)
        # break

        # for job in batch.jobs:
        #     for edge in job.dag:
        #         # print ("job_id:", job.id, "     edge:", edge)
                # P[self.operation_indices[job.id, edge[0]]][self.operation_indices[job.id, edge[1]]] = True

if __name__ == "__main__":
    main()