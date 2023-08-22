import os
import tiktoken
import json
import shutil
from multiprocessing import Pool, cpu_count


def ele_filter(src_folder, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".json") and ("eess" in file or "cond-mat" in file or "physics" in file):
                src_path = os.path.join(root, file)
                dst_path = os.path.join(dest_folder, file)
                shutil.copy(src_path, dst_path)


def count_tokens_for_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count tokens using tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(content))

    return num_tokens

def process_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count tokens using tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(content))

    # Count tokens for each field
    field_tokens = {}
    json_data = json.loads(content)
    for field, value in json_data.items():
        field_tokens[field] = len(encoding.encode(str(value)))

    return {'file': os.path.basename(file_path), **field_tokens}

def count_tokens(json_folder):
    total_files = 0
    total_tokens = 0
    each_field_total = {}
    total_tokens_per_field = {}

    file_paths = []
    for root, _, files in os.walk(json_folder):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

    pool = Pool(cpu_count())  # Use all available CPU cores
    results = pool.map(process_json_file, file_paths)
    pool.close()
    pool.join()

    each_file_tokens = results
    for result in results:
        total_files += 1
        for field, value in result.items():
            if field != 'file':
                if field in each_field_total:
                    each_field_total[field] += value
                else:
                    each_field_total[field] = value

                if field in total_tokens_per_field:
                    total_tokens_per_field[field] += value
                else:
                    total_tokens_per_field[field] = value

    each_file_tokens_total = {field: total for field, total in each_field_total.items()}
    for field_total in each_field_total.values():
        total_tokens += field_total

    all_file = {'file': total_files, 'token': total_tokens}

    result = {
        'each_file_token': each_file_tokens,
        'each_file_token_total': each_file_tokens_total,
        'total': all_file
    }

    return result


if __name__ == "__main__":
    folder_path = os.getcwd()
    print(folder_path)

    # Filter electricity files
    all_files_folder = os.path.join(folder_path, "all_json")
    ele_files_folder = os.path.join(folder_path, "electricity")
    ele_filter(all_files_folder, ele_files_folder)

    # Count tokens and save results
    result = count_tokens(ele_files_folder)
    result_file = os.path.join(folder_path, "result.json")
    with open(result_file, 'w', encoding='utf-8') as result_json:
        json.dump(result, result_json, indent=4)
        

    print("Finish")
