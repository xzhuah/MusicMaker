# Created by Xinyu Zhu on 4/4/2023, 12:30 AM
import os


def read_file(filename: str) -> str:
    with open(filename, encoding='utf-8') as f:
        data = f.read()
    return data


def write_file(filename: str, content: str, create_path_if_not_exist=True):
    if create_path_if_not_exist:
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)
    with open(filename, encoding='utf-8', mode="w") as f:
        f.write(content)
