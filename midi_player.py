# Created by Xinyu Zhu on 2020/12/23, 23:16
import pygame.midi
import time
import os
from ply_standardlizer import auto_format_for_file
from utils import read_file
from concurrent.futures import ThreadPoolExecutor

_thread_pool = None


def get_singleton_thread_pool() -> ThreadPoolExecutor:
    global _thread_pool
    if _thread_pool is None:
        _thread_pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="singleton_thread_pool")
    return _thread_pool


class MidiPlayer:
    def __init__(self):
        # 对于简谱上的一个数, 实际的声调应该在基础音阶的基础上增加多少
        self.unit_offset = {
            "1": 0,
            "2": 2,
            "3": 4,
            "4": 5,
            "5": 7,
            "6": 9,
            "7": 11
        }

        # 播放器所使用的初始基础音阶, 60为midi对于C大调的1(哆)
        self.base_freq = 60
        self.offset = 0

        # 根据简谱的调性, 播放器所使用的的基础音阶应该在初始基础音阶的基础上增加多少
        self.key_offset = {
            "C": 0,
            "Db": 1,
            "C#": 1,
            "D": 2,
            "Eb": 3,
            "E": 4,
            "F": 5,
            "Gb": 6,
            "F#": 6,
            "G": 7,
            "Ab": 8,
            "A": 9,
            "Bb": 10,
            "B": 11,
            "Cb": 11
        }

        # 每拍时间长度(s)
        self.pt = 0.66
        self.default_velocity = 127

        # 4/4 拍, 主要影响每拍的强弱
        self.beat = "4/4"
        # 一般音乐本身有设计好拍子的感觉, 不需要刻意调强弱, 响度设置成一样的感觉比较好
        self.strong_beat = 127
        self.less_strong_beat = 127
        self.weak_beat = 127

        self.auto_close_instrument = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 47, 112, 113, 114, 115, 116,
                                      117, 118, 119, 127, 45}
        # 对于无法自动停止的乐器, 在n个节拍后强制停止
        self.auto_close_duration_index = 1
        self.default_instrument = [0]
        # 用于发声的midi模块初始化
        self.output = get_singleton_midi_output()

        self.ins_to_channel = {
            0: 0
        }
        self.next_channel = 1
        # self.data_manager = MusicDataManager()

        # 是否固定使用默认乐器而不根据乐谱调整
        self.force_instrument = False
        self.force_to = 0

        self.threading_pool = get_singleton_thread_pool()

    def choose_from_default_instrument(self, channel_index):
        index = int(channel_index * len(self.default_instrument))
        # print(channel_index, self.default_instrument, index)
        return self.default_instrument[index]

    def get_channel_for_instrument(self, instrument):
        return 0
        # if instrument in self.ins_to_channel:
        #     return self.ins_to_channel[instrument]
        # else:
        #     self.ins_to_channel[instrument] = self.next_channel
        #     self.next_channel += 1
        #     if self.next_channel > 15:
        #         self.next_channel = 1
        #     return self.ins_to_channel[instrument]

    def auto_play_and_close(self, note, velocity=127, duration=2, channel=0):
        self.output.note_on(note, velocity, channel)
        time.sleep(duration)
        self.output.note_off(note, velocity, channel)

    def play_single_note(self, instrument, note, velocity, duration=-1.0, channel_index=0):
        self.output.set_instrument(instrument, channel_index)
        if duration == -1.0:
            self.output.note_on(note, velocity, channel_index)
        else:
            self.threading_pool.submit(self.auto_play_and_close, note, velocity, duration, channel_index)
            # threading.Thread(target=self.auto_play_and_close,
            #                  args=(note, velocity, duration, channel_index)).start()

    def play_note(self, note):
        for note_number in note["note"]:
            if note_number > 0:
                if note["ins"] in self.auto_close_instrument:
                    self.play_single_note(note["ins"], note_number, note["velocity"], -1.0,
                                          self.get_channel_for_instrument(note["ins"]))
                else:
                    self.play_single_note(note["ins"], note_number, note["velocity"],
                                          self.pt * self.auto_close_duration_index,
                                          self.get_channel_for_instrument(note["ins"]))
            time.sleep(self.pt / len(note["note"]))

    def play_chord(self, notes):
        list(self.threading_pool.map(self.play_note, notes))

    def play_section(self, list_of_notes: list):
        for notes in list_of_notes:
            # print(notes)
            self.play_chord(notes)

    def single_note_to_num(self, single_note: str):
        """
            将简谱中的单个音阶装换为实际频率代码
            支持的规则: 1: 普通的音阶, 1#: 升半调, .1: 升7度, 1..: 降两个7度, 1..#或者1#..: 降两个7度后升半调
            .1.: 会被解析为升两个7度, .1##.: 会忽略重复的#, 被解析为..1#
            不支持: .8.: 不在1~7的范围内, 返回-1, 不会播放, @1: 含有不合法字符, 返回-1 不会播放
        """

        # 以.开头视为需要升若干个7度, 否则需要降
        should_increase_7 = (single_note[0] == ".")

        # 具体升降多少个7度看.的个数
        cycle_should_change = single_note.count(".")

        # 去除.和#之后的字符视为要播放的音阶
        unit_key = single_note.replace(".", "").replace("#", "")

        if unit_key in self.unit_offset:
            unit_key_freq = self.base_freq + self.unit_offset[unit_key] + self.offset * 12
        elif unit_key == '0':
            return 0
        else:
            return -1

        if "#" in single_note:
            unit_key_freq += 1

        if should_increase_7:
            unit_key_freq += cycle_should_change * 12
        else:
            unit_key_freq -= cycle_should_change * 12
        return unit_key_freq

    def note_str_to_note(self, note_str: str) -> list:
        """
           将类似 1_2. 这种有联系的多个音符转成一个数组, 每个数组中全部音阶播放的完的时间会相同, 也就是一个拍的时间
           多个拍组成一个音轨的一个小节(segment), 4/4拍的音乐中, 4拍为一节

           多个音轨组成的一个小节, 我们叫做一节(section), 也就是我们编写音乐中的一行, 播放时一节一节地解析播放

           单个音节也能形成一个长度为1的数组
       """
        result = []
        for single_unit in note_str.split("_"):
            result.append(self.single_note_to_num(single_unit))
        return result

    def parse_section_channel(self, channel_str: str, channel_index: float) -> list:
        # 规定在每个channel后面可以用方括号设定该channel的属性(乐器, 响度等)
        local_attr_str = ""

        if "[" in channel_str:
            local_attr_str = channel_str[channel_str.index("[") + 1:channel_str.index("]")]
            channel_str = channel_str[0:channel_str.index("[")]
            channel_str = channel_str.strip()
        attr = self.get_attr_from_str(local_attr_str, channel_index)
        result = []
        for note_str in channel_str.split():
            note = {
                "ins": self.force_to if self.force_instrument else attr["ins="],
                "note": self.note_str_to_note(note_str),
                "velocity": attr["vol="]
            }
            result.append(note)
        return result

    def parse_repeated_channel(self, channel, last_channel, channel_index: float):
        channel = channel.strip()
        should_increase_note = 1 if channel.startswith(".") else -1
        increase_count = channel.count(".")
        this_channel = []

        for channel_note in last_channel:
            base_notes = channel_note["note"]
            new_notes = []
            for note in base_notes:
                if note > 0:
                    new_notes.append(note + increase_count * 12 * should_increase_note)
                else:
                    new_notes.append(note)
            this_channel_node = {
                "ins": self.force_to if self.force_instrument else channel_note["ins"],
                "note": new_notes,
                "velocity": channel_note["velocity"]
            }
            this_channel.append(this_channel_node)
        return this_channel

    def parse_section(self, section_str: str):
        result = []
        total_channel_num = section_str.count("|") + 1
        for i, channel in enumerate(section_str.split("|")):
            if "*" in channel:
                result.append(self.parse_repeated_channel(channel, result[-1], i / total_channel_num))
            else:
                result.append(self.parse_section_channel(channel, i / total_channel_num))
        re_arranged_result = []
        for i in range(len(result[0])):
            buffer = []
            for j in range(len(result)):
                if i >= len(result[j]):
                    print("Error in channel length:", section_str)
                    print(section_str.split("|")[j])
                buffer.append(result[j][i])
            re_arranged_result.append(buffer)
        return re_arranged_result

    def get_attr_from_str(self, attr="", channel_index=0):
        base_attr = {
            "1=": self.base_freq,
            "p=": self.beat,
            "pm=": self.pt,
            "offset=": self.offset,
            "ins=": self.choose_from_default_instrument(channel_index),
            "vol=": self.default_velocity
        }
        attrs = attr.split(",")
        for attr_unit in attrs:
            attr_unit = attr_unit.replace(" ", "")
            if "1=" in attr_unit:
                key = attr_unit.replace("1=", "").strip()
                base_attr["1="] = 60 + self.key_offset[key]
            elif "p=" in attr_unit:
                base_attr["p="] = attr_unit.replace("p=", "").strip()
            elif "pm=" in attr_unit:
                base_attr["pm="] = 60 / int(attr_unit.replace("pm=", ""))
            elif "offset=" in attr_unit:
                base_attr["offset="] = int(attr_unit.replace("offset=", ""))
            elif "ins=" in attr_unit:
                base_attr["ins="] = int(attr_unit.replace("ins=", ""))
            elif "vol=" in attr_unit:
                base_attr["vol="] = int(attr_unit.replace("vol=", ""))
        return base_attr

    def set_attr(self, attr: str):
        attrs = attr.split(",")
        for attr_unit in attrs:
            self.set_attr_unit(attr_unit)

    def set_attr_unit(self, attr_unit: str):
        attr_unit = attr_unit.replace(" ", "")
        if "1=" in attr_unit:
            key = attr_unit.replace("1=", "").strip()
            self.base_freq = 60 + self.key_offset[key]
        elif "p=" in attr_unit:
            self.beat = attr_unit.replace("p=", "").strip()
        elif "pm=" in attr_unit:
            self.pt = 60 / int(attr_unit.replace("pm=", ""))
        elif "offset=" in attr_unit:
            self.offset = int(attr_unit.replace("offset=", ""))
        elif "ins=" in attr_unit:
            ins_content = attr_unit.replace("ins=", "")
            # support things like: ins = (1|2|3)
            if "(" not in ins_content:
                self.default_instrument = [int(ins_content)]
            else:
                ins_content = ins_content.replace("(", "").replace(")", "")
                self.default_instrument = []
                for ins in ins_content.split("|"):
                    self.default_instrument.append(int(ins))
        elif "vol=" in attr_unit:
            self.default_velocity = int(attr_unit.replace("vol=", ""))

    def stream_music(self, music_sheet: list):
        play = True
        for line in music_sheet:
            if "//" in line:
                # 跳过注释
                continue
            if "<" in line:
                # 跳过播放
                play = False
                continue
            if ">" in line:
                # 开始播放
                play = True
                continue
            if "=" in line and "[" not in line:
                # 设置全局属性
                self.set_attr(line)
                continue
            if play and line != "":
                print(line)
                self.play_section(self.parse_section(line))

    # an helper function for midi_io
    def parse_music_line(self, music_sheet: list):
        play = True
        for line in music_sheet:
            if "//" in line:
                # 跳过注释
                continue
            if "<" in line:
                # 跳过播放
                play = False
                continue
            if ">" in line:
                # 开始播放
                play = True
                continue
            if "=" in line and "[" not in line:
                # 设置全局属性
                self.set_attr(line)
                continue
            if play and line != "":
                yield self.parse_section(line), line

    def compile_music(self, music_sheet: list):
        # self.data_manager.init()
        for line in music_sheet:
            if "//" in line or "<" in line or ">" in line:
                # 跳过注释
                continue
            if "=" in line and "[" not in line:
                # 设置全局属性
                self.set_attr(line)
                continue
        #     if line != "":
        #         self.data_manager.parse_music(self.parse_section(line), self.pt, self.base_freq)
        # self.data_manager.output_current()

    def play_file(self, filename):
        auto_format_for_file(filename)
        data = read_file(filename)

        self.compile_music(data.split("\n"))
        self.stream_music(data.split("\n"))

    def close(self):
        self.output.close()


