# Created by Xinyu Zhu on 2020/12/21, 1:31

import pygame.midi
import time
import threading

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
        self.auto_close_duration_index = 2
        self.default_instrument = 0
        # 用于发声的midi模块初始化
        pygame.midi.init()
        self.output = pygame.midi.Output(pygame.midi.get_default_output_id())

        self.ins_to_channel = {
            0: 0
        }
        self.next_channel = 1

    def get_channel_for_instrument(self, instrument):
        if instrument in self.ins_to_channel:
            return self.ins_to_channel[instrument]
        else:
            self.ins_to_channel[instrument] = self.next_channel
            self.next_channel += 1
            if self.next_channel > 15:
                self.next_channel = 1
            return self.ins_to_channel[instrument]

    def auto_play_and_close(self, note, velocity=127, duration=2, channel=0):
        self.output.note_on(note, velocity, channel)
        time.sleep(duration)
        self.output.note_off(note, velocity, channel)

    def play_single_note(self, instrument, note, velocity, duration=-1.0, channel_index=0):
        self.output.set_instrument(instrument, channel_index)
        if duration == -1.0:
            self.output.note_on(note, velocity, channel_index)
        else:
            threading.Thread(target=self.auto_play_and_close,
                             args=(note, velocity, duration, channel_index)).start()

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
        threads = []
        for i, note in enumerate(notes):
            threads.append(
                threading.Thread(target=self.play_note, args=(note,)))
        [thr.start() for thr in threads]
        [thr.join() for thr in threads]

    def play_section(self, list_of_notes: list):
        for notes in list_of_notes:
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

    def parse_section_channel(self, channel_str: str) -> list:
        # 规定在每个channel后面可以用方括号设定该channel的属性(乐器, 响度等)
        local_attr_str = ""

        if "[" in channel_str:
            local_attr_str = channel_str[channel_str.index("[") + 1:channel_str.index("]")]
            channel_str = channel_str[0:channel_str.index("[")]
            channel_str = channel_str.strip()
        attr = self.get_attr_from_str(local_attr_str)
        result = []
        for note_str in channel_str.split():
            note = {
                "ins": attr["ins="],
                "note": self.note_str_to_note(note_str),
                "velocity": attr["vol="]
            }
            result.append(note)
        return result

    def parse_section(self, section_str: str):
        result = []
        for channel in section_str.split("|"):
            result.append(self.parse_section_channel(channel))
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

    def get_attr_from_str(self, attr=""):
        base_attr = {
            "1=": self.base_freq,
            "p=": self.beat,
            "pm=": self.pt,
            "offset=": self.offset,
            "ins=": self.default_instrument,
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
            self.default_instrument = int(attr_unit.replace("ins=", ""))
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
                self.play_section(self.parse_section(line))

    def play_file(self, filename):
        with open(filename, encoding='utf-8') as f:
            data = f.read()
            self.stream_music(data.split("\n"))

    def close(self):
        self.output.close()


if __name__ == '__main__':

    # 编写的简谱文件所在路径, 后缀名随意, 保证格式正确即可
    file_to_play = "./sisterNoise.ply"

    player = MidiPlayer()

    player.play_file(file_to_play)

    player.close()
