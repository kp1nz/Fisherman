import tkinter as tk
from tkinter import scrolledtext
import librosa
import numpy as np
import pyaudio
import keyboard
import time
import random
import threading

class AudioMatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fisher_v0.0.3")
        self.root.resizable(False, False)

        self.threshold = tk.DoubleVar(value=888)
        self.is_listening = False
        self.audio_thread = None
        self.last_match_time = 0  # 记录上一次匹配的时间
        self.start_time = None  # 记录程序启动时间

        # 添加配置项
        self.key1 = tk.StringVar(value='1')  # 抛竿按键
        self.key2 = tk.StringVar(value='2')  # 收杆按键
        self.timed_key1 = tk.StringVar(value='3')  # 绑饵料按键
        self.timed_interval1 = tk.StringVar(value='9-10')  # 绑饵料时间间隔
        self.timed_key2 = tk.StringVar(value='4')  # 悬浮术按键
        self.timed_interval2 = tk.StringVar(value='')  # 悬浮术时间间隔

        self.create_widgets()

    def create_widgets(self):
        self.log_output = scrolledtext.ScrolledText(self.root, width=60, height=20)
        self.log_output.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        frame = tk.Frame(self.root)
        frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        tk.Label(frame, text="Threshold:").grid(row=0, column=0, padx=5, pady=10)
        self.threshold_entry = tk.Entry(frame, textvariable=self.threshold, width=10)
        self.threshold_entry.grid(row=0, column=1, padx=5, pady=10)

        tk.Label(frame, text="Key for cast:").grid(row=1, column=0, padx=5, pady=10)
        self.key1_entry = tk.Entry(frame, textvariable=self.key1, width=10)
        self.key1_entry.grid(row=1, column=1, padx=5, pady=10)

        tk.Label(frame, text="Key for reel in:").grid(row=2, column=0, padx=5, pady=10)
        self.key2_entry = tk.Entry(frame, textvariable=self.key2, width=10)
        self.key2_entry.grid(row=2, column=1, padx=5, pady=10)

        self.start_button = tk.Button(frame, text="Start", command=self.start_listening, width=10)
        self.start_button.grid(row=0, column=2, padx=5, pady=10)
        self.stop_button = tk.Button(frame, text="Stop", command=self.stop_listening, state=tk.DISABLED, width=10)
        self.stop_button.grid(row=0, column=3, padx=5, pady=10)

        tk.Label(frame, text="Key1 (绑饵料):").grid(row=3, column=0, padx=5, pady=10)
        self.timed_key1_entry = tk.Entry(frame, textvariable=self.timed_key1, width=10)
        self.timed_key1_entry.grid(row=3, column=1, padx=5, pady=10)
        tk.Label(frame, text="Interval (分钟):").grid(row=3, column=2, padx=5, pady=10)
        self.timed_interval1_entry = tk.Entry(frame, textvariable=self.timed_interval1, width=10)
        self.timed_interval1_entry.grid(row=3, column=3, padx=5, pady=10)

        tk.Label(frame, text="Key2 (悬浮术):").grid(row=4, column=0, padx=5, pady=10)
        self.timed_key2_entry = tk.Entry(frame, textvariable=self.timed_key2, width=10)
        self.timed_key2_entry.grid(row=4, column=1, padx=5, pady=10)
        tk.Label(frame, text="Interval (分钟):").grid(row=4, column=2, padx=5, pady=10)
        self.timed_interval2_entry = tk.Entry(frame, textvariable=self.timed_interval2, width=10)
        self.timed_interval2_entry.grid(row=4, column=3, padx=5, pady=10)

        self.watermark = tk.Label(self.root, text="Author: kp1nz", font=('Arial', 8), fg='gray')
        self.watermark.grid(row=5, column=3, sticky=tk.SE, padx=10, pady=5)

        self.timer_label = tk.Label(self.root, text="Uptime: 0h 0m 0s", font=('Arial', 8), fg='gray')
        self.timer_label.grid(row=5, column=0, sticky=tk.SW, padx=10, pady=5)

    def log(self, message):
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.yview(tk.END)

    def update_timer(self):
        if self.is_listening:
            elapsed_time = int(time.time() - self.start_time)
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.config(text=f"运行时长: {hours}h {minutes}m {seconds}s")
            self.root.after(1000, self.update_timer)

    def load_audio(self, file_path):
        y, sr = librosa.load(file_path, sr=None)
        return y, sr

    def extract_features(self, y, sr, n_mfcc=13):
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        rms = librosa.feature.rms(y=y)
        return mfccs, rms

    def compare_features(self, mfccs1, rms1, mfccs2, rms2):
        min_mfcc_columns = min(mfccs1.shape[1], mfccs2.shape[1])
        mfccs1 = mfccs1[:, :min_mfcc_columns]
        mfccs2 = mfccs2[:, :min_mfcc_columns]
        min_rms_columns = min(rms1.shape[1], rms2.shape[1])
        rms1 = rms1[:, :min_rms_columns]
        rms2 = rms2[:, :min_rms_columns]
        mfcc_distance = round(np.linalg.norm(mfccs1 - mfccs2), 2)
        rms_distance = round(np.linalg.norm(rms1 - rms2), 2)
        return mfcc_distance, rms_distance

    def listen_and_compare(self, target_mfcc, target_rms, sr, target_length):
        chunk_size = sr // 4  # 假设每0.25秒处理一次
        overlap = chunk_size // 2  # 重叠一半数据
        format = pyaudio.paInt16
        channels = 1
        rate = sr

        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)
        self.log("Listening...")

        audio_buffer = np.array([], dtype=np.float32)
        next_timed_key1 = time.time() + self.get_random_interval(self.timed_interval1.get()) if self.timed_interval1.get() else None
        next_timed_key2 = time.time() + self.get_random_interval(self.timed_interval2.get()) if self.timed_interval2.get() else None

        try:
            while self.is_listening:
                data = stream.read(chunk_size, exception_on_overflow=False)
                y = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                audio_buffer = np.concatenate((audio_buffer, y))

                while len(audio_buffer) >= chunk_size and self.is_listening:
                    processed_audio = audio_buffer[:chunk_size]
                    mfccs, rms = self.extract_features(processed_audio, sr)
                    mfcc_distance, rms_distance = self.compare_features(target_mfcc, target_rms, mfccs, rms)

                    formatted_message = f"MFCC Distance: {mfcc_distance:.2f}, RMS Distance: {rms_distance:.2f}"
                    self.log(formatted_message)

                    if mfcc_distance < self.threshold.get() and rms_distance < self.threshold.get():
                        self.log("Match found!!!")
                        keyboard.press_and_release(self.key2.get())
                        time.sleep(random.uniform(0.8, 1.5))
                        keyboard.press_and_release(self.key1.get())
                        self.last_match_time = time.time()

                    elif time.time() - self.last_match_time >= 1:
                        keyboard.press_and_release(self.key1.get())
                        self.last_match_time = time.time()

                    # 定时按键1
                    if next_timed_key1 and time.time() >= next_timed_key1:
                        keyboard.press_and_release(self.timed_key1.get())
                        next_timed_key1 = time.time() + self.get_random_interval(self.timed_interval1.get())

                    # 定时按键2
                    if next_timed_key2 and time.time() >= next_timed_key2:
                        keyboard.press_and_release(self.timed_key2.get())
                        next_timed_key2 = time.time() + self.get_random_interval(self.timed_interval2.get())

                    audio_buffer = audio_buffer[overlap:]  # 保留重叠部分的数据
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def get_random_interval(self, interval_str):
        if '-' in interval_str:
            min_interval, max_interval = map(float, interval_str.split('-'))
            return random.uniform(min_interval, max_interval) * 60
        else:
            return float(interval_str) * 60

    def start_listening(self):
        self.is_listening = True
        self.log("Please select the wow window with the mouse....")
        self.start_time = time.time()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.disable_entries()
        keyboard.press_and_release(self.timed_key1.get())  # 启动时按一下绑饵料按键
        self.root.after(3000, self.start_audio_thread)  # 休眠三秒后启动音频线程
        self.update_timer()  # 开始更新运行时长

    def start_audio_thread(self):
        self.audio_thread = threading.Thread(target=self.run_audio_matcher)
        self.audio_thread.start()

    def stop_listening(self):
        self.is_listening = False
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1)
        if self.audio_thread.is_alive():
            self.log("Thread did not stop properly.")
        self.start_button.config(state=tk.NORMAL)
        self.enable_entries()
        self.stop_button.config(state=tk.DISABLED)

    def run_audio_matcher(self):
        target_file = 'sc.wav'
        y, sr = self.load_audio(target_file)
        target_mfcc, target_rms = self.extract_features(y, sr)
        target_length = len(y)
        self.listen_and_compare(target_mfcc, target_rms, sr, target_length)

    def disable_entries(self):
        self.threshold_entry.config(state=tk.DISABLED)
        self.key1_entry.config(state=tk.DISABLED)
        self.key2_entry.config(state=tk.DISABLED)
        self.timed_key1_entry.config(state=tk.DISABLED)
        self.timed_interval1_entry.config(state=tk.DISABLED)
        self.timed_key2_entry.config(state=tk.DISABLED)
        self.timed_interval2_entry.config(state=tk.DISABLED)

    def enable_entries(self):
        self.threshold_entry.config(state=tk.NORMAL)
        self.key1_entry.config(state=tk.NORMAL)
        self.key2_entry.config(state=tk.NORMAL)
        self.timed_key1_entry.config(state=tk.NORMAL)
        self.timed_interval1_entry.config(state=tk.NORMAL)
        self.timed_key2_entry.config(state=tk.NORMAL)
        self.timed_interval2_entry.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioMatcherApp(root)
    root.mainloop()