midi_output = None


def get_singleton_midi_output():
    global midi_output
    if midi_output is None:
        pygame.midi.init()
        midi_output = pygame.midi.Output(pygame.midi.get_default_output_id())
    return midi_output


if __name__ == '__main__':
    player = MidiPlayer()
    # player.force_instrument = True
    # player.play_file("test.ply")
    player.play_file("ply/railgun_piano.ply")
    player.play_file("ply/tonight.ply")
    player.play_file("ply/ningchi.ply")
    player.play_file("ply/yehangxin_single.ply")
    player.play_file("ply/spectre.ply")
    player.play_file("ply/qifengle.ply")
    player.play_file("ply/yuxitan.ply")
    player.play_file("ply/klodia.ply")
    player.play_file("ply/lightofhumanity.ply")

    # player.play_file("ningchi.ply")
    player.play_file("ply/astronomia.ply")
    player.play_file("ply/railgun_piano.ply")
    player.play_file("ply/level5.ply")

    player.play_file("ply/qihung_end.ply")
    player.play_file("ply/qihung_end2.ply")
    player.play_file("ply/faded.ply")
    player.play_file("ply/myHeartWillGoOn.ply")
    player.play_file("ply/qianbenying.ply")
    player.play_file("ply/one_punch.ply")
    player.play_file("ply/nextToYou.ply")
    player.play_file("ply/tail.ply")
    player.play_file("ply/bird.ply")
    player.play_file("ply/sisterNoise.ply")
    player.play_file("ply/tanzilang.ply")
    player.play_file("ply/railgun.ply")
    player.play_file("ply/canon_1.ply")
    player.play_file("ply/west.ply")
    player.play_file("ply/xiaozhiqu.ply")

    # player.play_section(player.parse_section(
    #     "0 0 ..2 0 | 0_.6 ..1_..3 .5 0_-_..1_.7|..1_6 .1_.3 .2 0_-_.1_.7|0_-_6.._3. 1_3._1._6.. 0_-_4.._1. 6._1._6.._4..[ins=99]"))
    player.close()
