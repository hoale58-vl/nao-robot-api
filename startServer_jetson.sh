#! /bin/bash
./stopServer.sh
python_env='/home/black/env/nao/bin/python'
working_dir='/home/black/naoServer'

python_env2='/home/black/env/rasa/bin/python'
working_dir2='/home/black/rasa'

# export MXNET_CUDNN_AUTOTUNE_DEFAULT=0
# cd ${working_dir}/robotControl && nohup ${python_env} webSocketControl.py &
cd ${working_dir}/robotChatbot && nohup ${python_env} webSocketChatbot.py &

cd ${working_dir2} && nohup ${python_env2} -m rasa run actions >> action.log &
cd ${working_dir2} && nohup ${python_env2} -m rasa run -m models --enable-api --log-file out.log -p 5006 &

ip4=$(/sbin/ip -o -4 addr list eth0 | awk '{print $4}' | cut -d/ -f1)
/usr/bin/pactl unload-module module-rtp-recv
/usr/bin/pactl load-module module-rtp-recv sap_address=$ip4

export MXNET_CUDNN_AUTOTUNE_DEFAULT=0
cd ${working_dir}/robotControl && ${python_env} webSocketControl.py