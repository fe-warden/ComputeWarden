# AutoResizer Script v1.0 
Authored by Andres Martinez

# Overview
The AutoResizer script is a Python-based Lambda function that is able to resize instances based on tags. This pseudo-application also features built-in error-handling and logging. 

# Requirements
- The user creating the Lambda Function, IAM role, and modifying tags in EC2 **must** be an Administrator.
- The autoresizer.py source-code.
- The IAM Policy titled "Allow-EC2-AutoResize.json"

# Deployment Guide
## Lambda Section
1. Go to AWS Lambda and create a new function.
    - Name it something useful; this will be needed for the IAM section.
2. Copy and paste the source code from autoresizer.py.
3. Edit the timeout configuration to be 14 minutes and 0 seconds.
4. Add an environment variable titled **Region** with the value of the region (ex: us-east-1)
    - This is **case-sensitive**!
5. Add an event trigger with EventBridge.
    - See CRON Examples section for examples and to better understand CRON.

## IAM Section
1. Create a new IAM Policy.
2. Paste the contents of Allow-EC2-AutoResize.json into the JSON section.
    - Modify permissions as necessary if company policy dictates something else. 
3. Name the policy "Allow-EC2-AutoResize" or whatever name you want.
4. Attach the policy to the auto-generated Lambda role with the name you specified.

## EC2 Section
For each instance being modified:
- Add the following tags: 
    1. Key Name: AutoResizerInstanceType, Value: **INSTANCETYPE_VALUE** (t3.medium)
    2. Key Name: AutoResizerInstanceAuth, Value: **boolean** (true/false)
    
- Note: The only accepted values for Auth are: true or false; case-sensitive. 

# CRON Examples
- cron(01 08 04 07 ? 2022)
    - Explanation: Execute on July 4th, 2022 at 08:01 UTC.
    - Use case: If you only want one-time execution.
- cron(01 08 * * SAT *)
    - Explanation: Execute every Saturday at 08:01 UTC.
    - Use case: If you want continual executions.

# Troubleshooting
- Most if not all the problems you may encounter with this Lambda function are related to IAM permissions. Ensure you have the correct values in place for the Allow-EC2-AutoResize policy and that it is attached to the Lambda Role. 
- The logs will also tell you what the problem was. Detailed logging is configured for the application. 