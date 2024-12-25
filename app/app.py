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

module_config = yaml.safe_load(open(os.path.join(model_dir, "config.yaml"), "r"))

tts_config = sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=module_config.get("module_name", "./models/model.onnx"),
            lexicon=module_config.get("lexicon", ""),
            data_dir=module_config.get("data_dir", ""),
            dict_dir=module_config.get("dict_dir", ""),
            tokens=module_config.get("tokens", "./models/tokens.txt"),
        ),
        provider="cpu",
        debug=False,
        num_threads=8,
    ),
    rule_fsts=os.path.join(module_config.get("rule_fsts", "")),
    max_num_sentences=1,
)
if not tts_config.validate():
    raise ValueError("Please check your config")
tts_server = sherpa_onnx.OfflineTts(tts_config)
app = Flask(__name__)

@app.route("/tts", methods=["POST"])
def tts():
    text = request.json.get("text", "")
    sid = request.json.get("sid", 0)
    speed = request.json.get("speed", 1.2)
    app.logger.debug(f"tts_server.generate: {text}, {sid}, {speed}")
    app.logger.debug(f"tts config: {tts_config}")
    audio = tts_server.generate(text, sid=sid, speed=speed)
    if audio is None:
        return Response("Failed to generate speech", status=400)
    audio_duration = len(audio.samples) / audio.sample_rate
    app.logger.info(f"tts_server.generate: {audio_duration}")
    buffer = io.BytesIO()
    sf.write(buffer, audio.samples, samplerate=audio.sample_rate, format="WAV")
    buffer.seek(0)
    return Response(buffer, mimetype="audio/wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
