from flask import Flask, jsonify, request
from botApi import BotApi
app = Flask(__name__)

@app.route('/chat/<user_id>', methods = ['POST'])
def chat(user_id):
        data = request.json
        if 'msg' not in data:
                return jsonify(isError= False,
                                                        message= "Bad Request",
                                                        statusCode= 400,
                                                        data= {"msg":"Missing msg param"}), 400
        msg = data['msg']
        bot = BotApi(user_id)
        msg = bot.askBot(msg)
        if msg is None:
                return jsonify(isError= False,
                                                        message= "Server Error",
                                                        statusCode= 502,
                                                        data= {"msg":"Chatbot mockup failed"}), 502
        return jsonify(isError= False,
                                                        message= "Success",
                                                        statusCode= 200,
                                                        data= {"msg":msg}), 200

@app.route('/naochat/<user_id>', methods = ['POST'])
def naochat(user_id):
        data = request.json
        if 'msg' not in data:
                return jsonify(isError= False,
                                                        message= "Bad Request",
                                                        statusCode= 400,
                                                        data= {"msg":"Missing msg param"}), 400
        msg = data['msg']
        bot = BotApi(user_id)
        msg = bot.askNaoBot(msg)
        if msg is None:
                return jsonify(isError= False,
                                                        message= "Server Error",
                                                        statusCode= 502,
                                                        data= {"msg":"Chatbot mockup failed"}), 502
        return jsonify(isError= False,
                                                        message= "Success",
                                                        statusCode= 200,
                                                        data= {"msg":msg}), 200

if __name__ == '__main__':
        app.run()