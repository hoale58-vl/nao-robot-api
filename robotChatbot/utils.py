import requests
from googletrans import Translator
import re

class BotApi:
	def __init__(self, id_user, ip="127.0.0.1", port=5006):
		url = "http://{}:{}/conversations/{}/".format(ip, str(port), str(id_user))
		self.urlAddMsg = url + "messages"
		self.urlPredictNextAction = url + "predict"
		self.executeAction = url + "execute"
		self.translator = Translator()
		self.lang = 'vi'
	
	def requestMsg(self, msg):
		response = requests.post(self.urlAddMsg, json={"text":msg, "sender":"user"})
		if(response.status_code == requests.codes.ok):
			self.lang = response.json()['latest_message']['lang']
		else:
			self.lang = 'vi'
		return response.status_code

	def requestPredict(self):
		response = requests.post(self.urlPredictNextAction)
		if(response.status_code == requests.codes.ok):
			return {"name": response.json()['scores'][0]['action']}
		return None

	def listen(self):
		return {"name": "action_listen"}

	def translate(self, text):
		if self.lang != 'vi':
			if self.lang in ['ja','zh-cn']:
				result = self.translator.translate(text, src='vi', dest=self.lang)
			else:
				result = self.translator.translate(text, src='vi', dest='en')
			return result.text
		return text

	def askBot(self, msg):
		if self.requestMsg(msg) != requests.codes.ok:
			return None, None
		botRes, lang = ("", None)
		max_action = 10
		for x in range(max_action):
			predict = self.requestPredict()
			if predict['name'] is None:
				return None, None
			elif re.match("utter_.*", predict['name']):
				response = requests.post(self.executeAction, json=predict)
				if(response.status_code == requests.codes.ok):
					messages = response.json()['messages']
					if(len(messages) > 0):
						if self.lang == 'en':
							botRes, lang = self.translate(messages[0]['text']), self.lang
						elif self.lang == 'vi':
							predict['name'] = re.sub("_\d+", "", predict['name'])
							botRes, lang = ("rasa/" + predict['name'] + "_", self.lang)
			elif predict['name'] == "action_listen":
				requests.post(self.executeAction, json=self.listen())
				break
			elif re.match("action_.*", predict['name']):
				requests.post(self.executeAction, json=predict)
		return botRes, lang
