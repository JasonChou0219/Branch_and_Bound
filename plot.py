import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Tuple, Optional
from AllTypes import Machine, Job, Operation, Batch

def epochsec2datetime(epochsec: int) -> datetime:
    return datetime.fromtimestamp(epochsec)

def find_operation_by_id(operations, operation_id):
    for i, operation in enumerate(operations):
        if operation.id == operation_id:
            return i, operation
    raise IndexError(f"Operation with ID {operation_id} not found")


def plot_schedule(
                  all_jobs: List[Job],
                  all_operations: List[Operation],
                  scheduled_operations : List[Operation],
                  machines: List[Machine],
                  init_time: int,
                  xlims: Tuple[float, float] = (-float('inf'), float('inf')),
                #   highlight_job_id: Optional[int] = None,
                  size: Tuple[int, int] = (600, 400),
                  ):

    fig, ax = plt.subplots(figsize=(size[0] / 80, size[1] / 80))

    machine_names = [m.name for m in machines]

    ax.set_yticks(range(len(machine_names)))
    ax.set_yticklabels(machine_names)
    # ax.set_ylim(0, len(machines))

    ax.set_ylim(len(machines) - 0.5, -0.5)
    ax.invert_yaxis()   

    # machine_names = [m.name for m in machines][::-1]

    # ax.set_yticks(range(len(machines)))
    # ax.set_yticklabels(machine_names)
    # ax.set_ylim(len(machines)-0.5, -0.5)


    turn = 0
    x_min = 0
    x_max = -1
    for job in all_jobs:
        cmap = plt.get_cmap('viridis', len(all_jobs) + 1)
        color = cmap(job.id)

        for op in job.operations:  
            if op in scheduled_operations:          
                xs = [op.S - int(init_time.timestamp()), op.end_time() - int(init_time.timestamp())]
                print(f"the start time of operation {op.id} is {op.S - int(init_time.timestamp())}")
                ys = [op.E, op.E]
                print(f"y value of operation {op.id} is {op.E}")
                ax.plot(xs, ys, linewidth=4, color=color)
                label = f"{job.id} : {op.S - int(init_time.timestamp())}, {op.end_time() - int(init_time.timestamp())}"
                if turn == 0:
                    ax.text(xs[0], ys[0]+0.2, label, fontsize=6, ha='center', va='bottom')
                if turn == 1:
                    ax.text(xs[0], ys[0]-0.2, label, fontsize=6, ha='center', va='top')

        for edge in job.dag:
            try:
                index1, op1 = find_operation_by_id(job.operations, edge[0])
                index2, op2 = find_operation_by_id(job.operations, edge[1])
                if op1 in scheduled_operations and op2 in scheduled_operations:
                    xs = [op1.end_time() - int(init_time.timestamp()), op2.S - int(init_time.timestamp())]
                    ys = [op1.E, op2.E]
                    ax.plot(xs, ys, linestyle='--', color='gray')
                    ax.plot(xs, ys, linestyle='--', color='gray')
                    if op2.end_time() - int(init_time.timestamp()) > x_max:
                        x_max = op1.end_time() - int(init_time.timestamp())
            except IndexError as e:
                print(e)
        turn = (turn + 1) % 2
    # ax.set_xlim(x_min, x_max)
    ax.set_title('Scheduling Result')
    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    ax.set_xlim(xlims)

    # plt.show()
