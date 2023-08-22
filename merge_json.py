import sys,os
import glob
import json
if __name__ == "__main__":
    
    folder_path = os.getcwd()
    target_dir = os.path.join(folder_path, "electricity")
    assert os.path.isdir(target_dir)
    files = glob.glob(os.path.join(target_dir,"*.json"))
    # print(files)
    out = open("electricity.jsonl","w")
    for file in files:
        with open(file,"r") as f:
            data = json.load(f)
            out.write(json.dumps(data,ensure_ascii=False)+"\n")
    
    print("Finish")
