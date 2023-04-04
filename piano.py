# Created by Xinyu Zhu on 2022/7/17, 21:38

from pynput.keyboard import Key, Listener
import pygame.midi

import turtle
import threading


# print is not allowed since when java call this file, print statement will break the keyboard listener

def _pre_pre_process_key(key):
    key = str(key).lower()
    key = key.strip()
    if key == "'''":
        return "'"
    else:
        key = key.strip("'")
        if len(key) == 1:
            return key
        else:
            return key


class Piano:
    def __init__(self):
        # use these key to represent 1234567 do la mi fa suo la xi, from low to high, loop by 7
        self._music_keys = "zxcvm,.asdfjklqweruio1234789"
        self._music_keys_table = {}
        for i, key in enumerate(self._music_keys):
            self._music_keys_table[key] = i

        # when read these keys, transform them to the original key
        self._key_transform = {
            "<": ",",
            ">": ".",
            "!": "1",
            "@": "2",
            "#": "3",
            "$": "4",
            "&": "7",
            "*": "8",
            "(": "9"
        }

        self._base = [0, 2, 4, 5, 7, 9, 11]
        self._special_base = {4, 9, 10, 11}
        self._loop_size = 12

        self.off_set = 4

        self.shift = False

        self.selected_instrument = [0, 8, 9, 10, 11, 24, 32, 34, 44, 46, 48, 49, 50, 51, 53, 54, 72, 73, 75, 77, 88, 89,
                                    92, 93, 95, 98, 99]
        self.instrument_pointer = 0

        # circle of five
        self.circle_position = 0
        self._circle_five = {
            -12: "Cm",
            -1: '#Cm',
            -2: 'Dm',
            -3: "bEm",
            -4: "Em",
            -5: "Fm",
            -6: "#Fm",
            -7: "Gm",
            -8: "#Gm",
            -9: "Am",
            -10: "bBm",
            -11: "Bm",

            0: "C",
            1: "Db, C#",
            2: "D",
            3: "Eb",
            4: "E",
            5: "F",
            6: "Gb, F#",
            7: "G",
            8: "Ab",
            9: "A",
            10: "Bb",
            11: "B, Cb"

        }

        self.instrument = 0
        self._list_of_instrument = ["Acoustic Grand Piano 大钢琴（声学钢琴）", "Bright Acoustic Piano 明亮的钢琴",
                                    "Electric Grand Piano 电钢琴",
                                    "Honky-tonk Piano 酒吧钢琴", "Rhodes Piano 柔和的电钢琴", "Chorused Piano 加合唱效果的电钢琴",
                                    "Harpsichord 羽管键琴（拨弦古钢琴）", "Clavichord 科拉维科特琴（击弦古钢琴）", "Celesta 钢片琴",
                                    "Glockenspiel 钟琴",
                                    "Music box 八音盒", "Vibraphone 颤音琴", "Marimba 马林巴", "Xylophone 木琴",
                                    "Tubular Bells 管钟",
                                    "Dulcimer 大扬琴", "Hammond Organ 击杆风琴", "Percussive Organ 打击式风琴", "Rock Organ 摇滚风琴",
                                    "Church Organ 教堂风琴", "Reed Organ 簧管风琴", "Accordian 手风琴", "Harmonica 口琴",
                                    "Tango Accordian 探戈手风琴",
                                    "Acoustic Guitar (nylon) 尼龙弦吉他", "Acoustic Guitar (steel) 钢弦吉他",
                                    "Electric Guitar (jazz) 爵士电吉他",
                                    "Electric Guitar (clean) 清音电吉他", "Electric Guitar (muted) 闷音电吉他",
                                    "Overdriven Guitar 加驱动效果的电吉他",
                                    "Distortion Guitar 加失真效果的电吉他", "Guitar Harmonics 吉他和音", "Acoustic Bass 大贝司（声学贝司）",
                                    "Electric Bass(finger) 电贝司（指弹）", "Electric Bass (pick) 电贝司（拨片）",
                                    "Fretless Bass 无品贝司",
                                    "Slap Bass 掌击Bass 1", "Slap Bass 掌击Bass 2", "Synth Bass 电子合成Bass 1",
                                    "Synth Bass 电子合成Bass 2",
                                    "Violin 小提琴", "Viola 中提琴", "Cello 大提琴", "Contrabass 低音大提琴",
                                    "Tremolo Strings 弦乐群颤音音色",
                                    "Pizzicato Strings 弦乐群拨弦音色", "Orchestral Harp 竖琴", "Timpani 定音鼓",
                                    "String Ensemble 弦乐合奏音色1",
                                    "String Ensemble 弦乐合奏音色2", "Synth Strings 合成弦乐合奏音色1", "Synth Strings 合成弦乐合奏音色2",
                                    "Choir Aahs 人声合唱“啊”", "Voice Oohs 人声“嘟”", "Synth Voice 合成人声",
                                    "Orchestra Hit 管弦乐敲击齐奏",
                                    "Trumpet 小号", "Trombone 长号", "Tuba 大号", "Muted Trumpet 加弱音器小号",
                                    "French Horn 法国号（圆号）",
                                    "Brass Section 铜管组（铜管乐器合奏音色）", "Synth Brass 合成铜管音色1", "Synth Brass 合成铜管音色2",
                                    "Soprano Sax 高音萨克斯风",
                                    "Alto Sax 次中音萨克斯风", "Tenor Sax 中音萨克斯风", "Baritone Sax 低音萨克斯风", "Oboe 双簧管",
                                    "English Horn 英国管",
                                    "Bassoon 巴松（大管）", "Clarinet 单簧管（黑管）", "Piccolo 短笛", "Flute 长笛", "Recorder 竖笛",
                                    "Pan Flute 排箫",
                                    "Bottle Blow 吹瓶声", "Shakuhachi 日本尺八", "Whistle 口哨声", "Ocarina 奥卡雷那",
                                    "Lead (square) 合成主音1（方波）",
                                    "Lead (sawtooth) 合成主音2（锯齿波）", "Lead (caliope lead)合成主音3", "Lead (chiff lead) 合成主音4",
                                    "Lead (charang) 合成主音5", "Lead (voice) 合成主音6（人声）", "Lead (fifths) 合成主音7（平行五度）",
                                    "Lead (bass+lead) 合成主音8（贝司加主音）", "Pad (new age) 合成音色1（新世纪）", "Pad (warm) 合成音色（温暖）",
                                    "Pad (polysynth) 合成音色3", "Pad (choir) 合成音色（合唱）", "Pad (bowed) 合成音色5",
                                    "Pad (metallic) 合成音色（金属声）",
                                    "Pad (halo) 合成音色（光环）", "Pad (sweep) 合成音色8", "FX (rain) 合成效果 雨声",
                                    "FX (soundtrack) 合成效果 音轨",
                                    "FX (crystal) 合成效果 水晶", "FX (atmosphere) 合成效果 大气", "FX (brightness) 合成效果 明亮",
                                    "FX (goblins) 合成效果 鬼怪", "FX (echoes) 合成效果 回声", "FX (sci-fi) 合成效果 科幻",
                                    "Sitar 西塔尔（印度）",
                                    "Banjo 班卓琴（美洲）", "Shamisen 三昧线（日本）", "Koto 十三弦筝（日本）", "Kalimba 卡林巴", "Bagpipe 风笛",
                                    "Fiddle 民族提琴",
                                    "Shanai 山奈", "Tinkle Bell 叮当铃", "Agogo 摇摆舞铃", "Steel Drums 钢鼓", "Woodblock 木鱼",
                                    "Taiko Drum 太鼓",
                                    "Melodic Tom 通通鼓", "Synth Drum 合成鼓", "Reverse Cymbal 铜钹",
                                    "Guitar Fret Noise 吉他换把杂音",
                                    "Breath Noise 呼吸声", "Seashore 海浪声", "Bird Tweet 鸟鸣", "Telephone Ring 电话铃",
                                    "Helicopter 直升机",
                                    "Applause 鼓掌声", "Gunshot 枪击声"]

        pygame.midi.init()
        self.output = pygame.midi.Output(pygame.midi.get_default_output_id())
        self.output.set_instrument(self.instrument)

    def __str__(self):
        return "Instrument:{0}, Circle:{1}, Offset:{2}".format(self._list_of_instrument[self.instrument],
                                                               self._circle_five[self.circle_position],
                                                               self.off_set)

    def shift_change(self):
        self.shift = not self.shift

    def increase_circle_position(self):
        if self.circle_position >= 11:
            self.circle_position = 11
        else:
            self.circle_position = self.circle_position + 1

    def decrease_circle_position(self):
        if self.circle_position <= -12:
            self.circle_position = -12
        else:
            self.circle_position = self.circle_position - 1

    def set_instrument(self, instrument_number):
        if instrument_number >= 0:
            instrument_number = instrument_number % len(self._list_of_instrument)
            pygame.midi.init()
            self.output.set_instrument(instrument_number)
            self.instrument = instrument_number

    def simple_set_instrument(self):
        self.instrument_pointer += 1
        if self.instrument_pointer >= len(self.selected_instrument):
            self.instrument_pointer = 0
        self.instrument = self.selected_instrument[self.instrument_pointer]
        self.set_instrument(self.instrument)

        # self.set_instrument(self.instrument + 1)

    def set_off_set(self, offset):
        if offset < 0:
            self.off_set = 0
        elif offset >= 8:
            self.off_set = 7
        else:
            self.off_set = offset

    def increase_offset(self):
        self.set_off_set(self.off_set + 1)

    def decrease_offset(self):
        self.set_off_set(self.off_set - 1)

    def _key_base(self, key):
        if key in self._key_transform:
            key = self._key_transform[key]

        if key in self._music_keys_table:
            base = self._music_keys_table[key]
            remainder = base % len(self._base)
            result = base // len(self._base)
            return self._base[remainder] + result * self._loop_size
        else:
            return None

    def _key_shift(self, key_base):
        if self.shift:
            return key_base + 1
        else:
            return key_base

    def _key_offset(self, key_shifted):
        return self.off_set * self._loop_size + key_shifted

    def _key_to_code(self, key_shifted):
        if self.circle_position >= 0:
            return key_shifted + self.circle_position
        else:
            real_key = key_shifted % self._loop_size
            key_shifted += abs(self.circle_position)
            if real_key in self._special_base:
                key_shifted -= 1
            return key_shifted

    def key_to_code(self, key):
        # this function convert a pressed button to the correct code that should be played
        base = self._key_base(key)
        if base is None:
            return None
        shifted = self._key_shift(base)
        offset_key = self._key_offset(shifted)
        code = self._key_to_code(offset_key)
        return code

    def play_node(self, node, velocity=127):
        self.output.note_on(node, velocity)

    def stop_node(self, node):

        self.output.note_off(node)


