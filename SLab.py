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
    init_time = datetime(2023, 3, 25, 9, 0, 0)
    # start_time = current_time + timedelta(hours=1)
    start_time = init_time
    beta = 1 * 60
    scheduled_jobs = []
    scheduled_operations = []
    interval = 3000
    # run scheduling
    current_time = 0
    # for batch in batches:
    #     execution_time = schedule(batch, scheduled_jobs, scheduled_operations, machines, start_time, beta, interval, end_threads=12)
    # for batch in batches:
    batch = batches[0]
    while batch.get_N() > 0 and len(scheduled_operations) < len(batch.operations):
        # while (len(batch.operations) != len(scheduled_operations)):
        # print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!the number of opeartions is {batch.get_N()}")
        execution_time, scheduled_jobs, scheduled_operations = schedule(batch, machines, scheduled_jobs, scheduled_operations, init_time, start_time, beta, interval, end_threads=12)
        start_time += timedelta(seconds = interval)
        # print(f"the size of scheduled operations is {len(scheduled_operations)}")
    # current_time += execution_time
    # print (f"execution time is {execution_time} !!!!!!!! ")
    # print (f"interval is {interval} !!!!!!!!!!!!")
        # print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!the number of opeartions is {batch.get_N()}")
    # execution_time, scheduled_jobs, scheduled_operations = schedule(batch, machines, scheduled_jobs, scheduled_operations, init_time, start_time + timedelta(seconds = interval), beta, interval, end_threads=12)
    # current_time += execution_time
            # update_batch(batch)
    
    # print(len(scheduled_operations))
    # for op in scheduled_operations:
        # print(f"the machine type of operation{batch.operations.index(op)} is : {op.E} : {machines[op.E].name}!!!!!!!!!!!!!!!!!!")

    # print(f"Jobs will be completed in {current_time / 60} minutes.")

    # save and plot scheduling result
    with open(os.path.join(case_path, f"{case_name}_result"), 'wb') as f:
        pickle.dump((scheduled_jobs, machines, init_time), f)

    plot_schedule(
        batch.jobs,
        batch.operations,
        scheduled_operations, 
        machines,
        init_time,
        xlims=(
            # int((current_time + timedelta(minutes=50)).timestamp()),
            # int((current_time).timestamp()),
            0,
            # int((current_time + timedelta(hours=int(plot_range))).timestamp()),
            10000,
        ),
        size=(800, 600),
    )
    plt.savefig(os.path.join(case_path, f"{case_name}_result.pdf"))



if __name__ == "__main__":
    case_name = "case_4_D"
    case_path = "data/case_4/case_4_D"
    # case_name = "case_1_A" 
    # case_path = "data/case_1/case_1_A"
    main(case_name, case_path)


    # if len(sys.argv) < 3:
    #     print("Usage: python script_name.py case_name case_path")
    #     sys.exit(1)

    # case_name = sys.argv[1]
    # case_path = sys.argv[2]
    # main(case_name, case_path)
