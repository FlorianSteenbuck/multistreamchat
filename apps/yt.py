import requests
import json
import time
import datetime
import dateutil.parser

from apps import yt_conf
yt = yt_conf

appid = yt.appid
livechatid = yt.livechatid
apikey = yt.apikey
ownerchannelid = yt.ownerchannelid
msgs = []
follower = []

def run_msgs_collector():
	global msgs
	global internal_id
	global livechatid
	global apikey
	global ownerchannelid
	global follower
	pagetoken = None
	time2sleep = 1
	alreadyid = []
	while(True):
		if pagetoken != None:
			nmsgs = requests.get("https://www.googleapis.com/youtube/v3/liveChat/messages?liveChatId="+livechatid+"&pagetoken="+pagetoken+"&part=snippet%2Cid&hl=de&key="+apikey)
		else:
			nmsgs = requests.get("https://www.googleapis.com/youtube/v3/liveChat/messages?liveChatId="+livechatid+"&part=snippet%2Cid&hl=de&key="+apikey)
		nmsgs = json.loads(nmsgs.text)
		time2sleep = nmsgs["pollingIntervalMillis"]/1000
		nmsgs = nmsgs["items"]
		for nmsg in nmsgs:
			if nmsg["snippet"]["type"] == "textMessageEvent":
				if not nmsg["id"] in alreadyid:
					alreadyid.append(nmsg["id"])
					status = "normal"
					ntime = int(time.mktime((dateutil.parser.parse(nmsg["snippet"]["publishedAt"])).timetuple())*1000)
					username = "[$#!#!#$]"
					username_r = requests.get("https://www.googleapis.com/youtube/v3/channels?part=snippet&id="+nmsg["snippet"]["authorChannelId"]+"&key="+apikey)
					username_r = json.loads(username_r.text)
					for names in username_r["items"]:
						username = names["snippet"]["title"]
					if nmsg["snippet"]["authorChannelId"] in follower:
						status = "follow"
					if nmsg["snippet"]["authorChannelId"] == ownerchannelid:
						status = "own"
					text = nmsg["snippet"]["displayMessage"]
					msgs.append({"inid":nmsg["id"],"time":ntime,"user":{"status":status,"name":username,"uid":nmsg["snippet"]["authorChannelId"]},"msg":text})
					print("["+str(ntime)+"] [yt]["+status+"] ["+nmsg["snippet"]["authorChannelId"]+"]"+username+": "+text)
		time.sleep(time2sleep)
