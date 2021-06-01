# Created by Xinyu Zhu on 2021/3/31, 20:41

# Replace * with real note
# sort channel with the Median
# format

import re
import statistics


def reformat(filename: str):
    with open(filename, encoding='utf-8') as f:
        data = f.read()
        content = data.split("\n")
    formatted_content = []
    for line in content:
        if need_reformat(line):
            try:
                line = pre_process(line)
                line = star_remover(line)
                line = sort_channel(line)
            except:
                print(line, " contains wrong format")
                exit(-1)
        formatted_content.append(line)
    return formatted_content


def need_reformat(line: str):
    if len(line) == 0 or "=" in line or "//" in line:
        return False
    return True


def pre_process(line: str):
    new_line = ""
    line = line.strip()
    channels = line.split("|")
    for channel in channels:
        for note in channel.split():
            if len(note) > 0:
                new_line += note.strip() + " "
        new_line = new_line.strip() + "|"
    return new_line.strip("|")


def shift_note(line: str, offset: int, left=True):
    for i in range(1, 8):
        if left:
            line = line.replace(str(i), offset * "." + str(i))
        else:
            line = line.replace(str(i), str(i) + offset * ".")
    notes = line.split()
    for i, note in enumerate(notes):
        nums = note.split("_")
        for j, num in enumerate(nums):
            nums[j] = process_num_with_point(num)
        notes[i] = "_".join(nums)

    return " ".join(notes)


def process_num_with_point(num: str):
    num = num.strip()
    has_half = "#" in num
    num = num.replace("#", "")

    rd = "0"
    for d in num:
        if d != ".":
            rd = d
            break

    if num.startswith(".") and num.endswith("."):
        num_index = -1
        raw_num = "-"
        for i, c in enumerate(num):
            if c != ".":
                num_index = i
                raw_num = c
        prefix_point_num = num_index
        postfix_point_num = len(num) - 1 - prefix_point_num
        diff = prefix_point_num - postfix_point_num
        raw_num = raw_num + "#" if has_half else raw_num
        if diff > 0:
            return "." * diff + raw_num
        elif diff < 0:
            return raw_num + "." * (-diff)
        else:
            return raw_num

    else:
        return num.replace(rd, rd + "#") if has_half else num


def star_remover(line):
    if "*" not in line:
        return line
    new_line = line.split("|")
    for i in range(1, len(new_line)):
        if "*" in new_line[i]:
            new_line[i] = shift_note(new_line[i - 1], new_line[i].count("."), new_line[i].startswith("."))
    return "|".join(new_line)


def sort_channel(line):
    if "|" not in line:
        return line

    line_to_medium = {}
    for l in line.split("|"):
        line_to_medium[l] = extract_medium(l)

    sorted_list = sorted(line_to_medium.items(), key=lambda item: item[1], reverse=True)
    new_line = []
    for item in sorted_list:
        new_line.append(item[0])
    return "\t|\t".join(new_line)


def extract_medium(line: str):
    line = line.replace("#", "")
    numbers = []
    for c in re.split(" |_|\t", line):
        # c = c.strip()
        if c != "0" and c != "-":
            raw_number = int(c.replace(".", ""))
            if c.startswith("."):
                raw_number += 7 * c.count(".")
            else:
                raw_number -= 7 * c.count(".")
            numbers.append(raw_number)
    if len(numbers) == 0:
        return -10000
    return statistics.median(numbers)


def write_to_file(refomatted, filename):
    while len(refomatted[-1]) == 0:
        refomatted.pop(-1)
    with open(filename, encoding='utf-8', mode="w") as f:
        for line in refomatted:
            f.write(line + "\n")


def auto_format_for_file(filename):
    reformatted = reformat(filename)
    write_to_file(reformatted, filename)
