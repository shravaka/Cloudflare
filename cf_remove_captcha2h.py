#!/bin/python

#######################################################
### Remove captcha rules after 2h, based on keyword####
#######################################################


import CloudFlare
import time
import json
import datetime

priv_key = ""
email = ""
rule_list = []
now = datetime.datetime.utcnow()
#path to store logs
log_path = ""
#path to external file with list of Cf organizations
org_list = ""
epochtime = str(time.time())

#Chek if the rule has been created more than 2h ago
def calc_tdelta(rule_timestamp):
    then = datetime.datetime.strptime(rule_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    t_delta = (now - then).seconds
    if t_delta > 7200:
        return "delete"
    else:
        return "remain"

#Cf authentication
def cf_auth():
    cf = CloudFlare.CloudFlare(email=email, token=priv_key, raw=True)
    return cf

# Read organization IDs from the file
def org_read():
    org_ids = []
    f = open(org_list,"r")
    lines = f.readlines()
    for i in lines:
        org_ids.append(i.split()[0])
    return org_ids

#Get rule pages count:
def get_no_of_pages(cf, organization):
#### keyword defined in the notes field
    response = cf.organizations.firewall.access_rules.rules(organization, params={"per_page":100, "notes":""})
    no_of_pages = response["result_info"]["total_pages"]
    return no_of_pages

#Create list of existing rules
def load_rules(cf, organization, no_of_pages):
    for i in range(1,no_of_pages+1):
#### keyword defined in the notes field
        res = cf.organizations.firewall.access_rules.rules(organization, params= {"per_page":100, "notes":"", "page":i})
        rule_list.append(res["result"])
    return rule_list


#remove rules that are less thatn 2h old
def rule_filter(rule_list):
    rule_list_delete = []
    for i in range (0, len(rule_list)):
        for j in range (0, len(rule_list[i])):
            checker = calc_tdelta(rule_list[i][j]['modified_on'])
            if checker == "delete":
                entity = {"target":rule_list[i][j]["configuration"]["target"],
"address":rule_list[i][j]["configuration"]["value"],
"notes":rule_list[i][j]["notes"],
"created":rule_list[i][j]["created_on"],
"mode":rule_list[i][j]["mode"],
"id":rule_list[i][j]["id"]}
                rule_list_delete.append(entity)
            else:
                pass
    return rule_list_delete

#Rule deletion + log file update
def delete_rules(cf, organization, rule_list):
    for i in range(0, len(rule_list)):
        rule = rule_list[i]["id"]
        delete = cf.organizations.firewall.access_rules.rules.delete(organization, rule)
        rule_list[i].update({"status":"Rule removed"})
    return rule_list

#save log file
def save_to_file(rule_list):
    if rule_list:
        with open ("%sremoved_captha.log+%s" % (log_path,epochtime), 'a' ) as f:
            f.write('\n'.join(json.dumps(obj) for obj in rule_list))
    else:
        exit()

def main():
    cf = cf_auth()
    orgs = org_read()
    for i in orgs:
        no_of_pages = get_no_of_pages(cf, i)
        rule_list = load_rules(cf,i, no_of_pages)
        rules_to_delete = rule_filter(rule_list)
        deleted = delete_rules(cf, i, rules_to_delete)
        save_to_file(deleted)
   
if __name__=="__main__":
	main()

