#!/bin/python -W ignore


###############################################################
### Script to remove captchax on the Cf organization level ###
###############################################################

import CloudFlare
import time
import json
import datetime

priv_key = ""
email = ""
ip_list = []
now = datetime.datetime.utcnow()
#path to store logs
log_path = ""
#list of organizations
org_list = ""
epochtime = str(time.time())


#Cf authentication
def cf_auth():
    cf = CloudFlare.CloudFlare(email=email, token=priv_key, raw=True)
    return cf

# Reard organization ID from the file
def org_read():
    org_ids = []
    f = open(org_list,"r")
    lines = f.readlines()
    for i in lines:
        org_ids.append(i)
    return org_ids

#number of rule pages:
def get_no_of_pages(cf, organization, keyword, mode):
    response = cf.organizations.firewall.access_rules.rules(organization.split()[0], params={"per_page":100, "mode":mode, "notes":keyword})
    no_of_pages = response["result_info"]["total_pages"]
    return no_of_pages

#create a full list of existing rules
def load_rules(cf, organization, no_of_pages, keyword, mode):
    for i in range(1,no_of_pages+1):
        res = cf.organizations.firewall.access_rules.rules(organization.split()[0], params= {"per_page":100,"mode":mode, "notes":keyword, "page":i})
        rule_list.append(res["result"])
    return rule_list


#rule deletiond + logs creation
def delete_rules(cf, organization, rule_list):
    for i in range(0, len(rule_list)):
        for j in range(0, len(rule_list[i])):
            rule = rule_list[i][j]["id"]
            ip = rule_list[i][j]["configuration"]["value"]
            ip_list.append(ip[1:-1])
            print "Deleting  "+ip+" "+rule_list[i][j]["notes"]+" for zone: "+organization.split()[1]
            delete = cf.organizations.firewall.access_rules.rules.delete(organization.split()[0], rule)
            print "rule deleted: "+str(delete)
            rule_list[i][j].update({"status":"rule removed"})
            time.sleep(0.2)

#save lgos to file
def save_to_file():
    if rule_list:
        with open ("%sremoved_rules.log+%s" % (log_path,epochtime), 'a' ) as f:
            f.write('\n'.join(json.dumps(obj) for obj in rule_list))
        with open ("%scf_removed_rules.log+%s" % (log_path,epochtime), 'a' ) as f:
            f.write('\n'.join(json.dumps(obj) for obj in ip_list ))
    else:
        exit()

def main():
    print "CAUTION: ALL rules for given organization will be removed, based on selected options"
    print "If you are not sure what you are doing, exit this program now!"
    kword = raw_input("Rule keyword (any word that is included in rule note): ")
    mode = raw_input("Mode (challenge/block): ")
    cf = cf_auth()
    orgs = org_read()
    for i in orgs:
        rule_list = []  
        no_of_pages = get_no_of_pages(cf, i, kword,mode)
        rule_list = load_rules(cf,i, no_of_pages, kword,mode)
        delete_rules(cf, i, rule_list)
   
#start          
if __name__=="__main__":
	main()


