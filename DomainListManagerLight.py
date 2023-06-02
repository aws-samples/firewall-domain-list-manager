import sys
import os
import boto3
import re
import logging

s3 = boto3.client('s3')
r53_client = boto3.client('route53resolver')
anfw_client = boto3.client('network-firewall')

managed_rule_group_name = str(os.environ['RULE_GROUP_NAME'])
anfw_rule_group_require_capacity = int(os.environ['ANFW_RULE_GROUP_CAPACITY'])
anfw_rule_type = os.environ['ANFW_RULE_TYPE']
r53_rule_type = os.environ['R53_RULE_TYPE']
managed_domain_list_name = str(os.environ['DOMAIN_LIST_NAME'])
r53_domain_list_id = str(os.environ['DOMAIN_LIST_ID'])
domain_regex="(?:[*.a-z0-9](?:[a-z_0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]"
rule_order = os.environ['RULE_ORDER']


def get_list_file(event):
    try:
        invalidcount=0
        validcount=0
        p=re.compile(domain_regex)
        fileobj = s3.get_object(
        Bucket=event['Records'][0]['s3']['bucket']['name'],
        Key=event['Records'][0]['s3']['object']['key']
        )
        filedata = fileobj['Body'].read()
        contents = filedata.decode('utf-8')
        domains=contents.split()
        lower_domains=[]
        for domain in domains:
            if domain.startswith("*."):
                if p.search(domain.lstrip("*.")):
                    lower_domains.append(domain.lower())
                    validcount = validcount + 1
            elif domain.startswith("."):
                invalidcount = invalidcount + 1
                print("Incorrect use of wildcard. Wildcarded domains must start with *. " + domain + " has been excluded")
            elif p.fullmatch(domain):
                lower_domains.append(domain.lower())
                validcount = validcount + 1
            else:
                invalidcount=invalidcount + 1
                print("The domain "+domain+" is not a properly formed domain name. It has been excluded")
        return lower_domains,validcount,invalidcount
    except Exception as e: 
            logging.exception('caught exception' + print(e))

# GET LIST OF ROUTE 53 RESOLVER FIREWALL DOMAINS
def pull_domain_list():
    try:
        list = {}
        paginator = r53_client.get_paginator('list_firewall_domain_lists')
        for page in paginator.paginate():
            list.update(page)
        return list
    except Exception as e: 
            logging.exception('caught exception' + print(e))    

def get_r53_domains(r53_domain_list_id):
    try:
        domainlist=[]
        paginator=r53_client.get_paginator('list_firewall_domains')
        for page in paginator.paginate(FirewallDomainListId=r53_domain_list_id):
            domainlist.append(page)
        if domainlist[0]['Domains'] is not None:
            domainlist=list(set(domainlist[0]['Domains']))
            domainlist = [ s.rstrip(".") for s in domainlist ]
        return domainlist
    except Exception as e:
            logging.exception('caught exception' + print(e))    

def merge_r53_domain_lists(existing_domains, update_domains):
    try:
        removelist=[]
        addlist=[]

        # If update_domains is empty, it will result in empty list which breaks ANFW
        if len(update_domains) != 0:
            #Populating the addlist based on diff from existing
            addlist=set(update_domains).difference(set(existing_domains))
            addlist=list(addlist)
            #Populating the removelist based on diff from existing
            removelist=set(existing_domains).difference(set(update_domains))
            removelist=list(removelist)
            # If removelist and addlist is empty because update_domains matches existing_domains then return -1
            if len(removelist) == 0 and len(addlist) == 0:
                return(-1)
            else:
                return addlist, removelist
        else:
            return(-1)
            
    except Exception as e:
            logging.exception('caught exception' + print(e))    
    
