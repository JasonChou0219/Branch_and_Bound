import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Tuple, Optional
from AllTypes import Machine, Job, Operation

def epochsec2datetime(epochsec: int) -> datetime:
    return datetime.fromtimestamp(epochsec)

def plot_schedule(scheduled_jobs: List[Job],
                  machines: List[Machine],
                  xlims: Tuple[float, float] = (-float('inf'), float('inf')),
                  highlight_job_id: Optional[int] = None,
                  size: Tuple[int, int] = (600, 400)):

    fig, ax = plt.subplots(figsize=(size[0] / 80, size[1] / 80))

    machine_names = [m.name for m in machines][::-1]

    ax.set_yticks(range(len(machines)))
    ax.set_yticklabels(machine_names)
    ax.set_ylim(0, len(machines))


    # color = job.id
    for job in scheduled_jobs:
        cmap = plt.get_cmap('viridis', len(scheduled_jobs) + 1)
        color = cmap(job.id)
        if highlight_job_id is not None:
            if job.id == highlight_job_id:
                color = 'darkblue'
            else:
                color = 'lightgray'

        for op in job.operations:
            # xs = [epochsec2datetime(op.S), epochsec2datetime(op.end_time())]
            xs = [op.S, op.end_time()]
            ys = [machines[op.E].name] * 2
            ax.plot(xs, ys, linewidth=4, color=color)

        for edge in job.dag:
            # xs = [epochsec2datetime(job.operations[edge[0] - 1].end_time()), epochsec2datetime(job.operations[edge[1] - 1].S)]
            xs = [job.operations[edge[0] - 1].end_time(), job.operations[edge[1] - 1].S]
            ys = [machines[job.operations[edge[0] - 1].E].name, machines[job.operations[edge[1] - 1].E].name]
            ax.plot(xs, ys, linestyle='--', color='gray')

    ax.set_title('Scheduling Result')
    ax.set_xlabel('Date/Time')
    ax.set_ylabel('Machine')
    ax.set_xlim(xlims)

    plt.show()
