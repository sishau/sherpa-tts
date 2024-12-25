# sherpa-tts
---

本地 TTS 服务, 使用 docker 运行 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 引擎。

## 使用

1. 下载模型 [vits-melo-tts-zh_en](https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-melo-tts-zh_en.tar.bz2), 解压后放入./app/models 文件夹

    目录结构:

    |- app

    |    |-models

    |    |    |- vits-melo-tts-zh_cn

    |    |    |- config.yaml

    |    |- app.py

    |- logs


```bash
#
docker build -t sherpa-tts:dev .
docker run -it --name sherpa-tts-dev -p 8080:8080 -v ./app:/app -v ./logs:/logs sherpa-tts:dev
```

部署完成后, 可以使用 `curl -H "Content-Type: application/json" -X POST http://127.0.0.1:8080/tts -d "{\"text\": \"Hello, 文字转语音测试.\"}" -o ./test.wav` 进行测试

## 接口
```
# 8080/tts

# method: post

# 入参:
    text: str, 待转换的文字
    sid: 发音人
    speed: 朗读速度

# 返回: audio/wav
```

## 感谢
- 参考 [sherpa-onnx/python-api-examples/offline-tts.py](https://github.com/k2-fsa/sherpa-onnx/blob/master/python-api-examples/offline-tts.py)
