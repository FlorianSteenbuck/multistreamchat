from websocket import create_connection
import requests
import json

from apps import hitbox_conf
hitbox = hitbox_conf

appid = hitbox.appid
channel = hitbox.channel
user = hitbox.user
token = hitbox.token
internal_id = 0
msgs = []
ws = None

def send_msg(text,to=None):
	global ws
	global channel
	global user
	global token
	if ws != None:
		if to != None:
			ws.send("5:::"+json.dumps({"name":"message","args":[{"method":"directMsg","params":{"channel":channel,"from":user,"to":to,"token":token,"text":text}}]}))
		else:
			ws.send("5:::"+json.dumps({"name":"message","args":[{"method":"chatMsg","params":{"channel":channel,"name":user,"text":text}}]}))

def delete_msg(msg):
	global ws
	global channel
	global token
	if ws != None:
		ws.send("5:::"+json.dumps({"name":"message","args":[{"method":"kickUser","params":{"channel":channel,"name":msg["user"]["uid"],"token":token,"timeout":"1"}}]}))

def get_status(params):
	status = "normal"
	if params["isFollower"]:
		status = "follow"
	if params["isSubscriber"]:
		status = "sub"
	if params["isOwner"]:
		status = "own"
	if params["isStaff"]:
		status = "staff"
	if params["isCommunity"]:
		status = "ambas"
	return status

def run_msgs_collector():
	global msgs
	global internal_id
	global ws
	global user
	global token
	r_servers = requests.get("https://api.hitbox.tv/chat/servers")
	servers = json.loads(r_servers.text)
	server = servers[2]["server_ip"]
	r_websocketid = requests.get("http://"+server+"/socket.io/1/")
	websocketid = (r_websocketid.text).split(":")[0]
	ws = create_connection("ws://"+server+"/socket.io/1/websocket/"+websocketid)
	if ws.recv() == "1::":
		joinchanneljsonstr = (json.dumps({"name":"message","args":[{"method":"joinChannel","params":{"channel":"alsob","name":"UnknownSoldier","token":None,"isAdmin":False}}]}))
		if user != "" and token != "":
			joinchanneljsonstr = (json.dumps({"name":"message","args":[{"method":"joinChannel","params":{"channel":"alsob","name":user,"token":token,"isAdmin":True}}]}))
		ws.send("5:::"+joinchanneljsonstr)
		resp = ws.recv()
		resp = json.loads(resp[4:])
		resp = json.loads(resp["args"][0])
		if resp["method"] == "loginMsg":
			while True:
				resp = ws.recv()
				if resp != "":
					if resp == "2::":
						ws.send(resp)
					else:
						resp = resp[4:]
						msg = json.loads(resp)["args"]
						msg = json.loads(msg[0])
						if msg["method"] == "chatMsg":
							if "buffer" not in msg["params"].keys() and "buffersent" not in msg["params"].keys():
								msgparam = msg["params"]
								ntime = msgparam["time"]*1000
								msgs.append({"inid":internal_id,"time":ntime,"user":{"status":get_status(msgparam),"name":msgparam["name"],"uid":msgparam["name"]},"msg":msgparam["text"]})
								print("["+str(ntime)+"] [hitbox]["+get_status(msgparam)+"] ["+msgparam["name"]+"]"+msgparam["name"]+": "+msgparam["text"])
							elif msg["method"] == "infoMsg":
								msgparam = msg["params"]
								ntime = msgparam["time"]*1000
								msgs.append({"inid":internal_id,"time":ntime,"user":{"status":"system","name":"","uid":"system"},"msg":msgparam["text"]})
								print("["+str(ntime)+"] [hitbox] "+msgparam["text"])
							internal_id+=1
	ws.close()