def update_r53_resolver_fw_domain_list(addlist,removelist):
    #operation = 'REPLACE' #replace the list the first time

    try:
        if len(addlist) > 0:
            operation='ADD'
            for i in range(0, len(addlist), 1000):
                response = r53_client.update_firewall_domains(
                    FirewallDomainListId=r53_domain_list_id,
                    Operation=operation,
                    Domains=addlist[i:i+1000]
                )
        if len(removelist) > 0:
            operation='REMOVE'
            for i in range(0, len(removelist), 1000):
                response = r53_client.update_firewall_domains(
                    FirewallDomainListId=r53_domain_list_id,
                    Operation=operation,
                    Domains=removelist[i:i+1000]
                )
    except Exception as e: 
            logging.exception('caught exception' + print(e))
            
# Get update token for rule group updates
def get_rule_group_update_token(anfw_rule_group_name):
    try:
        response = anfw_client.describe_rule_group(RuleGroupName=anfw_rule_group_name, Type='STATEFUL')
        return response['UpdateToken']
    except Exception as e: 
            logging.exception('caught exception' + print(e))

def get_anfw_domain_list(anfw_rule_group_name):
    anfw_domain_list=[]
    response = anfw_client.describe_rule_group(RuleGroupName=anfw_rule_group_name,Type='STATEFUL')
    anfw_domain_list=response['RuleGroup']['RulesSource']['RulesSourceList']['Targets']
    return anfw_domain_list
    
# Update the ANFW rule group
def update_anfw_rule_group(update_token,anfw_rule_group_name,domains,rule_type):
    try:
        anfw_domains=[]
        if len(domains) > 0:
            for domain in domains:
                anfw_domains.append(domain.lstrip("*"))
            response = anfw_client.update_rule_group(UpdateToken=update_token,RuleGroupName=anfw_rule_group_name,Type='STATEFUL',
            RuleGroup = {
            'RuleVariables': {
                'IPSets': {
                    "HOME_NET": {
                        'Definition': [
                            "0.0.0.0/0"
                        ]
                    }
                }
            },
            'RulesSource': {
                'RulesSourceList': {
                    'Targets': anfw_domains,'TargetTypes': [
                        "HTTP_HOST",
                        "TLS_SNI"
                    ],
                    'GeneratedRulesType': anfw_rule_type
                }
            },
            "StatefulRuleOptions": {
                "RuleOrder": rule_order
                }
         }
         )
    except Exception as e: 
            logging.exception('caught exception' + print(e))

def lambda_handler(event,context):
    try:
        domainlist=()
        domainlist=get_list_file(event)
        domains = domainlist[0]
        diff=[]
        
        print(domains)
        
        ## Testing the merge functionality
        currentdomains=get_r53_domains(r53_domain_list_id)
        addremovelist=merge_r53_domain_lists(currentdomains,domains)
        
        # stripping the trailing . and leading * so we can compare to the netfw domain lists
        currentdomains = [ s.rstrip(".") for s in currentdomains ]
        
        anfw_domains = get_anfw_domain_list(managed_rule_group_name)
        anfw_domains = [ s.lstrip("*") for s in anfw_domains ]
        
        # Don't do anything if we're removing all domains or the current and new list is the same.
        if addremovelist != -1:
            # Don't do anything if the lists are out of sync.
            if set(anfw_domains) == set(currentdomains):
                addlist=addremovelist[0]
                removelist=addremovelist[1]
                
                if addlist is not None:
                    print("Adding domains: "+str(addlist))
                if removelist is not None:
                    print("Removing domains: "+ str(removelist))
                
                # Updating list via add/remove
                update_r53_resolver_fw_domain_list(addlist,removelist)
            
                update_token=get_rule_group_update_token(managed_rule_group_name)
                update_anfw_rule_group(update_token,managed_rule_group_name,domains,anfw_rule_type)
                print("Done! " + str(domainlist[1]) + " valid domains were processed " + str(domainlist[2]) + " Invalid domains were discarded")
            else:
                print("There was a problem! The R53 and Network Firewall Domain Lists may be out of sync. Fix them manually or re-deploy")
        else:
            print("The current domain list is either the same as what is deployed or will remove all domains, this is not currently supported. Please update the list and try again.")

        return None
        
    except Exception as e: 
            logging.exception('caught exception' + print(e))