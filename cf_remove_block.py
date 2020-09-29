#!/bin/python

#########################################################
#### Script to remove all Cf blocks for a given zone ####

import CloudFlare
import time
import json

priv_key = ""
email = ""
zone = ""
rule_list = []
log_path = ""

#Cf authentication
def cf_auth():
    cf = CloudFlare.CloudFlare(email=email, token=priv_key, raw=True)
    return cf

#get first page with rulles
def get_first_rules(cf):
    rules = cf.zones.firewall.access_rules.rules(zone, params={'per_page':1000, "notes":"", "mode":"block"})
    num_of_rules = rules["result_info"]["count"]
    num_of_pages = rules["result_info"]["total_pages"]
    rules_total = rules["result_info"]["total_count"]
    for i in range(num_of_rules):
        entity = {"target":rules["result"][i]["configuration"]["target"],
"country":rules["result"][i]["configuration"]["value"],
"notes":rules["result"][i]["notes"],
"created":rules["result"][i]["created_on"],
"mode":rules["result"][i]["mode"],
"id":rules["result"][i]["id"]} 
        rule_list.append(entity)
    return num_of_pages

#get remaining prages with rules
def get_remaining_rules(cf,num_of_pages):
    for i in range(2,num_of_pages+1):
        rules = cf.zones.firewall.access_rules.rules(zone, params={'per_page':1000, "notes":"", "mode":"block", "page":i})
        num_of_rules = rules["result_info"]["count"]
        for j in range (num_of_rules):
            entity = {"target":rules["result"][i]["configuration"]["target"],
"country":rules["result"][i]["configuration"]["value"],
"notes":rules["result"][i]["notes"],
"created":rules["result"][i]["created_on"],
"mode":rules["result"][i]["mode"],
"id":rules["result"][i]["id"]} 
        rule_list.append(entity)
 

#remove block rules
def delete_rules(cf):
    for i in range(len(rule_list)):
        rule = rule_list[i]["id"]
        del_rule = cf.organizations.firewall.access_rules.rules.delete(organization, rule)
        rule_list[i].update({"status":"Rule removed"})
        time.sleep(0.1)

#save logs to file
def save_to_file():
    if rule_list:
        with open ("%sblock-remove.log" % log_path,'a' ) as f:
            f.write('\n'.join(json.dumps(obj) for obj in rule_list))
    else:
        exit()

def main():
    cf = cf_auth()
    num_of_pages = get_first_rules(cf)
    if num_of_pages != 1:
        get_remaining_rules(cf,num_of_pages)
    delete_rules(cf)
    save_to_file()
   
if __name__=="__main__":
	main()

