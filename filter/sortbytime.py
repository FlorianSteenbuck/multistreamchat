from filter import sortbytime_conf
sortbytime = sortbytime_conf

def extract_time(json):
	try:
		return int(json['time'])
	except KeyError:
		return 0

def run_filter(msgs):
	msgs.sort(key=extract_time, reverse=sortbytime.reverse)
	return msgs