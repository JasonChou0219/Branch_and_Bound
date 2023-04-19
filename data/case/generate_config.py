# import os
# import csv
# import random
# import string

# def generate_files(job_num):
#     # 生成config.tsv
#     with open('config.tsv', 'w', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f, delimiter='\t')
#         writer.writerow(['N_job', 'Plot_range'])
#         writer.writerow([job_num, 1000])

#     # 生成machines.tsv
#     max_machine_type = random.randint(3, 10)
#     max_alternative = random.randint(1, 3)

#     with open('machines.tsv', 'w', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f, delimiter='\t')
#         writer.writerow(['Machine_type', 'Machine_name'])

#         for i in range(1, max_machine_type + 1):
#             for j in range(1, max_alternative + 1):
#                 machine_name = f"Machine {string.ascii_uppercase[i-1]}"
#                 if j > 1:
#                     machine_name += f"-{j}"
#                 writer.writerow([i, machine_name])

#     # 生成operations.tsv
#     operation_num = random.randint(1, 10)

#     with open('operations.tsv', 'w', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f, delimiter='\t')
#         writer.writerow(['Operation_ID', 'Compatible_machine', 'Processing_time', 'Note'])

#         for i in range(1, operation_num + 1):
#             compatible_machine = random.randint(1, max_machine_type)
#             processing_time = random.randint(5, 30)
#             note = string.ascii_uppercase[compatible_machine - 1]
#             writer.writerow([i, compatible_machine, processing_time, note])

# # 请根据需要调整job_num参数
# generate_files(job_num=5)



import os
import csv
import random
import string

def generate_files(job_num):
    # 生成config.tsv
    with open('config.tsv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['N_job', 'Plot_range'])
        writer.writerow([job_num, 1000])

    # 生成machines.tsv
    max_machine_type = random.randint(3, 5)
    max_alternative = random.randint(1, 4)

    with open('machines.tsv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Machine_type', 'Machine_name'])

        for i in range(1, max_machine_type + 1):
            alternative_count = random.randint(1, max_alternative)
            for j in range(1, alternative_count + 1):
                machine_name = f"Machine {string.ascii_uppercase[i-1]}-{j}"
                writer.writerow([i, machine_name])

    # 生成operations.tsv
    operation_num = random.randint(1, 10)

    with open('operations.tsv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Operation_ID', 'Compatible_machine', 'Processing_time', 'Note'])

        for i in range(1, operation_num + 1):
            compatible_machine = random.randint(1, max_machine_type)
            processing_time = random.randint(5, 30)
            note = string.ascii_uppercase[compatible_machine - 1]
            writer.writerow([i, compatible_machine, processing_time, note])

# 请根据需要调整job_num参数
generate_files(job_num=3)

