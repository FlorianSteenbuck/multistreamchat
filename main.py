from apps import *
from filter import *
from pusher import *

import json
import time
import operator
import threading
import datetime

msgs = []
lastlength = 0

def TimestampMillisec64():
	return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

def iskeyvaluefromappinmsgs(key,value,appid,msgs):
	thereturn = False
	for msg in msgs:
		if value == msg[key] and msg["app"] == appid:
			thereturn = True
			break
	return thereturn

def mergemsgs(newmsgs,oldmsgs,appid):
	global mid
	for nmsg in newmsgs:
		nmsg["app"] = appid
		if not iskeyvaluefromappinmsgs("inid",nmsg["inid"],appid,oldmsgs):
			oldmsgs.append(nmsg)

def delete_msg(msg):
	if twitch_conf.active:
		twitch.delete_msg(msg)
	if hitbox_conf.active:
		hitbox.delete_msg(msg)

def send_msg(msg):
	if twitch_conf.active:
		twitch.send_msg(msg)
	if hitbox_conf.active:
		hitbox.send_msg(msg)

if yt_conf.active:
	yt_thread = threading.Thread(target = yt.run_msgs_collector, args = [])
	yt_thread.start()

if beampro_conf.active:
	beampro_thread = threading.Thread(target = beampro.run_msgs_collector, args = [])
	beampro_thread.start()

if twitch_conf.active:
	twitch_fol_thread = threading.Thread(target = twitch.run_follower_collector, args = [])
	twitch_fol_thread.start()
	twitch_thread = threading.Thread(target = twitch.run_msgs_collector, args = [])
	twitch_thread.start()

if hitbox_conf.active:
	hitbox_thread = threading.Thread(target = hitbox.run_msgs_collector, args = [])
	hitbox_thread.start()

while(True):
	lastlength = len(msgs)
	#mergemsgs region
	if hitbox_conf.active:
		mergemsgs(hitbox.msgs,msgs,hitbox.appid)
	if twitch_conf.active:
		mergemsgs(twitch.msgs,msgs,twitch.appid)
	if beampro_conf.active:
		mergemsgs(beampro.msgs,msgs,beampro.appid)
	if yt_conf.active:
		mergemsgs(yt.msgs,msgs,yt.appid)
	#filter region
	if sortbytime_conf.active:
		msgs = sortbytime.run_filter(msgs)
	if backtime_conf.active:
		msgs = backtime.run_filter(msgs)
	if lastlength < len(msgs):
		if filejson_conf.active:
			filejson.run_pusher(msgs)
			
