## Centralized Domain List Manager

Here is an overview of how the solution works:

    Deploy the CloudFormation Template found in our GitHub repository.
    Upload a file to the S3 bucket created by CloudFormation. This file is a domain list that you manage with one unique domain per row.
    After a domain list is uploaded, an S3 Event invokes the Lambda function which manages rules, rule groups, and domain lists.
    For DNS Firewall, the Lambda function pulls the domain list from Amazon S3 and updates a DNS Firewall Domain List.
    For Amazon Network Firewall, the Lambda function pulls the domain list from Amazon S3 and updates the firewall rule.

Launching the CloudFormation stack

To begin, launch the CloudFormation stack.  

  1  Go to AWS CloudFormation in the AWS Management Console.  
  
  2  Choose Create Stack and select “With new resources” (standard).  

  3  On the Create Stack page, under Specify template, select the Upload a template file template source.  

  4  Select Choose file and find the template that you downloaded in the Prerequisites steps.  

  5  Choose Next to continue.  

  6  On the Specify Stack Details page, give your stack a name, such as “MyStackName”.  

  7  Under Parameters, review the default parameters and enter the required: BUCKETNAME, R53_RULE_TYPE, ANFW_RULE_TYPE, ANFW_RULE_GROUP_CAPACITY.  

        When deploying CloudFormation, select whether the configured domain lists will allow or deny traffic for both Network Firewall and DNS Firewall.  

        There are several parameters for the CloudFormation stack:  
         -   BUCKETNAME – The name of the S3 Bucket to create  
         -   R53_RULE_TYPE – This is the type of DNS Firewall rule action applied to the domain list.   This must be of the type ALLOW, DENY, or ALERT. The DENY action requires the DENY ACTION parameter to be configured.  
         -   ANFW_RULE_TYPE – This is the type of stateful firewall rule action that is applied to the domain list. It must be of type ALLOWLIST or DENYLIST.  
         -   ANFW_RULE_GROUP_CAPACITY – This is the capacity defined for Amazon Network Firewall Rule groups. This can’t be changed after creation. Refer here to calculate capacity units.  

    8 On the Configure stack options page, you can choose to add tags, choose additional options, or just choose Next.  

    9 On the Review page, validate your parameters and acknowledge that IAM resources will be created.  Finally, select Create stack.  

    10 Once you select Create stack, you can follow the process and view the status of the deployment via the Events tab of the CloudFormation stack. When it finishes deploying, move on to the next step.  


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

