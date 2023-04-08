import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple
from mip import Model, xsum, INTEGER
import pulp
import matplotlib.pyplot as plt
import pickle
import sys


from AllTypes import Machine, Batch, Operation, TCMB, Job
from load import load_case
from schedule import schedule
from plot import plot_schedule

def main(case_name: str, case_path: str) -> None:
    machines, batches, plot_range = load_case(case_path)

    # misc parameters
    current_time = datetime(2023, 3, 25, 9, 0, 0)
    order_time = current_time + timedelta(hours=1)
    beta = 1 * 60
    scheduled_jobs = []

    # run scheduling
    execution_time = 0
    for batch in batches:
        execution_time = schedule(batch, scheduled_jobs, machines, order_time, beta, threads=12)
    print(f"Jobs will be completed in {execution_time / 60} minutes.")

    # save and plot scheduling result
    with open(os.path.join(case_path, f"{case_name}_result"), 'wb') as f:
        pickle.dump((scheduled_jobs, machines, current_time), f)

    plot_schedule(
        scheduled_jobs,
        machines,
        xlims=(
            int((current_time + timedelta(minutes=50)).timestamp()),
            int((current_time + timedelta(hours=int(plot_range))).timestamp()),
        ),
        size=(800, 600),
    )
    plt.savefig(os.path.join(case_path, f"{case_name}_result.pdf"))



if __name__ == "__main__":
    case_name = "case1"
    case_path = "data/case_1/case_1_A"
    main(case_name, case_path)


    # if len(sys.argv) < 3:
    #     print("Usage: python script_name.py case_name case_path")
    #     sys.exit(1)

    # case_name = sys.argv[1]
    # case_path = sys.argv[2]
    # main(case_name, case_path)
