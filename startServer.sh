#! /bin/bash
./stopServer.sh
python_env='/home/black/.env/naoServer/bin/python'
working_dir='/home/black/naoServer'

cd ${working_dir}/robotControl && nohup ${python_env} webSocketControl.py >> log.log &
cd ${working_dir}/robotChatbot && nohup ${python_env} webSocketChatbot.py >> log.log &
