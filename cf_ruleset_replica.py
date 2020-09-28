#!/bin/bash

###################################################
##### Replicate WAF settings across the zones #####
###################################################

import CloudFlare
import os
import json

priv_key = ""
email = ""
#id of the source zone
source = "" 
#external file with list of target zones
zones_file = "zones.txt"
#external files with IDs of ruleset to replicate 
ruleset_file = "rulesets.txt"

#load zones, returns zone IDs
def load_data(z):
    f = open(z,"r")
    return f.read().splitlines()

#
def replicate_rules(zone, ruleset):
    cf = CloudFlare.CloudFlare(email=email, token=priv_key, raw=True)
    for i in range (1,26):
         rules = cf.zones.firewall.waf.packages.rules(source,ruleset, params={"per_page":100, "page":i}) 
         for x in rules["result"]:
             print "Rule ", x["description"], "status:", x["mode"], "for zone: ", zone 
             os.system('curl -X PATCH "https://api.cloudflare.com/client/v4/zones/%s/firewall/waf/packages/%s/rules/%s" -H "X-Auth-Email: %s" -H "X-Auth-Key: %s" -H "Content-Type: application/json" --data \'{"mode":"%s"}\'' % (zone,ruleset, x["id"], email, priv_key, x["mode"]))

def replicate_groups(zone,ruleset):
    cf = CloudFlare.CloudFlare(email=email, token=priv_key, raw=True)
    groups = cf.zones.firewall.waf.packages.groups.get(source, ruleset)
    for x in groups["result"]:
        print x["id"], x["mode"]
        print "Zestaw regul:", x["name"],"status", x["mode"], "dla zony: ", zone 
        os.system('curl -X PATCH "https://api.cloudflare.com/client/v4/zones/%s/firewall/waf/packages/%s/groups/%s" -H "X-Auth-Email: %s" -H "X-Auth-Key: %s" -H "Content-Type: application/json" --data \'{"mode":"%s"}\'' % (zone, ruleset, x["id"], email, priv_key, x["mode"]))


def main ():
  zones = load_data(zones_file)
  rulesets = load_data(ruleset_file)
  for y in rulesets:
      for i in zones:
           replicate_groups(i, y)
           replicate_rules(i,y )
#start          
if __name__=="__main__":
	main()

