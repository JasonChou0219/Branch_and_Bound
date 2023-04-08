import os
import pandas as pd
from typing import List, Tuple
from AllTypes import Machine, Batch, Operation, TCMB, Job

def load_case(case_path: str) -> Tuple[List[Machine], List[Batch], int]:
    # config
    df_config = pd.read_csv(os.path.join(case_path, "config.tsv"), delimiter="\t")
    n_job = df_config.loc[0, "N_job"]
    is_sequential = df_config.loc[0, "Sequential"] == 1
    plot_range = df_config.loc[0, "Plot_range"]

    # machines
    df_machines = pd.read_csv(os.path.join(case_path, "machines.tsv"), delimiter="\t")
    machines = [Machine(i, row["Machine_type"], row["Machine_name"]) for i, row in df_machines.iterrows()]

    # job definitions
    df_operations = pd.read_csv(os.path.join(case_path, "operations.tsv"), delimiter="\t")
    df_dependency = pd.read_csv(os.path.join(case_path, "dependency.tsv"), delimiter="\t")
    df_tcmb = pd.read_csv(os.path.join(case_path, "tcmb.tsv"), delimiter="\t")

    jobs = [Job(job_id, [], [], []) for job_id in range(1, n_job + 1)]

    for job_id in range(1, n_job + 1):
        for _, row in df_operations.iterrows():
            jobs[job_id - 1].operations.append(
                Operation(
                    job_id,
                    row["Operation_ID"],
                    row["Compatible_machine"],
                    row["Processing_time"] * 60,
                    row["Note"],
                )
            )

        for _, row in df_dependency.iterrows():
            jobs[job_id - 1].dag.append((row["Operation_ID_1"], row["Operation_ID_2"]))

        for _, row in df_tcmb.iterrows():
            jobs[job_id - 1].constraints.append(
                TCMB(
                    row["Operation_ID_1"],
                    row["Point_1"],
                    row["Operation_ID_2"],
                    row["Point_2"],
                    row["Time_constraint"] * 60,
                )
            )

    # create batch
    batches = []
    if is_sequential:
        for job_id in range(1, n_job + 1):
            batches.append(Batch([jobs[job_id - 1]]))
    else:
        batches.append(Batch(jobs))

    return machines, batches, plot_range


def main():
    machines, batches, plot_range = load_case("data/case_2")
    # print("machines:", machines)
    # print("batches:", batches)
    # print("plot_range:", plot_range)

    for batch in batches:
        for row in batch.get_P():
            pass;
        #     for value in row:
        #         print(value)
        # break

        # for job in batch.jobs:
        #     for edge in job.dag:
        #         # print ("job_id:", job.id, "     edge:", edge)
                # P[self.operation_indices[job.id, edge[0]]][self.operation_indices[job.id, edge[1]]] = True

if __name__ == "__main__":
    main()