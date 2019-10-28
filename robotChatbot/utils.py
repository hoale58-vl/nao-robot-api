import requests
import re

class BotApi:
	def __init__(self, id_user, ip="127.0.0.1", port=80):
		self.url = "http://{}:{}/webhooks/multilang/chat".format(ip, str(port))
		self.id_user = str(id_user)

	def askBot(self, msg):
		response = requests.post(self.url, json={"message":msg, "sender":self.id_user})
		print(response.status_code, self.url, response.json(), self.id_user)
		if(response.status_code == requests.codes.ok):
			return response.json()['result']
		return None
		
