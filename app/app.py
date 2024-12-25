import os
import yaml
import time
import sherpa_onnx
import io
import soundfile as sf
from logging.config import dictConfig
from flask import Flask, request, Response

rootdir = os.getcwd()
model_dir = os.path.join(rootdir, "models")
log_file = "/logs/sherpa_{}.log".format(time.strftime('%y%m%d', time.localtime(time.time())))

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s]<%(filename)s:%(lineno)d>%(levelname)-8s: %(message)s',
            "datefmt": '%y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s[%(module)s]%(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': log_file,
            'delay': True,
            'maxBytes': 5242880,
            'backupCount': 10,
            'encoding': 'utf8',
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file']
    }
})

model_config = yaml.safe_load(open(os.path.join(model_dir, "config.yaml"), "r"))
model_dir = model_config.get("model_folder", "./models")
model_config = {key:os.path.join(model_dir, value) for key, value in model_config.items() if key != "model_dir"}

tts_config = sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=model_config.get("model", "./models/model.onnx"),
            lexicon=model_config.get("lexicon", ""),
            data_dir=model_config.get("data_dir", ""),
            dict_dir=model_config.get("dict_dir", ""),
            tokens=model_config.get("tokens", "./models/tokens.txt"),
        ),
        provider="cpu",
        debug=False,
        num_threads=1,
    ),
    rule_fsts=os.path.join(model_config.get("rule_fsts", "")),
    max_num_sentences=1,
)
if not tts_config.validate():
    raise ValueError("Please check your config")
tts_server = sherpa_onnx.OfflineTts(tts_config)
app = Flask(__name__)
app.logger.info(f"model_config: {model_config}")

@app.route("/tts", methods=["POST"])
def tts():
    text = request.json.get("text", "")
    sid = request.json.get("sid", 0)
    speed = request.json.get("speed", 1.2)
    app.logger.debug(f"tts config: {tts_config}")
    audio = tts_server.generate(text, sid=sid, speed=speed)
    if audio is None:
        return Response("Failed to generate speech", status=400)
    buffer = io.BytesIO()
    sf.write(buffer, audio.samples, samplerate=audio.sample_rate, format="WAV")
    buffer.seek(0)
    return Response(buffer, mimetype="audio/wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
