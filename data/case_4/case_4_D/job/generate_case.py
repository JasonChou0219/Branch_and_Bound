import os
import random
import pandas as pd

# def generate_dependency(job_num=3):
#     for i in range(job_num):
#         # 生成随机数量的行
#         row_count = random.randint(2, 6)

#         # 生成Operation_ID_1和Operation_ID_2
#         operation_ids = [random.randint(1, 5) for _ in range(row_count)]
#         operation_id_pairs = [(operation_ids[i], operation_ids[i+1]) for i in range(row_count - 1)]

#         # 创建DataFrame并写入文件
#         dependency_df = pd.DataFrame(operation_id_pairs, columns=["Operation_ID_1", "Operation_ID_2"])
#         dependency_df.to_csv(f"dependency_{i}.tsv", sep="\t", index=False)
def generate_dependency(job_num=3):
    for i in range(job_num):
        # 生成随机数量的行
        row_count = random.randint(2, 6)

        # 生成不重复的Operation_ID_1和Operation_ID_2
        operation_ids = list(range(1, 6))
        random.shuffle(operation_ids)
        operation_ids = operation_ids[:row_count]

        operation_id_pairs = [(operation_ids[i], operation_ids[i + 1]) for i in range(row_count - 1)]

        # 创建DataFrame并写入文件
        dependency_df = pd.DataFrame(operation_id_pairs, columns=["Operation_ID_1", "Operation_ID_2"])
        dependency_df.to_csv(f"dependency_{i}.tsv", sep="\t", index=False)




def generate_tcmb(job_num=3):
    for i in range(job_num):
        # 读取对应的dependency.tsv文件
        dependency_df = pd.read_csv(f"dependency_{i}.tsv", sep="\t")

        # 随机选取行并生成Time_constraint
        selected_rows = random.sample(range(dependency_df.shape[0]), random.randint(1, dependency_df.shape[0]))
        tcmb_df = dependency_df.iloc[selected_rows].reset_index(drop=True)
        tcmb_df["Time_constraint"] = [random.randint(1, 30) for _ in range(tcmb_df.shape[0])]

        # 将结果写入tcmb.tsv文件
        tcmb_df.to_csv(f"tcmb_{i}.tsv", sep="\t", index=False)

if __name__ == "__main__":
    generate_dependency()
    generate_tcmb()

