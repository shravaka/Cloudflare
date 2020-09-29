import os
import datetime


#script home path
script_path = ""
#path for saving logs
logs_path = ""
#error log
errfile = ""

#get and format local time for timestamping log file
def get_current_time():
    current = datetime.datetime.now()
    format = "%b-%d-%H:%M:%S"
    timestamp = current.strftime(format)
    return timestamp

#get zones ID from external file:
def get_zones():
    try:
       f = open("%s/zones.txt" % (script_path),"r")
       lines = f.readlines()
       return lines
    except Exception as e:
       with open (errfile, 'a') as err:
          now = datetime.datetime.now()
          err.write("%s - Zone file read error: %s\n" %(now, e))

#get start and finish time, one minute interval
def get_times():
    start = (datetime.datetime.utcnow()-datetime.timedelta(minutes=11)).isoformat("T")[:-9]+"00Z"
    finish = (datetime.datetime.utcnow()-datetime.timedelta(minutes=10)).isoformat("T")[:-9]+"00Z"
    return start, finish


#get Cloudflare logs
def get_logs(zone,start,finish):
    # define required fields
    what="EdgeStartTimestamp,CacheCacheStatus,ClientCountry,ClientIP,ClientRequestHost,ClientRequestMethod,ClientRequestProtocol,ClientRequestURI,ClientRequestUserAgent,EdgeResponseStatus,OriginResponseStatus,ClientSSLProtocol,EdgeResponseBytes,EdgePathingOp,EdgePathingSrc,RayID,ClientRequestReferer,OriginResponseTime,WAFAction,WAFRuleMessage,ClientIPClass,EdgeRateLimitAction,EdgeRateLimitID,OriginIP"
    request = ('curl --compressed -s -X GET "https://api.cloudflare.com/client/v4/zones/%s/logs/received?start=%s&end=%s&fields=%s&timestamps=unix" -H "Content-Type:application/json" -H "X-Auth-Key:xxx" -H "X-Auth-Email:xxx" ' % (zone, start, finish, what))
    try:
        logs = os.popen(request).read()
        return logs
    except Exception as e:
        with open(errfile, 'a') as err:
            now = datetime.datetime.now()
            err.write("%s - Cloudflare API error: %s\n" %(now, e))

#save logs to the file
def save_to_file(logs, zone_name, timestamp):
    filename = '%s/%s.log+%s' % (logs_path, zone_name, timestamp)
    try:
        with open(filename, 'w+') as logfile:
            logfile.write(logs)
    except Exception as e:
        with open (errfile, 'a') as err:
            now = datetime.datetime.now()
            err.write("%s - File save error: %s\n" % (now, e))

def main():
    timestamp = get_current_time()
    times = get_times()
    zones = get_zones()
    for x in zones:
        zone = x.split(' ')[0]
        zone_name = x.split(' ')[1].strip('\n')
	logs = get_logs(zone,times[0],times[1])
        save_to_file(logs, zone_name, timestamp)

if __name__=="__main__":
	main()
