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
    # print (f"the size of all_jobs is {len(all_jobs)} %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

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
    
    for job in all_jobs:
        cmap = plt.get_cmap('viridis', len(all_jobs) + 1)
        color = cmap(job.id)
        # if highlight_job_id is not None:
        #     if job.id == highlight_job_id:
        #         color = 'darkblue'
        #     else:
        #         color = 'lightgray'

        for op in job.operations:  
            if op in scheduled_operations:          
            # xs = [epochsec2datetime(op.S), epochsec2datetime(op.end_time())]
            # xs = [op.S, op.end_time()]
                xs = [op.S - int(init_time.timestamp()), op.end_time() - int(init_time.timestamp())]
                # ys = [machines[op.E].name, machines[op.E].name]
                #!!!!!!!! y should also be a value
                ys = [op.E, op.E]
                # print(ys)
                # print(f"the machine of operation {op.id} is :  {machines[op.E].name} machine   {op.E}!!!!!!!!!!!!!!!!!!")
                ax.plot(xs, ys, linewidth=4, color=color)
                label = f"{job.id} : {op.S - int(init_time.timestamp())}, {op.end_time() - int(init_time.timestamp())}"
                if turn == 0:
                    ax.text(xs[0], ys[0]+0.2, label, fontsize=6, ha='center', va='bottom')
                if turn == 1:
                    ax.text(xs[0], ys[0]-0.2, label, fontsize=6, ha='center', va='top')

        for edge in job.dag:
            # xs = [epochsec2datetime(job.operations[edge[0] - 1].end_time()), epochsec2datetime(job.operations[edge[1] - 1].S)]
            try:
                index1, op1 = find_operation_by_id(job.operations, edge[0])
                index2, op2 = find_operation_by_id(job.operations, edge[1])
                # if job.id == 1:
                    # print(f"dag first is : {edge[0]}")
                    # print(f"dag second is : {edge[1]}")
                    # print(f"index1 is : {index1}")
                    # print(f"op1 is : {op1.id} ")
                    # print(f"index2 is : {index2}")
                    # print(f"op2 is : {op2.id} ")
                if op1 in scheduled_operations and op2 in scheduled_operations:
                # if job.operations[edge[0] - 1] in scheduled_operations and job.operations[edge[1] - 1] in scheduled_operations:
                    # if job.id == 1:
                    #     print("job_id:", job.id)
                    #     print("operations:")
                    #     for o in job.operations:
                    #         print(o.id)
                    #     print("dag:")
                    #     for e in job.dag:
                    #         print(e)
                    #     print("constraints:")
                    #     for cons in job.constraints:
                    #         print(f"op1 is : {cons.operation_id_1}")
                    #         print(f"op2 is : {cons.operation_id_2}")
                    #         print(f"constraint is : {cons.alpha}")
                        # print(f"grey line op1 is : {job.operations[edge[0] - 1].id} ")
                        # print(f"grey line op2 is : {job.operations[edge[1] - 1].id} ")
                        # print(f"op1 machine is : {job.operations[edge[0] - 1].E} ")
                        # print(f"op2 machine is : {job.operations[edge[1] - 1].E} ")
                    #transform from op_id to the index in job.operations
                    # xs = [job.operations[edge[0] - 1].end_time() - int(init_time.timestamp()), job.operations[edge[1] - 1].S - int(init_time.timestamp())]
                    # # ys = [machines[job.operations[edge[0] - 1].E].name, machines[job.operations[edge[1] - 1].E].name]
                    # ys = [job.operations[edge[0] - 1].E, job.operations[edge[1] - 1].E]
                    xs = [op1.end_time() - int(init_time.timestamp()), op2.S - int(init_time.timestamp())]
                    # ys = [machines[job.operations[edge[0] - 1].E].name, machines[job.operations[edge[1] - 1].E].name]
                    ys = [op1.E, op2.E]
                    ax.plot(xs, ys, linestyle='--', color='gray')
                    ax.plot(xs, ys, linestyle='--', color='gray')
            except IndexError as e:
                print(e)
        turn = (turn + 1) % 2

    ax.set_title('Scheduling Result')
    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    ax.set_xlim(xlims)

    plt.show()
