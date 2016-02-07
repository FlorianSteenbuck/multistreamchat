import requests
import json
import time
import datetime

from apps import beampro_conf
beampro = beampro_conf

appid = beampro.appid
channelid = beampro.channelid
userroles = {
	"Admin":{
		"priority":5,
		"name":"staff"
	},
	"Owner":{
		"priority":4,
		"name":"own"
	},
	"Mod":{
		"priority":3,
		"name":"mod"
	},
	"Subscriber":{
		"priority":2,
		"name":"sub"
	},
	"Pro":{
		"priority":1,
		"name":"normal"
	},
	"User":{
		"priority":0,
		"name":"normal"
	}
}
msgs = []

def TimestampMillisec64():
	return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000) 

def get_status(user_roles):
	global userroles
	maxprio = 0
	userrolename = "normal"
	for userrole in user_roles:
		if userroles[userrole] != None:
			if userroles[userrole]["priority"] > maxprio:
				maxprio = userroles[userrole]["priority"]
				userrolename = userroles[userrole]["name"]
	return userrolename

def get_msg_in_text(msg):
	thereturn = ""
	for obj in msg:
		if obj["type"] == "text":
			thereturn += obj["data"]
		elif obj["type"] == "emoticon":
			thereturn += obj["text"]
		elif obj["type"] == "link":
			thereturn += obj["text"]
		else:
			if "text" in obj:
				thereturn += obj["text"]
	return thereturn

def run_msgs_collector():
	global msgs
	global internal_id
	global channelid
	timest = TimestampMillisec64()
	while(True):
		msgs_r = requests.get("https://beam.pro/api/v1/chats/"+channelid+"/message?start="+str(timest))
		msgs_r = json.loads(msgs_r.text)
		for nmsg in msgs_r:
			name = nmsg["user_name"]
			nin = nmsg["id"]
			uid = str(nmsg["user_id"])
			timest = TimestampMillisec64()
			msgs.append({"inid":nin,"time":timest,"user":{"status":get_status(nmsg["user_roles"]),"name":name,"uid":uid},"msg":get_msg_in_text(nmsg["message"]["message"])})				
			print("["+str(timest)+"] [beampro]["+get_status(nmsg["user_roles"])+"] ["+uid+"]"+name+": "+get_msg_in_text(nmsg["message"]["message"]))
