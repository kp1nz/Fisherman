import pyaudio
import numpy as np
import keyboard
import time

def listen_sound_threshold(base_volume=8, spike_threshold=10):
    # 初始化PyAudio
    p = pyaudio.PyAudio()

    # 打开流
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    print("Listening for sound...")

    try:
        normal_volume = None  # 用于存储测量到的正常音量水平
        while True:
            # 读取数据
            data = np.frombuffer(stream.read(1024), dtype=np.int16)
            # 计算声音强度
            volume = np.linalg.norm(data)

            # 初始化正常音量水平
            if normal_volume is None:
                normal_volume = volume
                print(f"Initial volume set at: {normal_volume}")

            print(f"Current volume: {volume}")
            if volume > normal_volume + spike_threshold:
                print("Sound spike detected!")
                return True

            # 更新正常音量水平
            normal_volume = (normal_volume * 0.9) + (volume * 0.1)  # 使用移动平均来平滑正常音量水平的变化
    finally:
        # 停止和关闭流
        stream.stop_stream()
        stream.close()
        p.terminate()

def cast_fishing_rod():
    print("Casting fishing rod...")
    keyboard.press_and_release('1')

def reel_in_fishing_rod():
    print("Reeling in fishing rod...")
    keyboard.press_and_release('f')

if __name__ == '__main__':
    try:
        while True:
            cast_fishing_rod()  # 抛竿
            time.sleep(1)  # 延时，根据实际需要调整
            if listen_sound_threshold(base_volume=10000, spike_threshold=8000):
                reel_in_fishing_rod()  # 收杆
                time.sleep(1)  # 延时，根据实际需要调整，避免频繁操作
    except KeyboardInterrupt:
        print("Program terminated by user.")
