import os
import csv
import random
import string
import pandas as pd

def generate_files(job_num = 3, op_num = 5):
    # generate config.tsv
    with open('config.tsv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['N_job', 'Plot_range'])
        writer.writerow([job_num, 1000])

    # generate machines.tsv
    max_machine_type = random.randint(3, 5)
    max_alternative = random.randint(1, 3)

    with open('machines.tsv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Machine_type', 'Machine_name'])

        for i in range(1, max_machine_type + 1):
            alternative_count = random.randint(1, max_alternative)
            for j in range(1, alternative_count + 1):
                machine_name = f"Machine {string.ascii_uppercase[i-1]}-{j}"
                writer.writerow([i, machine_name])

    # gnerate operations.tsv
    with open('operations.tsv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Operation_ID', 'Compatible_machine', 'Processing_time', 'Note'])

        for i in range(1, op_num + 1):
            compatible_machine = random.randint(1, max_machine_type)
            processing_time = random.randint(5, 30)
            note = string.ascii_uppercase[compatible_machine - 1]
            writer.writerow([i, compatible_machine, processing_time, note])

def generate_dependency(job_num=3, op_num=5):
    for i in range(job_num):
        # random number of rows
        row_count = random.randint(2, op_num)

        # Operation_ID_1 Operation_ID_2 witout repeat
        operation_ids = list(range(1, op_num + 1))
        print("operation_ids", operation_ids)
        random.shuffle(operation_ids)
        print("shuffled operation_ids", operation_ids)
        operation_ids = operation_ids[:row_count]
        print("operation_ids[:row_count]", operation_ids)

        operation_id_pairs = [(operation_ids[i], operation_ids[i + 1]) for i in range(row_count - 1)]
        print("operation_id_pairs", operation_id_pairs)
        # build dateframe and write to file
        dependency_df = pd.DataFrame(operation_id_pairs, columns=["Operation_ID_1", "Operation_ID_2"])
        dependency_df.to_csv(f"job/dependency_{i}.tsv", sep="\t", index=False)

def generate_tcmb(job_num=3):
    for i in range(job_num):
        #read corresponding dependency.tsv file
        dependency_df = pd.read_csv(f"job/dependency_{i}.tsv", sep="\t")

        # random time constraint
        selected_rows = random.sample(range(dependency_df.shape[0]), random.randint(1, dependency_df.shape[0]))
        tcmb_df = dependency_df.iloc[selected_rows].reset_index(drop=True)
        tcmb_df["Time_constraint"] = [random.randint(1, 30) for _ in range(tcmb_df.shape[0])]

        tcmb_df.to_csv(f"job/tcmb_{i}.tsv", sep="\t", index=False)

def generate_arrival_time(job_num=3):
    arrival_times = [random.randint(0, 50) for _ in range(job_num)]
    df = pd.DataFrame({'Job_Arrival_Time': arrival_times})
    df.to_csv('job/arrival_time.tsv', sep='\t', index=False)


if __name__ == "__main__":
    job_num = 3
    op_num = 5
    generate_files(job_num)
    generate_dependency(job_num, op_num)
    generate_tcmb()
    generate_arrival_time()


