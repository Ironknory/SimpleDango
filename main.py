import json
import os
import random
import requests
import configparser
from hashlib import md5

CONFIG_FILE = 'config.ini'
TARGET_FILE = 'lang.png'

def get_md5(string, encoding='utf-8'):
	return md5(string.encode(encoding)).hexdigest()

def get_file_md5(file_name):
	with open(file_name, "rb") as file:
		return md5(file.read()).hexdigest()


if __name__ == "__main__":
	config = configparser.ConfigParser()
	config.read(CONFIG_FILE)

	# common setting
	url = 'https://fanyi-api.baidu.com/api/trans/sdk/picture'
	app_id, app_key = config['common']['appid'], config['common']['appkey']
	from_lang, to_lang = config['common']['from_lang'], config['common']['to_lang']
	cuid, mac = 'APICUID', 'mac'

	salt = random.randint(32768, 65536)
	sign = get_md5(app_id + get_file_md5(TARGET_FILE) + str(salt) + cuid + mac + app_key)

	payload = {'from': from_lang, 'to': to_lang, 'appid': app_id, 'salt': salt, 'sign': sign, 'cuid': cuid, 'mac': mac}
	image = {'image': (os.path.basename(TARGET_FILE), open(TARGET_FILE, 'rb'), "multipart/form-data")}

	try:
		response = requests.post(url, params=payload, files=image)
		result = response.json()
		if int(result['error_code']) != 0:
			raise Exception(result['error_msg'])
	except Exception as errinfo:
		print(errinfo)
	else:
		result = result['data']['content'][0]
		print(result['dst'])
