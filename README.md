## Centralized Domain List Manager

This solution automates the process of creating and updating a common domain list for Network Firewall and Route 53 Resolver DNS Firewall. 

Here is an overview of how the solution works:

1. Deploy the CloudFormation Template found in our GitHub repository.  

2. Upload a file to the S3 bucket created by CloudFormation. This file is a domain list that you manage with one unique domain per row.  

3. After a domain list is uploaded, an S3 Event invokes the Lambda function which manages rules, rule groups, and domain lists.  
    - For DNS Firewall, the Lambda function pulls the domain list from Amazon S3 and updates a DNS Firewall Domain List.  
    - For Amazon Network Firewall, the Lambda function pulls the domain list from Amazon S3 and updates the firewall rule.  

### Launching the CloudFormation stack

To begin, launch the CloudFormation stack.  

1.  Go to AWS CloudFormation in the AWS Management Console.  
  
2.  Choose Create Stack and select “With new resources” (standard).  

3.   On the Create Stack page, under Specify template, select the Upload a template file template source.  

4.  Select Choose file and find the template that you downloaded in the Prerequisites steps.  

5.  Choose Next to continue.  

6.  On the Specify Stack Details page, give your stack a name, such as “MyStackName”.  

7.  Under Parameters, review the default parameters and enter the required: BUCKETNAME, R53_RULE_TYPE, ANFW_RULE_TYPE, ANFW_RULE_GROUP_CAPACITY.  

When deploying CloudFormation, select whether the configured domain lists will allow or deny traffic for both Network Firewall and DNS Firewall.  

There are several parameters for the CloudFormation stack:  
 - BucketName – The name of the S3 Bucket to create. This S3 bucket is where domain lists are uploaded and processed by the solution.
 - R53RuleType – This is the type of DNS Firewall rule action applied to the domain list.   This must be of the type ALLOW, DENY, or ALERT. For a DENY action, the solution defaults to returning NODATA and is not configurable.
 - ANFWRuleType – This is the type of stateful firewall rule action that is applied to the domain list. It must be of type ALLOWLIST or DENYLIST.  
 -   ANFWRuleGroupCapacity – This is the capacity defined for Amazon Network Firewall Rule groups. This can’t be changed after creation. Refer here to calculate capacity units.
 - ANFWRuleOrdering - This is the type of rule ordering that Network Firewall rule groups are deployed and updated with. The solution defaults to STRICT_ORDER but also supports DEFAULT_ACTION_ORDER
 - DomainListName - This is the name of a domain list that is the solution will deploy. Defaults to "managed-domain-list"
 - RuleGroupName - This is the name of the rule groups deployed for both Network Firewall and Route 53 Resolver DNS Firewall. Defaults to "domain-list-rule-group"
 - DNSDomainListPriority - This sets the priority for the DNS Domain list deployed by the solution. This defaults to 1.
 - NetworkFirewallDefaultDomain - This is the default domain name used in the Network Firewall domain list. This is required because a Network Firewall rule cannot contain an empty domain list. This default domain is updated the first time a new domain list is applied via the solution. Defaults to example.com

8. On the Configure stack options page, you can choose to add tags, choose additional options, or just choose Next.  

9. On the Review page, validate your parameters and acknowledge that IAM resources will be created.  Finally, select Create stack.  

10. Once you select Create stack, you can follow the process and view the status of the deployment via the Events tab of the CloudFormation stack. 

Note : The solution does not associate Route 53 Resolver DNS firewall rules with VPCs or Network Firewall Rule Groups with Firewall policies, this must be done outside of the solution itself.


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

