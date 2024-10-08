# import re
import regex as re
import os
import json
import shutil
import gzip
import time
from multiprocessing import Pool, cpu_count
import tarfile


def extract_subsection(text):
    subsection_pattern = (
        r"\\subsection\*?\s*\{([\s\S]*?)\}([\s\S]+?)(?=(?:\\subsection)|\Z)"
    )
    subsection_matches = re.findall(subsection_pattern, text, re.DOTALL)

    subsections = []
    for subsection_match in subsection_matches:
        title = subsection_match[0].strip()
        if "\\" in title:
            continue
        content = subsection_match[1].strip()
        subsections.append({"title": title, "text": content})

    return subsections


def extract_latex_content(latex_text, file_name):
    latex_text = re.sub(r"\\(bf|em|Large|sc|LARGE|ls|normalsize)", "", latex_text)
    latex_text = re.sub(r"%", "", latex_text)
    index = latex_text.find("\\begin{thebibliography}")
    if index:
        latex_text = latex_text[:index]
    index = latex_text.find("\\begin{references}")
    if index:
        latex_text = latex_text[:index]

    title_pattern = r"\\title\s*\{([\s\S]*?)\\"
    title_pattern2 = r"\\title\s*\{([\s\S]*?)\}"

    author_pattern = r"\\author\s*\{([\s\S]*?)\}"
    author_pattern2 = r"\\author\s*\{([\s\S]*?)\\"

    abstract_pattern = r"\\begin\s*\{abstract\}([\s\S]*?)\\end\{abstract\}"
    abstract_pattern2 = r"\s*\wbstract\}([\s\S]*?)(?=(?:\\)|\Z)"
    abstract_pattern3 = r"\\abstract\s*\{([\s\S]*?)\}"
    abstract_pattern4 = (
        r"\\begin\{center\}\s*\{\s*Abstract\s*\}\s*\\end\{center\}\s*([\s\S]*?)\\"
    )

    extracted_content = {}

    # id
    id_pattern = r"(.+)\.gz"
    id_match = re.search(id_pattern, file_name)
    if id_match:
        extracted_content["id"] = id_match.group(1)
    else:
        extracted_content["id"] = ""

    # category
    category_pattern = r"([A-Za-z-]+)\d+\.gz"
    category_match = re.search(category_pattern, file_name)
    if category_match:
        extracted_content["category"] = category_match.group(1)
    else:
        extracted_content["category"] = ""

    # title
    latex_text_tmp = latex_text
    latex_text_tmp = re.sub(r"\\\\", "", latex_text_tmp)
    title_match = re.search(title_pattern, latex_text_tmp)
    title_match2 = re.search(title_pattern2, latex_text_tmp)
    extracted2 = ""
    if title_match:
        extracted = title_match.group(1).strip()
        extracted = re.sub(r"[^A-Za-z\s.,-]", "", extracted)
        extracted_content["title"] = extracted
    elif title_match2:
        extracted2 = title_match2.group(1).strip()
        extracted2 = re.sub(r"[^A-Za-z\s.,-]", "", extracted2)
        extracted_content["title"] = extracted2
    if title_match and title_match2:
        if len(extracted) > len(extracted2):
            extracted_content["title"] = extracted
        else:
            extracted_content["title"] = extracted2
    else:
        extracted_content["title"] = ""

    # author
    author_match = re.search(author_pattern, latex_text)
    author_match2 = re.search(author_pattern2, latex_text)
    if author_match:
        extracted = author_match.group(1).strip()
        extracted = re.sub(r"[^A-Za-z\s.,-]", "", extracted)
        extracted_content["author"] = extracted
    if author_match2:
        extracted2 = author_match2.group(1).strip()
        extracted2 = re.sub(r"[^A-Za-z\s.,-]", "", extracted2)
        extracted_content["author"] = extracted2
    if author_match and author_match2:
        if len(extracted) > len(extracted2):
            extracted_content["author"] = extracted
        else:
            extracted_content["author"] = extracted2
    else:
        extracted_content["author"] = ""

    # abstract
    abstract_match = re.search(abstract_pattern, latex_text, re.DOTALL)
    abstract_match2 = re.search(abstract_pattern2, latex_text, re.DOTALL)
    abstract_match3 = re.search(abstract_pattern3, latex_text, re.DOTALL)
    abstract_match4 = re.search(abstract_pattern4, latex_text, re.DOTALL)
    if abstract_match:
        extracted_content["abstract"] = abstract_match.group(1).strip()
    elif abstract_match2:
        extracted_content["abstract"] = abstract_match2.group(1).strip()
    elif abstract_match3:
        extracted_content["abstract"] = abstract_match3.group(1).strip()
    elif abstract_match4:
        extracted_content["abstract"] = abstract_match4.group(1).strip()
    else:
        extracted_content["abstract"] = ""

    if len(extracted_content["abstract"]) < 10:
        extracted_content["abstract"] = ""

    # section and subsection
    section_pattern = r"\\section\*?\s*\{([\s\S]*?)\}([\s\S]+?)(?=(?:\\section)|\Z)"
    section_matches = re.findall(section_pattern, latex_text, re.DOTALL)
    sections = []
    for section_match in section_matches:
        title = section_match[0].strip()
        if "\\" in title:
            continue
        content = section_match[1].strip()

        content = content.encode("unicode_escape").decode("utf-8", errors="ignore")
        index = content.find("\\x0")
        if index:
            content = content[:index]

        subsections = extract_subsection(content)
        if "subsection" in content:
            content = ""
        sections.append({"title": title, "text": content, "subsection": subsections})

    if sections == []:
        start = latex_text.find("\\end{abstract}")
        if start:
            content = latex_text[start + 14 :]
            sections.append({"title": "", "text": content, "subsection": []})

    extracted_content["section"] = sections

    return extracted_content


def process_file(file_path, dst_path):
    latex_content = ""
    with gzip.open(file_path, "rt", encoding="ISO-8859-1") as f:
        try:
            with tarfile.open(file_path) as sub_tf:
                for member in sub_tf.getmembers():
                    if member.name.endswith(".tex"):
                        if sub_tf.extractfile(member) == None:
                            continue
                        latex = sub_tf.extractfile(member).read()
                        try:
                            latex = latex.decode("utf-8")
                        except UnicodeDecodeError:
                            latex = latex.decode("latin-1", errors="replace")
                        latex_content += latex

        except tarfile.ReadError:
            latex_content = f.read()

        file_name = os.path.basename(file_path)
        parsed_dict = extract_latex_content(latex_content, file_name)

        json_file_path = os.path.splitext(file_path)[0] + ".json"
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(parsed_dict, json_file)

        if os.path.exists(os.path.join(dst_path, os.path.basename(json_file_path))):
            os.remove(os.path.join(dst_path, os.path.basename(json_file_path)))

        shutil.move(json_file_path, dst_path)
        # print(f"Processed: {file_path}")


def tex2json_multiprocess(file_paths, dst_path):
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    start_time = time.time()

    with Pool(cpu_count()) as pool:
        pool.starmap(process_file, [(file_path, dst_path) for file_path in file_paths])

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Processing completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    folder_path = os.getcwd()
    dst_path = os.path.join(folder_path, "all_json")

    file_paths = [
        os.path.join(root, file)
        for root, _, files in os.walk(os.path.join(folder_path, "src"))
        for file in files
        if file.endswith(".gz")
    ]

    tex2json_multiprocess(file_paths, dst_path)

    print("Finish")
