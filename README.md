# Common

```
pip install -r requirements.txt
```

# Control + Stream

**Gi**

```
ln -s /usr/lib/python3/dist-packages/gi ~/anaconda3/envs/rasa/lib/python3.6/site-packages/
cd ~/anaconda3/envs/rasa/lib/python3.6/site-packages/gi/
sudo cp _gi.cpython-35m-x86_64-linux-gnu.so _gi.cpython-36m-x86_64-linux-gnu.so
sudo cp _gi_cairo.cpython-35m-x86_64-linux-gnu.so _gi_cairo.cpython-36m-x86_64-linux-gnu.so
sudo apt-get update -y
*sudo apt-get install -y gir1.2-gtk-3.0*
sudo apt-get install -y gir1.2-gst-plugins-base-1.0
```

```
sudo yum install cairo cairo-dev gstreamer1 gstreamer1-plugins-good
```

**OpenCV**

```
sudo apt-get install libsm6 libxext6 libxrender-dev
```

**RetinaFace**

```
cd retinaFace
git clone https://github.com/deepinsight/insightface
cd insightface/RetinaFace
make -j8
```

# Nginx Config

```
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
```

# Test websocket

```
wscat -c wss://chatbot.ari.com.vn/webchatbot/
```

# Script startup server

```
#! /bin/bash
cd robotControl && nohup python webSocketControl.py > log.log & 
cd robotChatbot && nohup python webSocketChatbot.py > log.log & 
```

# Script stop server

```
#! /bin/bash
killall /home/black/anaconda3/envs/rasa_chatbot/bin/python
```

# Loop back audio
## NAO

```
pactl load-module module-rtp-send source=alsa_output.0.output-speakers.monitor destination_ip=<server_ip>
```

## Server

```
pactl load-module module-rtp-recv sap_address=<server_ip>
```

### List loaded module

```
pactl list short
```

### Unload loaded module

```
pactl unload <index>
```
