Demo: https://www.bilibili.com/video/bv1A54y1t7pC

# 如何运行

确保你的设备有支持midi的发音设备,一般的windows电脑自带

需要安装pygame模块用来合成声音, [更多关于这个库的信息](https://www.pygame.org/docs/ref/midi.html)

```pip install -r requirements.txt```

直接运行, 可播放内置音乐, 简谱文件见同目录下

```python midi_player.py```

运行键盘钢琴, 可在键盘上弹奏

```python piano.py```

如果要播放其他简谱文件, 修改代码中的文件目录即可, 后缀不一定要ply, 随意即可, 只需保证文件格式正确

# 简谱文件支持的属性
1. 可以任意设置简谱的调性, 如1=Ab, 表示使用降A大调
2. 可以设置时频, 如pm=90, 表示每分钟90拍
3. 可以设置升/降多少个7度, 比如offset=-1, 表示降1个7度
4. 可以设置播放的乐器, 比如ins=99, 使用midi的编号99的乐器
你可以在文件任意位置插入以上命令, 命令后面的音乐属性会随之更改

# 如何编写你自己的简谱文件

需要具备一定的乐理知识, 懂得节拍和音调, 会看简谱
## 规则举例
### 单个音符的表示
\.1#: 表示简谱中的升一个7度的1# (有时候简谱是把#卸载前面#1表示升半调, 但我们必须写在数字后面) <br>
1#\..: 表示降两个7度的的1#, \. 的数量表示几个7度, 在前面表示升, 后面表示降<br>
\- 或者 0: 简谱中的0表示停顿音, \-表示延续音, 但是在我们的简谱中它们都表示延续音, 事实上,我们的简谱暂时不支持停顿音, 每一个音会自动慢慢减弱, 对于一般的听众可能不会有太大影响, 在写简谱时, 可以用0或者
\-填充空白位置, 或者补齐简谱中的多分音符<br>

### 多分音符
1_2: 表示二分音符(一条下划线)
1_2_2_3: 是一个四分音符(两条下划线)
1_0_2_3: 是一个复合音符, 实际在简谱中只有3个数字:123, 其中1下面只有1条下划线, 23下面有两条, 注意不能写成1_2_3, 必须用0或者\-补充完整

### 小节
简谱文件中每一行是一个小节, 以4/4拍的音乐为例子
```
..3_0_0_..3 0_.7 .7 0 
.4 .6_0_.5_.6 0_..4 ..3_..2
```
表示两个小节, 也就是简谱中以|分割的连续两部分, 上面例子中, 每个小节有4个多分音符, 用空格隔开, 每个音符的播放时间长度是一样的, 由时频(pm)决定, 即60/pm秒
不同小节的长度不需要保持相同

### 多音轨
一个小节(一行)可以包含多个音轨, 用|分开
```
.1 .1_0_7_.1 0_.2. .3_.4    | ..1 0 0 0 
```
一个小节中的每个音轨必须保证长度相同, 如果不同,需要用0或者\-补到相同, 这些音轨会同时播放形成复音效果


# 乐器代号表
0 :  Acoustic Grand Piano 大钢琴（声学钢琴） <br>
1 :  Bright Acoustic Piano 明亮的钢琴 <br>
2 :  Electric Grand Piano 电钢琴 <br>
3 :  Honky-tonk Piano 酒吧钢琴 <br>
4 :  Rhodes Piano 柔和的电钢琴 <br>
5 :  Chorused Piano 加合唱效果的电钢琴 <br>
6 :  Harpsichord 羽管键琴（拨弦古钢琴） <br>
7 :  Clavichord 科拉维科特琴（击弦古钢琴） <br>
8 :  Celesta 钢片琴 <br>
9 :  Glockenspiel 钟琴 <br>
10 :  Music box 八音盒 <br>
11 :  Vibraphone 颤音琴 <br>
12 :  Marimba 马林巴 <br>
13 :  Xylophone 木琴 <br>
14 :  Tubular Bells 管钟 <br>
15 :  Dulcimer 大扬琴 <br>
16 :  Hammond Organ 击杆风琴 <br>
17 :  Percussive Organ 打击式风琴 <br>
18 :  Rock Organ 摇滚风琴 <br>
19 :  Church Organ 教堂风琴 <br>
20 :  Reed Organ 簧管风琴 <br>
21 :  Accordian 手风琴 <br>
22 :  Harmonica 口琴 <br>
23 :  Tango Accordian 探戈手风琴 <br>
24 :  Acoustic Guitar (nylon) 尼龙弦吉他 <br>
25 :  Acoustic Guitar (steel) 钢弦吉他 <br>
26 :  Electric Guitar (jazz) 爵士电吉他 <br>
27 :  Electric Guitar (clean) 清音电吉他 <br>
28 :  Electric Guitar (muted) 闷音电吉他 <br>
29 :  Overdriven Guitar 加驱动效果的电吉他 <br>
30 :  Distortion Guitar 加失真效果的电吉他 <br>
31 :  Guitar Harmonics 吉他和音 <br>
32 :  Acoustic Bass 大贝司（声学贝司） <br>
33 :  Electric Bass(finger) 电贝司（指弹） <br>
34 :  Electric Bass (pick) 电贝司（拨片） <br>
35 :  Fretless Bass 无品贝司 <br>
36 :  Slap Bass 掌击Bass 1 <br>
37 :  Slap Bass 掌击Bass 2 <br>
38 :  Synth Bass 电子合成Bass 1 <br>
39 :  Synth Bass 电子合成Bass 2 <br>
40 :  Violin 小提琴 <br>
41 :  Viola 中提琴 <br>
42 :  Cello 大提琴 <br>
43 :  Contrabass 低音大提琴 <br>
44 :  Tremolo Strings 弦乐群颤音音色 <br>
45 :  Pizzicato Strings 弦乐群拨弦音色 <br>
46 :  Orchestral Harp 竖琴 <br>
47 :  Timpani 定音鼓 <br>
48 :  String Ensemble 弦乐合奏音色1 <br>
49 :  String Ensemble 弦乐合奏音色2 <br>
50 :  Synth Strings 合成弦乐合奏音色1 <br>
51 :  Synth Strings 合成弦乐合奏音色2 <br>
52 :  Choir Aahs 人声合唱“啊” <br>
53 :  Voice Oohs 人声“嘟” <br>
54 :  Synth Voice 合成人声 <br>
55 :  Orchestra Hit 管弦乐敲击齐奏 <br>
56 :  Trumpet 小号 <br>
57 :  Trombone 长号 <br>
58 :  Tuba 大号 <br>
59 :  Muted Trumpet 加弱音器小号 <br>
60 :  French Horn 法国号（圆号） <br>
61 :  Brass Section 铜管组（铜管乐器合奏音色） <br>
62 :  Synth Brass 合成铜管音色1 <br>
63 :  Synth Brass 合成铜管音色2 <br>
64 :  Soprano Sax 高音萨克斯风 <br>
65 :  Alto Sax 次中音萨克斯风 <br>
66 :  Tenor Sax 中音萨克斯风 <br>
67 :  Baritone Sax 低音萨克斯风 <br>
68 :  Oboe 双簧管 <br>
69 :  English Horn 英国管 <br>
70 :  Bassoon 巴松（大管） <br>
71 :  Clarinet 单簧管（黑管） <br>
72 :  Piccolo 短笛 <br>
73 :  Flute 长笛 <br>
74 :  Recorder 竖笛 <br>
75 :  Pan Flute 排箫 <br>
76 :  Bottle Blow 吹瓶声 <br>
77 :  Shakuhachi 日本尺八 <br>
78 :  Whistle 口哨声 <br>
79 :  Ocarina 奥卡雷那 <br>
80 :  Lead (square) 合成主音1（方波） <br>
81 :  Lead (sawtooth) 合成主音2（锯齿波） <br>
82 :  Lead (caliope lead)合成主音3 <br>
83 :  Lead (chiff lead) 合成主音4 <br>
84 :  Lead (charang) 合成主音5 <br>
85 :  Lead (voice) 合成主音6（人声） <br>
86 :  Lead (fifths) 合成主音7（平行五度） <br>
87 :  Lead (bass+lead) 合成主音8（贝司加主音） <br>
88 :  Pad (new age) 合成音色1（新世纪） <br>
89 :  Pad (warm) 合成音色（温暖） <br>
90 :  Pad (polysynth) 合成音色3 <br>
91 :  Pad (choir) 合成音色（合唱） <br>
92 :  Pad (bowed) 合成音色5 <br>
93 :  Pad (metallic) 合成音色（金属声） <br>
94 :  Pad (halo) 合成音色（光环） <br>
95 :  Pad (sweep) 合成音色8 <br>
96 :  FX (rain) 合成效果 雨声 <br>
97 :  FX (soundtrack) 合成效果 音轨 <br>
98 :  FX (crystal) 合成效果 水晶 <br>
99 :  FX (atmosphere) 合成效果 大气 <br>
100 :  FX (brightness) 合成效果 明亮 <br>
101 :  FX (goblins) 合成效果 鬼怪 <br>
102 :  FX (echoes) 合成效果 回声 <br>
103 :  FX (sci-fi) 合成效果 科幻 <br>
104 :  Sitar 西塔尔（印度） <br>
105 :  Banjo 班卓琴（美洲） <br>
106 :  Shamisen 三昧线（日本） <br>
107 :  Koto 十三弦筝（日本） <br>
108 :  Kalimba 卡林巴 <br>
109 :  Bagpipe 风笛 <br>
110 :  Fiddle 民族提琴 <br>
111 :  Shanai 山奈 <br>
112 :  Tinkle Bell 叮当铃 <br>
113 :  Agogo 摇摆舞铃 <br>
114 :  Steel Drums 钢鼓 <br>
115 :  Woodblock 木鱼 <br>
116 :  Taiko Drum 太鼓 <br>
117 :  Melodic Tom 通通鼓 <br>
118 :  Synth Drum 合成鼓 <br>
119 :  Reverse Cymbal 铜钹 <br>
120 :  Guitar Fret Noise 吉他换把杂音 <br>
121 :  Breath Noise 呼吸声 <br>
122 :  Seashore 海浪声 <br>
123 :  Bird Tweet 鸟鸣 <br>
124 :  Telephone Ring 电话铃 <br>
125 :  Helicopter 直升机 <br>
126 :  Applause 鼓掌声 <br>
127 :  Gunshot 枪击声 <br>




