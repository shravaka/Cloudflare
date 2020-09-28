#!/usr/bin/python

import os
import datetime

#path where the script is stored, used for feeding zone IDs
script_path = ""
#target log path
logs_path = ""
#error log
errfile = ""

#function gets previous day's date by substracting 6h from current date. The idea is to have this script running at 2-3 am.
#returns an tuple array with 1h intervals that cover the whole day
def get_timestamps():
    timestamps = []
    format = "%Y-%m-%d"
    #the 6h substraction can be edited in the below line
    yesterday = (datetime.datetime.utcnow()-datetime.timedelta(hours=6)).strftime(format)
    today = datetime.datetime.utcnow().strftime(format)
    a=["%02d" % x for x in range(23)]
    for i in a:
        st = (str(yesterday)+"T"+str(i)+":00:00Z")
        stp =  (str(yesterday)+"T"+str("%02d"%(int(i)+01))+":00:00Z")
        timestamps.append((st, stp))
    timestamps.append(("%sT23:00:00Z" %str(yesterday),"%sT00:00:00Z" % str(today))) 
    return timestamps

#read zone IDs from the file
def get_zones():
    try:
       f = open("%s/zones.txt" % (script_path),"r")
       lines = f.readlines()
       return lines
    except Exception as e:
       with open (errfile, 'a') as err:
          now = datetime.datetime.now()
          err.write("%s - Zone file read error: %s\n" %(now, e))


#get logs from Cf
def get_logs(zone,start,finish):
    # Define what fields should be downloaded (list of fields available on Cf pages)
    what=""
    request = ('curl --compressed -s -X GET "https://api.cloudflare.com/client/v4/zones/%s/logs/received?start=%s&end=%s&fields=%s&timestamps=unix" -H "Content-Type:application/json" -H "X-Auth-Key:xxx" -H "X-Auth-Email:xxx" ' % (zone, start, finish, what))
    try:
        logs = os.popen(request).read()
        return logs
    except Exception as e:
        with open(errfile, 'a') as err:
            now = datetime.datetime.now()
            err.write("%s - Cf API error: %s\n" %(now, e))

#save logs to files:
def save_to_file(logs, zone_name, timestamp):
    filename = '%s/%s.log+%s' % (logs_path, zone_name, timestamp)
    try:
        with open(filename, 'w+') as logfile:
            logfile.write(logs)
    except Exception as e:
        with open (errfile, 'a') as err:
            now = datetime.datetime.now()
            err.write("%s - Error while saving to file: %s\n" % (now, e))

#start
def main():
     timestamps = get_timestamps()
     zones = get_zones()
     for x in zones:
        zone = x.split(' ')[0]
        zone_name = x.split(' ')[1].strip('\n')
        for i in timestamps:
	    logs = get_logs(zone,i[0],i[1])
            save_to_file(logs, zone_name,i[0] )

if __name__=="__main__":
	main()
