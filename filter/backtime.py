from filter import backtime_conf
backtime = backtime_conf

def run_filter(msgs):
	for i in range(len(msgs)-1):
		if i < len(msgs)-1:
			if msgs[i]["time"] < TimestampMillisec64()-conf.backtime:
				msgs.pop(i)
	return msgs