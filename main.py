import os
import cv2
import time
import numpy
import random
import requests
import configparser
from hashlib import md5
from PIL import ImageGrab

CONFIG_FILE = 'config.ini'
TARGET_FILE = 'lang.png'

def getMd5(string, encoding='utf-8'):
	return md5(string.encode(encoding)).hexdigest()

def getFileMd5(file_name):
	with open(file_name, "rb") as file:
		return md5(file.read()).hexdigest()

def getZone():
	img = numpy.array(ImageGrab.grab())
	zone = cv2.selectROI('roi', img, False, False)
	cv2.destroyWindow('roi')
	return zone[0], zone[1], zone[0] + zone[2], zone[1] + zone[3]

def capture(zone):
	return numpy.array(ImageGrab.grab(bbox=(zone[0], zone[1], zone[2], zone[3])))

def getMse(img1, img2):
	err = numpy.sum((img1.astype("float") - img2.astype("float")) ** 2)
	return err / float(img1.shape[0] * img1.shape[1])


if __name__ == "__main__":
	config = configparser.ConfigParser()
	config.read(CONFIG_FILE)

	# common setting
	url = 'https://fanyi-api.baidu.com/api/trans/sdk/picture'
	app_id, app_key = config['common']['appid'], config['common']['appkey']
	from_lang, to_lang = config['common']['from_lang'], config['common']['to_lang']
	cuid, mac = 'APICUID', 'mac'

	zone = getZone()
	old_img = capture(zone)
	while True:
		time.sleep(0.5)
		img = capture(zone)
		if getMse(old_img, img) < 0.1:
			continue
		try:
			old_img = img
			cv2.imwrite(TARGET_FILE, img)

			salt = random.randint(32768, 65536)
			sign = getMd5(app_id + getFileMd5(TARGET_FILE) + str(salt) + cuid + mac + app_key)
			payload = {'from': from_lang, 'to': to_lang, 'appid': app_id, 'salt': salt, 'sign': sign, 'cuid': cuid, 'mac': mac}
			image = {'image': (os.path.basename(TARGET_FILE), open(TARGET_FILE, 'rb'), "multipart/form-data")}

			result = requests.post(url, params=payload, files=image).json()
			os.system('cls')
			if int(result['error_code']) != 0:
				raise Exception(result['error_msg'])
		except Exception as errinfo:
			print(errinfo)
		else:
			result = result['data']['content'][0]
			print(result['dst'])
