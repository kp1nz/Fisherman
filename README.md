# Fisherman

> [README_CN](https://github.com/kp1nz/Fisherman/blob/main/README_CN.md)

Fisherman is a GUI application built with Python and Tkinter, specifically designed for the game World of Warcraft (WoW) to automate fishing by detecting specific audio signals. This application provides automated keyboard operations based on audio feature matching, primarily used to detect specific audio signals and execute predefined actions.

## Features Overview

- **Audio Matching**: Listens to real-time audio and compares features with the target audio, including MFCC and RMS.
- **Keyboard Simulation**: Automatically simulates key presses when a matching audio is detected, with customizable keys.
- **Timed Key Operations**: Supports setting multiple timed key presses to automatically execute certain actions at specific intervals.
- **Uptime Display**: Shows the program's runtime, allowing users to monitor the application's status.

## Installation Requirements

- Python 3.x
- Required Python Libraries:
  - tkinter (standard library, usually comes with Python)
  - librosa: for audio signal processing
  - numpy: for numerical computations
  - pyaudio: for audio input
  - keyboard: for simulating keyboard presses

Install the required libraries with the following command:

```sh
pip install numpy librosa pyaudio keyboard
```

## Usage Instructions

1. Run the `main.py` file to start the application:

   ```sh
   python main.py
   ```

2. Application Interface:
   - **Log Window**: Displays program logs and matching results.
   - **Threshold Setting**: Set the feature distance threshold for audio matching. Lower values result in stricter matching.
   - **Key Configuration**: Customize keys for actions like casting, reeling, baiting, and levitating.
   - **Start/Stop Buttons**: Click the "Start" button to begin audio listening, and click "Stop" to end it.

3. **Timed Operations Setup**:
   - Set the execution interval for timed key presses, supporting range formats such as `9-10` minutes for random intervals.

## Main Components and Features

- **Fisherman Class**: Implements the entire application logic, including GUI creation, audio processing, feature comparison, and key simulation.
- **Audio Processing**: Uses `librosa` for loading audio and feature extraction, calculating MFCC and RMS for audio similarity comparison.
- **Keyboard Operations**: Simulates key responses using the `keyboard` module to automate actions.
- **Real-time Listening**: Uses `pyaudio` to capture audio in real-time and continuously compare it with the target audio.

## Notes

- **Administrator Privileges**: The `keyboard` module may require administrator privileges on some operating systems to simulate key presses properly.
- **Audio Device**: `pyaudio` requires a microphone device. If unavailable, ensure the system has a suitable audio input source configured.

## License

This project is open-source and follows the MIT License. You are free to use, modify, and distribute the code.
