#!/bin/python

########################################
### Get current number of rules ########

import CloudFlare
import datetime

priv_key = ""
email = ""
log_path = ""
org_list = ""
timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Read organization ID:
def org_read():
    org_ids = []
    f = open(org_list,"r")
    lines = f.readlines()
    for i in lines:
        org_ids.append(i)
    return org_ids


#Cf authorization
def cf_auth():
    cf = CloudFlare.CloudFlare(email=email, token=priv_key, raw=True)
    return cf

#get total number of rules for zone:
def get_no_of_rules(cf, organization):
    response = cf.organizations.firewall.access_rules.rules(organization.split(" ")[0])
    with open ("%sno_of_rules_%s.log+%s" % (log_path,organization,timestamp), 'a' ) as f:
        f.write(organization.split(" ")[1].strip('\n')+" "+str(response["result_info"]["total_count"])+"\n")
    
def main():
    cf = cf_auth()
    orgs = org_read()
    for i in orgs:
        get_no_of_rules(cf, i)

if __name__=="__main__":
	main()

