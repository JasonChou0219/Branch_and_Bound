import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Tuple, Optional
from AllTypes import Machine, Job, Operation, Batch

def epochsec2datetime(epochsec: int) -> datetime:
    return datetime.fromtimestamp(epochsec)

def plot_schedule(
                  scheduled_jobs: List[Job],
                  scheduled_operations : List[Operation],
                  machines: List[Machine],
                  start_time: int,
                  xlims: Tuple[float, float] = (-float('inf'), float('inf')),
                #   highlight_job_id: Optional[int] = None,
                  size: Tuple[int, int] = (600, 400),
                  ):

    fig, ax = plt.subplots(figsize=(size[0] / 80, size[1] / 80))

    machine_names = [m.name for m in machines]
    print(machine_names)

    ax.set_yticks(range(len(machine_names)))
    ax.set_yticklabels(machine_names)
    # ax.set_ylim(0, len(machines))

    ax.set_ylim(len(machines) - 0.5, -0.5)
    ax.invert_yaxis()   

    # machine_names = [m.name for m in machines][::-1]

    # ax.set_yticks(range(len(machines)))
    # ax.set_yticklabels(machine_names)
    # ax.set_ylim(len(machines)-0.5, -0.5)


    # color = job.id
    for job in scheduled_jobs:
        cmap = plt.get_cmap('viridis', len(scheduled_jobs) + 1)
        color = cmap(job.id)
        # if highlight_job_id is not None:
        #     if job.id == highlight_job_id:
        #         color = 'darkblue'
        #     else:
        #         color = 'lightgray'

        for op in job.operations:            
            # xs = [epochsec2datetime(op.S), epochsec2datetime(op.end_time())]
            # xs = [op.S, op.end_time()]
            xs = [op.S - int(start_time.timestamp()), op.end_time() - int(start_time.timestamp())]
            # ys = [machines[op.E].name, machines[op.E].name]
            #!!!!!!!! y should also be a value
            ys = [op.E, op.E]
            print(ys)
            print(f"the machine of operation {op.id} is :  {machines[op.E].name} machine   {op.E}!!!!!!!!!!!!!!!!!!")
            ax.plot(xs, ys, linewidth=4, color=color)

        for edge in job.dag:
            # xs = [epochsec2datetime(job.operations[edge[0] - 1].end_time()), epochsec2datetime(job.operations[edge[1] - 1].S)]
            if job.operations[edge[0] - 1] in scheduled_operations and job.operations[edge[1] - 1] in scheduled_operations:
                xs = [job.operations[edge[0] - 1].end_time() - int(start_time.timestamp()), job.operations[edge[1] - 1].S - int(start_time.timestamp())]
                # ys = [machines[job.operations[edge[0] - 1].E].name, machines[job.operations[edge[1] - 1].E].name]
                ys = [job.operations[edge[0] - 1].E, job.operations[edge[1] - 1].E]
                ax.plot(xs, ys, linestyle='--', color='gray')

    ax.set_title('Scheduling Result')
    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    ax.set_xlim(xlims)

    plt.show()




    # data = [(1, 3), (4, 5), (6, 9)]
    # colors = ['red', 'yellow', 'red']
    # # machine_names = [m.name for m in machines]
 
    # # fig, ax = plt.subplots()

    # for i in range(len(data)):
    #     x, y = data[i]
    #     color = colors[i]
    #     ax.axhline(y=y, xmin=x/10, xmax=(x+1)/10, color=color, linewidth=2)

    # plt.show()