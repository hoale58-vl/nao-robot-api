#! /bin/bash
./stopServer.sh
python_env='/home/black/anaconda3/envs/rasa_chatbot/bin/python'
python_env2='/home/quyen/.virtualenvs/ari_website/bin/python'
working_dir='/home/black/workSpace/nlu/gumi_project'

cd ${working_dir}/gumi && nohup ${python_env} -m rasa run -m models --enable-api --log-file out.log -p 5006 >> log.log &
cd ${working_dir}/gumi &&  nohup ${python_env} -m rasa run actions >> logAction.log &
cd ${working_dir}/simpleApiServer && nohup ${python_env} apiServer.py >> log.log &
#cd ${working_dir}/serverSource/robotControl && nohup ${python_env} webSocketControl.py >> log.log &
cd ${working_dir}/serverSource/robotChatbot && nohup ${python_env} webSocketChatbot.py >> log.log &

cd /home/quyen/ari_website && nohup ${python_env2} manage.py runserver 0.0.0.0:8080 &