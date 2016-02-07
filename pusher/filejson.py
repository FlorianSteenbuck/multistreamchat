import json

from pusher import filejson_conf
filejson = filejson_conf

def run_pusher(msgs):
	chatfile = open(filejson.chatfile,"w")
	chatfile.write(json.dumps(msgs))
	chatfile.close()