class PianoEffector:
    def __init__(self, piano):
        assert isinstance(piano, Piano)
        self.piano = piano
        self.press_effectors = []
        self.release_effectors = []

        self.press_effectors.append(self.normal_play)
        self.release_effectors.append(self.normal_end)

        self.press_effectors.append(self.chord_effect)
        self.release_effectors.append(self.chord_effect_release)

        self.shift_pressed = False
        self.sustaining_mode = True

        self.key_status = {}
        self.key_status_for_chord_effect = {}

        # all sound lower than self.low_sound_filter will decrease velocity
        # by a ratio of self.low_sound_velocity
        self.low_sound_filter = 0
        self.low_sound_velocity = 0.8

        self.chord_mode = 0  # 0 无 1:大3 2:小3 3:减3 4:增3
        self.chord_name = {
            0: "无和弦",
            1: "减一度和弦",
            2: "减二度和弦",
            3: "大三和弦",
            4: "小三和弦",
            5: "减三和弦",
            6: "增三和弦"
        }

        # self.music_buffer = []
        # self.record_start = 0

    def __str__(self):
        return self.piano.__str__() + "\n" + "sustaining:{0}, chord_mode:{1}, low_sound_filter:{2}, low_sound_velocity:{3}".format(
            self.sustaining_mode, self.chord_name[self.chord_mode],
            self.piano._music_keys[self.low_sound_filter * len(self.piano._base)], self.low_sound_velocity)

    def handle_func_key_press(self, key):

        if "key.shift" in key and not self.shift_pressed:
            self.shift_pressed = True
            self.piano.shift_change()

    def handle_func_key_release(self, key):
        if key == '[':
            self.piano.decrease_offset()
        elif key == ']':
            self.piano.increase_offset()
        elif key == '{':
            self.piano.decrease_circle_position()
        elif key == "}":
            self.piano.increase_circle_position()
        elif key == "`":
            self.piano.simple_set_instrument()
        elif key == "key.space":
            self.piano.set_instrument(0)
        elif key == "\\\\":
            self.sustaining_mode = not self.sustaining_mode
        elif key == "key.left":
            # decrease low sound bar
            if self.low_sound_filter > 0:
                self.low_sound_filter -= 1
        elif key == "key.right":
            # increase low sound bar
            if self.low_sound_filter < len(self.piano._music_keys) // len(self.piano._base) - 1:
                self.low_sound_filter += 1
        elif key == "key.down":
            # decrease low sound velocity
            if self.low_sound_velocity > 0:
                self.low_sound_velocity -= 0.05
        elif key == "key.up":
            # increase low sound velocity
            if self.low_sound_velocity < 1:
                self.low_sound_velocity += 0.05
        elif key == "-" or key == "_":
            if self.chord_mode > 0:
                self.chord_mode -= 1
        elif key == "+" or key == "=":
            self.chord_mode += 1
            if self.chord_mode >= len(self.chord_name):
                self.chord_mode -= 1

        elif "key.shift" in key:
            self.shift_pressed = False
            self.piano.shift_change()
            return
        elif "key.caps_lock" in key:
            self.piano.shift_change()
        else:
            return

        try:
            my_turtle.clear()
            my_turtle.penup()
            my_turtle.goto(-200, 0)
            my_turtle.pendown()
            my_turtle.write(str(self))
        except:
            exit(0)

    def handle_key_press(self, key):
        # origin_key = key

        key = _pre_pre_process_key(key)
        code = self.piano.key_to_code(key)

        if code is None:
            self.handle_func_key_press(key)
        else:
            for effector in self.press_effectors:
                effector(code, key)

    def handle_key_release(self, key):

        # origin_key = key
        key = _pre_pre_process_key(key)
        code = self.piano.key_to_code(key)
        if code is None:
            self.handle_func_key_release(key)
        else:
            for effector in self.release_effectors:
                effector(code, key)

    def _filter_low_sound(self, code):
        if code < self.piano.key_to_code(self.piano._music_keys[self.low_sound_filter * len(self.piano._base)]):
            return int(127 * self.low_sound_velocity)
        else:
            return 127

    # for sound playing
    def normal_play(self, code, key):
        key = key.lower()
        if key in self.piano._key_transform:
            key = self.piano._key_transform[key]
        if key not in self.key_status or not self.key_status[key]:
            self.key_status[key] = True
            self.piano.play_node(code, velocity=self._filter_low_sound(code))

    def normal_end(self, code, key):
        key = key.lower()
        if key in self.piano._key_transform:
            key = self.piano._key_transform[key]
        if not self.sustaining_mode or self.piano.instrument > 15:
            try:
                self.piano.stop_node(code)
            except:
                pass
        self.key_status[key] = False

    def _chord_generator(self, node):
        if self.chord_mode == 0:
            return []
        elif self.chord_mode == 1:
            return [node - 12]

        elif self.chord_mode == 2:
            return [node - 12, node - 24]

        elif self.chord_mode == 3:
            return [node - 3, node - 7]

        elif self.chord_mode == 4:
            return [node - 4, node - 8]

        elif self.chord_mode == 5:
            return [node - 3, node - 6]

        elif self.chord_mode == 6:
            return [node - 4, node - 8]

        else:
            return []

    def chord_effect(self, code, key):
        if key not in self.key_status_for_chord_effect or not self.key_status_for_chord_effect[key]:
            self.key_status_for_chord_effect[key] = True
            to_play = self._chord_generator(code)
            for c in to_play:
                self.piano.play_node(c, velocity=self._filter_low_sound(code))

    def chord_effect_release(self, code, key):
        to_play = self._chord_generator(code)
        if not self.sustaining_mode or self.piano.instrument > 15:
            for c in to_play:
                try:
                    self.piano.stop_node(c)
                except:
                    pass
        self.key_status_for_chord_effect[key] = False


playing = True

my_effector = PianoEffector(Piano())


def on_press(key):
    global playing
    if playing:
        my_effector.handle_key_press(key)


def on_release(key):
    global playing
    if key == Key.esc:
        playing = not playing
    if playing:
        my_effector.handle_key_release(key)


def maintain_piano():
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()


if __name__ == '__main__':
    wn = turtle.Screen()
    wn.setup(1000, 80, 850, 900)
    wn.title("Piano")
    my_turtle = turtle.Turtle()

    t = threading.Thread(target=maintain_piano)
    t.start()

    wn.listen()
    wn.mainloop()

    turtle.done()