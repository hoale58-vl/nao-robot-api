import requests
import re
import logging

class BotApi:
	def __init__(self, id_user, ip="127.0.0.1", port=80):
		self.url = "http://{}:{}/webhooks/multilang/chat".format(ip, str(port))
		self.id_user = str(id_user)

	def askBot(self, msg):
		response = requests.post(self.url, json={"message":msg, "sender":self.id_user})
		logging.debug("Status: {}, Response: {}, User: {}".format(response.status_code, str(response.json()), self.id_user))
		if(response.status_code == requests.codes.ok):
			return response.json()['result']
		return None
		
