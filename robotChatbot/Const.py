ROBOT_CHATBOT_WEBSOCKET_PORT = 8008
STOP_LISTENING_TIMEOUT = 15

CHUNK = 8192
RATE = 48000
GOOGLE_CLOUD_TIME_OUT = 5
pause_threshold = 1.5
energy_threshold = 300

GOOGLE_JSON_FILE_PATH = 'naorobot-lvh.json'
with open(GOOGLE_JSON_FILE_PATH, "r") as f:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()