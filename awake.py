# -*- coding: utf-8 -*-

import pyaudio
import numpy as np
from scipy import fftpack
import time
# import threading
import _thread
import wave


class Recorder():
    def __init__(self, chunk=1024, channels=1, rate=64000):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16 # 每次采集的位数
        self.CHANNELS = channels
        self.RATE = rate
        self._frames = []
        self.RECORD_SECONDS = 0

    def recording(self, time=0, threshold=7000):
        self._frames = []
        self.RECORD_SECONDS = time
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        print("录音中······")
        if time > 0:
            for i in range(0, int(self.RATE/self.CHUNK*self.RECORD_SECONDS)):
                data = stream.read(self.CHUNK)
                self._frames.append(data)
        else:
            stopflag = 0
            stopflag2 = 0
            while True:
                data = stream.read(self.CHUNK)
                rt_data = np.frombuffer(data, np.dtype('<i2'))  # int16 little endian的16-bit整数

                # 傅里叶变换
                fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
                fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size//2+1]  # 取0和正频率点，复数的绝对值--取模，取振幅谱的前半部分

                # 测试阈值
                print(sum(fft_data)//len(fft_data))

                # 判断麦克风是否停止，判断说话是否结束
                if sum(fft_data) // len(fft_data) > threshold:
                    stopflag += 1
                else:
                    stopflag2 += 1
                oneSecond = int(self.RATE/self.CHUNK)
                if stopflag2 + stopflag > oneSecond:
                    if stopflag2 > oneSecond // 3*2:
                        break
                    else:
                        stopflag2 = 0
                        stopflag = 0
                self._frames.append(data)
        print("*录音结束")

        stream.stop_stream()
        stream.close()
        p.terminate()

    def save(self, filename):

        p = pyaudio.PyAudio()
        if not filename.endswith(".wav"):
            filename = filename + ".wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        print("Saved")


if __name__ == "__main__":
    # rec == Recorder()
    # begin = time.time()
    # print("音频接收打开")
    # while time.time()<begin+4:
    #     rec.start()


    # for i in range(1, 4):
    #     a = int(input('请输入相应数字开始:'))
    #     if a == 1:
    rec = Recorder()
            # begin = time.time()
    # print("Start recording")
    rec.recording()
            # b = int(input('请输入相应数字停止:'))
            # if b == 2:
    # print("Stop recording")
    # rec.stop()
                # fina = time.time()
                # t = fina - begin
                # print('录音时间为%ds' % t)
    rec.save("tmp.wav")