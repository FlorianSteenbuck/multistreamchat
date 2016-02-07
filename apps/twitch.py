import json
import socket
import requests
import datetime
import time

from apps import twitch_conf
twitch = twitch_conf

appid = twitch.appid
nick = twitch.nick
channel = twitch.channel
oauth = twitch.oauth
msgs = []
follows = []
internal_id = 0
irc = None

def TimestampMillisec64():
	return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

def delete_msg(msg):
	global irc
	global channel
	if irc != None:
		irc.send(bytes('PRIVMSG #'+channel+' .timeout '+msg["user"]["uid"]+' 1\r\n','utf-8'))

def send_msg(text,to=None):
	global irc
	global channel
	if irc != None:
		if to != None:
			irc.send(bytes('PRIVMSG @'+to+' :'+text))
		else:
			irc.send(bytes('PRIVMSG #'+channel+' :'+text))

def get_param(tags,key):
	tags = tags.split(";")
	if isinstance(key,int):
		return tags[key].split("=")[1]
	else:
		toreturn = ""
		for tag in tags:
			tag = tag.split("=")
			if tag[0] == key:
				toreturn = tag[1]
				break
		return toreturn

def get_user_role(tags,name,channel):
	global follows
	status = "normal"
	if len(tags.split(";")) > 1:
		if get_param(tags,"subscriber") == "1":
			status = "sub"
		if name in follows:
			status = "follow"
		if get_param(tags,"mod") == "1":
			status = "mod"
		if name == channel:
			status = "own"
		if get_param(tags,"user-type") == "staff " or get_param(tags,"user-type") == "admin ":
			status = "staff"
		if get_param(tags,"user-type") == "global_mod ":
			status = "ambas"
		if name == "twitchnotify":
			status = "system"
	return status

def run_follower_collector():
	global follows
	pageurl = None
	while True:
		if pageurl != None:
			r_follows = requests.get(pageurl)
		else:
			r_follows = requests.get("https://api.twitch.tv/kraken/channels/alsob2016/follows")
		jso_follows = r_follows.text
		jso_follows = json.loads(jso_follows)
		pageurl = jso_follows["_links"]["next"]
		jso_follows = jso_follows["follows"]
		for follow in jso_follows:
			if follow["user"]["name"] not in follows:
				follows.append(follow["user"]["name"])
		time.sleep(1)

def run_msgs_collector():
	global msgs
	global nick
	global channel
	global oauth
	global internal_id
	global irc
	irc = socket.socket()
	irc.connect(("irc.twitch.tv", 6667))
	irc.send(bytes('PASS '+oauth+'\r\n','utf-8'))
	irc.send(bytes('USER '+nick+"\r\n",'utf-8'))
	irc.send(bytes('NICK '+nick+"\r\n",'utf-8'))
	irc.send(bytes('JOIN #'+channel+"\r\n",'utf-8'))
	n = 0
	while True:
		data = irc.recv(4096)
		data = data.decode('utf-8')
		if n == 1:
			irc.send(bytes('CAP REQ :twitch.tv/tags\r\n','utf-8'))
		if data[0:4] == "PING":
			irc.send(bytes(data,'utf-8'))
		else:
			argsfromnamefromtext = data.split(" ")
			if len(argsfromnamefromtext) >= 3:
				tags = argsfromnamefromtext[0]
				args = data[len(tags)+2:].split(":")
				if len(args) >= 2:
					text = data[len(args[0])+len(tags)+3:].replace('\ACTION\g',"\r")[:-2]
					args = args[0].split(" ")
					if len(args) >= 3:
						if args[1] == "PRIVMSG":
							if args[2] == "#"+channel:
								name = args[0].split("@")[0].split("!")[1]
								status = "normal"
								status = get_user_role(tags,name,channel)
								ntime = TimestampMillisec64()
								msgs.append({"inid":internal_id,"time":ntime,"user":{"status":status,"name":name,"uid":name},"msg":text})
								if status == "system":
									print("["+str(ntime)+"] [twitch] "+text)
								else:
									print("["+str(ntime)+"] [twitch]["+status+"] ["+name+"]"+name+": "+text)
								internal_id+=1
		n+=1
