# Common
pip install SimpleWebSocketServer
# Chatbot
pip install SpeechRecognition 
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