# Common
pip install SimpleWebSocketServer
# Chatbot
pip install SpeechRecognition 
pip install googletrans
pip install oauth2client

# Control + Stream
**Gi**
pip install vext.gi
ln -s /usr/lib/python3/dist-packages/gi ~/anaconda3/envs/rasa/lib/python3.6/site-packages/
cd ~/anaconda3/envs/rasa/lib/python3.6/site-packages/gi/
sudo cp _gi.cpython-35m-x86_64-linux-gnu.so _gi.cpython-36m-x86_64-linux-gnu.so
sudo cp _gi_cairo.cpython-35m-x86_64-linux-gnu.so _gi_cairo.cpython-36m-x86_64-linux-gnu.so
sudo apt-get update -y
*sudo apt-get install -y gir1.2-gtk-3.0*
sudo apt-get install -y gir1.2-gst-plugins-base-1.0

**OpenCV**
pip install opencv-python
pip install opencv-contrib-python
sudo apt-get install libsm6 libxext6 libxrender-dev

**RetinaFace**
pip install mxnet==1.4.0
pip install numpy==1.16
cd retinaFace/insightface/RetinaFace
make -j8

# Websocket client
pip install websocket_client==0.48

# Nginx Config
upstream controlbot-ws {
    server 127.0.0.1:5001;
}

upstream chatbot-ws {
    server 127.0.0.1:5002;
}

server {
        listen 80;
        listen [::]:80;
        server_name chatbot.ari.com.vn;

        access_log /opt/chatbot/logs/nginx-access.log;
        error_log /opt/chatbot/logs/nginx-error.log;

        location /conversations/ {
                proxy_pass http://127.0.0.1:5006/conversations/;
        }
        location /chat/ {
                proxy_pass http://127.0.0.1:5000/chat/;
        }

        location /controlbot/ {
            proxy_pass http://controlbot-ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        location /chatbot/ {
            proxy_pass http://chatbot-ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }
}

# Test websocket
wscat -c wss://chatbot.ari.com.vn/webchatbot/

# Script startup server
#! /bin/bash
cd /home/black/workSpace/nlu/gumi_project/gumi && nohup /home/black/anaconda3/envs/rasa_chatbot/bin/python -m rasa run -m models --enable-api --log-file out.log -p 5006 > log.log &

cd /home/black/workSpace/nlu/gumi_project/simpleApiServer && nohup /home/black/anaconda3/envs/rasa_chatbot/bin/python apiServer.py > log.log &

cd /home/black/workSpace/nlu/gumi_project/serverSource/robotControl && nohup /home/black/anaconda3/envs/rasa_chatbot/bin/python webSocketControl.py > log.log & 

cd /home/black/workSpace/nlu/gumi_project/serverSource/robotChatbot && nohup /home/black/anaconda3/envs/rasa_chatbot/bin/python webSocketChatbot.py > log.log & 

# Script stop server
#! /bin/bash
killall /home/black/anaconda3/envs/rasa_chatbot/bin/python