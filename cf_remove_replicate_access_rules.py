#!/bin/python

###################################################
## Replicate Access rules across the zones ########
###################################################

import CloudFlare
import os
import json
import sys

priv_key = ""
email = ""
#soure zone
source = "" 
#target zones:
org_list = ""
keyword = str(sys.argv[1])



# Cf authentication
def cf_auth():
    cf = CloudFlare.CloudFlare(email=email, token=priv_key, raw=True)
    return cf

#Count of rule pages:
def get_no_of_pages(cf):
    response = cf.zones.firewall.access_rules.rules(source, params={"per_page":100 })
    no_of_pages = response["result_info"]["total_pages"]
    return no_of_pages

#create list of rules existing in source zone
def load_rules(cf, no_of_pages):
    access_rules = []
    for i in range(1,no_of_pages+1):
        res = cf.zones.firewall.access_rules.rules(source, params= {"per_page":100, "page":i})
	for j in range(0,len(res["result"])):
	    access_rules.append(tuple([res["result"][j]["configuration"]["value"], res["result"][j]["notes"]]))
    return access_rules

# Read target zone IDs
def org_read():
    org_ids = []
    f = open(org_list,"r")
    lines = f.readlines()
    for i in lines:
        org_ids.append(i.split()[0])
    return org_ids


#captcha requests
def cf_captcha(cf, organization,rules):
    for i in rules:
        try:
            block_request = cf.organizations.firewall.access_rules.rules.post(organization, data={"mode":"challenge", "configuration":{"target":"ip", "value":i[0]}, "notes":i[1]})
            print "Rule added. Details:" + str(block_request["result"]["configuration"]["value"])+" "+str(block_request["result"]["notes"])
            print "Zone ID: "+str(block_request["result"]["scope"]["id"])
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            global error_msg
            error_msg = "Cloudflare API error: %d %s " % (e,e)
            print error_msg


def main():
    orgs = org_read()
    cf = cf_auth()
    no_of_pages = get_no_of_pages(cf)
    rules = load_rules(cf, no_of_pages)
    for i in orgs:
        cf_captcha(cf, i, rules)

if __name__=="__main__":
	main()
