import requests
import os
import io
import sounddevice as sd
import soundfile as sf

url = "http://localhost:8080/tts"

data = {
    "text": "Are you ok 是雷军2015年4月小米在印度举行新品发布会时说的。他还说过 I am very happy to be in China.雷军事后在微博上表示「万万没想到，视频火速传到国内，全国人民都笑了」、「现在国际米粉越来越多，我的确应该把英文学好，不让大家失望！加油！」",
    "sid": 1,
    "speed": 1.1,
}

data2 = {
    "text": "它也支持繁体字. 我相信你們一定聽過愛迪生說過的這句話Genius is one percent inspiration and ninety-nine percent perspiration.",
    "sid": 1,
    "speed": 1.1,
}


response = requests.post(url, json=data2)
if response.status_code == 200:
    print(len(response.content))
    audio_data = response.content
else:
    print(f'Error: {response.status_code} - {response.text}')

audio, simple_rate = sf.read(io.BytesIO(audio_data), dtype='int16')
device_info = sd.query_devices()
device_index = sd.default.device[1]
print(f'Using output device: {device_info[device_index]["name"]}')
with sd.OutputStream(device=device_index, channels=1, samplerate=simple_rate, blocksize=1024):
    sd.play(audio, device=device_index, samplerate=simple_rate)
    status = sd.wait()
    if status:
        print('Audio playback finished successfully.')
    else:
        print('Audio playback failed.')
