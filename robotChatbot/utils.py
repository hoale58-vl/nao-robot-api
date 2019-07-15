import requests

class BotApi:
	def __init__(self, id_user, ip="127.0.0.1", port=5005):
		url = "http://{}:{}/conversations/{}/".format(ip, str(port), str(id_user))
		self.urlAddMsg = url + "messages"
		self.urlPredictNextAction = url + "predict"
		self.executeAction = url + "execute"
	
	def requestMsg(self, msg):
		response = requests.post(self.urlAddMsg, json={"text":msg, "sender":"user"})
		return response.status_code

	def requestPredict(self):
		response = requests.post(self.urlPredictNextAction)
		if(response.status_code == requests.codes.ok):
			return {"name": response.json()['scores'][0]['action']}
		return None

	def askBot(self, msg):
		if self.requestMsg(msg) != requests.codes.ok:
			return None
		predict = self.requestPredict()
		response = requests.post(self.executeAction, json=predict)
		if(response.status_code == requests.codes.ok):
			messages = response.json()['messages']
			if(len(messages) > 0):
				return messages[0]['text']
			else:
				return ""
		return None
