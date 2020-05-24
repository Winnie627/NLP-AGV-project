#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding:unicode_escape
# Date    : 2018-12-02 19:04:55
import wave
import requests
import time
import base64
from pyaudio import PyAudio, paInt16
import logging
import re
from playsound import playsound

framerate = 16000  # 采样率
num_samples = 2000  # 采样点
channels = 1  # 声道
sampwidth = 2  # 采样宽度2bytes
FILEPATH = 'speech.wav'

base_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s"
APIKey = "yDvojaG6MZQo8j99Cbj6731g"
SecretKey = "P1rqYcsja44KrrWTrq6LGmnX19FtjI0X"

HOST = base_url % (APIKey, SecretKey)
DIRECTION ={
    u'前': 0,
    u'后': 1,
    u'左': 2,
    u'右': 3,
    u'停': 4,
    u'电': 5,
    u'卧': 6
}


def direction(input):
    linput = list(input)
    while linput:
        incdg = linput.pop()
        if incdg in DIRECTION:
            output =DIRECTION.get(incdg)
        else:
            continue
    return output

CN_NUM = {
    u'零': 0,
    u'一': 1,
    u'二': 2,
    u'三': 3,
    u'四': 4,
    u'五': 5,
    u'六': 6,
    u'七': 7,
    u'八': 8,
    u'九': 9,

    u'两': 2
}

CN_UNIT = {
    u'十': 10,
    u'百': 100,
    u'千': 1000
}


def cn2dig(cn):
    lcn = list(cn)
    unit = 0
    ldig = []  # 临时数组
    while lcn:
        cndig = lcn.pop()  # 移除列表中的一个元素（默认是最后一个元素），返回移除的元素对象
        if cndig in CN_UNIT:
            unit = CN_UNIT.get(cndig)
        elif cndig in CN_NUM:
            dig = CN_NUM.get(cndig)
            if unit:
                dig = dig * unit
                unit = 0
            ldig.append(dig)
        else:
            continue

    if unit == 10:
        ldig.append(10)

    ret = 0
    tmp = 0

    while ldig:
        x = ldig.pop()

        tmp += x
    ret += tmp
    return ret


def get_key(dict, value):
    return [k for k, v in dict.items() if v == value][0]


def getToken(host):
    res = requests.post(host)
    return res.json()['access_token']


def save_wave_file(filepath, data):
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b''.join(data))
    wf.close()


def my_record():
    pa = PyAudio()
    stream = pa.open(format=paInt16, channels=channels,
                     rate=framerate, input=True, frames_per_buffer=num_samples)
    my_buf = []
    # count = 0
    t = time.time()
    print('正在录音...')

    while time.time() < t + 4:  # 秒
        string_audio_data = stream.read(num_samples)
        my_buf.append(string_audio_data)
    print('录音结束.')
    save_wave_file(FILEPATH, my_buf)
    stream.close()


def get_audio(file):
    with open(file, 'rb') as f:
        data = f.read()
    return data


def speech2text(speech_data, token, dev_pid=1537):
    FORMAT = 'wav'
    RATE = '16000'
    CHANNEL = 1
    CUID = '*******'
    SPEECH = base64.b64encode(speech_data).decode('utf-8')

    data = {
        'format': FORMAT,
        'rate': RATE,
        'channel': CHANNEL,
        'cuid': CUID,
        'len': len(speech_data),
        'speech': SPEECH,
        'token': token,
        'dev_pid': dev_pid
    }
    url = 'https://vop.baidu.com/server_api'
    headers = {'Content-Type': 'application/json'}
    # r=requests.post(url,data=json.dumps(data),headers=headers)
    print('正在识别...')
    r = requests.post(url, json=data, headers=headers)
    Result = r.json()
    if Result["err_msg"] == "success.":
        print(Result['result'][0])
        return Result['result'][0]
    else:
        print("内容获取失败，退出语音识别")
        return -1


def text2speech(str_input, token):  # 输入要合成的文字
    apiUrl = 'https://tsn.baidu.com/text2audio'
    data = {
        "tex": str_input,  # 要进行语音合成的内容
        "tok": token,  # 个人的鉴权认证Acess Token
        "cuid": "*******",  # 随便一个值就好了，官网推荐是个人电脑的MAC地址
        "ctp": 1,  # 客户端类型，web端固定值1
        "lan": "zh",  # 中文语言
        "spd": 5,  # 语速
        "pit": 5,  # 语调
        "vol": 5,  # 音量
        "per": 4,  # 男女声，4是度丫丫
        "aue": 3,  # 音频格式，3是mp3
    }
    r = requests.post(apiUrl, data=data)
    # print(r.headers)  # 返回的表头
    text = r.content  # mp3二进制数据
    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    mp3_num = 0
    filename = f"00{mp3_num}"  # 保存的文件名
    if not isinstance(text, dict):
        with open(filename + '.mp3', 'wb+') as f:
            f.write(text)
    mp3_num += 1

    playsound(filename + '.mp3')


if __name__ == '__main__':
    pattern = re.compile(u"[0-9_\u4E00-\u9FA5]+")
    logging.basicConfig(level=logging.INFO)
    flag = 'y'
    while flag.lower() == 'y':
        # print('请输入数字选择语言：')
        # devpid = input('1536：普通话(简单英文),1537:普通话(有标点),1737:英语,1637:粤语,1837:四川话\n')
        devpid = '1537'
        # my_record()
        TOKEN = getToken(HOST)
        speech = get_audio(FILEPATH)
        result = speech2text(speech, TOKEN, int(devpid))
        if result == -1:
            flag = input('Continue?(y/n):')
        result_re1 = re.findall(r'\d+.\d+', str(result))  # 当出现小数时，提取中文字符串里的小数，对应移动距离
        result_re2 = re.findall(pattern, str(result))  # 整数时，提取纯文字字符串(不带标点）

        print('你说的是不是:', result)
        text = "你说的是不是%s" % (result)
        # text = text.encode('utf-8')
        # text = text.decode()
        text2speech(text, TOKEN)
        if input('y/n:') == str('y'):
            # 执行指令
            # 运动量为整数（数字可能为大写）
            pattern_int = re.compile('[0-9]+')
            match = pattern_int.findall(str(result))

            if match:
                if result_re1 == []:
                    vol = match[0]  # 含有数字，使用数字作为移动距离/角度
                else:
                    vol = result_re1[0]
            else:
                vol = cn2dig(result_re2[0])  # 不含数字，将汉字数字转换
            vol = float(vol)

            command = result_re2[0]
            dire = direction(command)  # 方向对应的数字变量
            print(dire)
            if dire < 2:
                # 移动距离数值
                dist = vol
                print("向 %s 移动 %f 米" % (get_key(DIRECTION, dire), dist))
            elif dire >= 2 and dire < 4:
                # 转动角度数值
                ang = vol
                print("向 %s 转动 %f 度" % (get_key(DIRECTION, dire), ang))
            elif dire == 4:
                print("停止命令")

            elif dire == 5:
                print("去充电命令")

            else:
                print("去卧室命令")


        flag = input('Continue?(y/n):')