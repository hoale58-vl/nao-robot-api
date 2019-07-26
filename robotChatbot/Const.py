ROBOT_CHATBOT_WEBSOCKET_PORT = 5002
STOP_LISTENING_TIMEOUT = 15

CHUNK = 8192
RATE = 48000
GOOGLE_CLOUD_TIME_OUT = 5
pause_threshold = 1.5
energy_threshold = 600

WEBSOCKET_CONTROL_URL = "ws://127.0.0.1/controlbot/"
chatbot_id = "naorobot"

GOOGLE_JSON_FILE_PATH = 'naorobot-lvh.json'
with open(GOOGLE_JSON_FILE_PATH, "r") as f:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()