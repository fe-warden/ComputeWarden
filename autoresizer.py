#
#   
#   Authored by: Andres D. Martinez
#
#

import boto3,os

# define the connections
region = os.environ['Region']
client = boto3.client('ec2', region_name=region)

# Instantiates the dictionaries that will be used to find valid and authenticated instances.
TagList = {}
GoodAuth = {}

# Automatically finds all instances with specific tags.
def resize_instance():
    # Calls tag_finder() and ignore instances in the list if they don't have tags.
    InstanceTypeMap = {}
    InstanceTypeMap = tag_finder()

    
    for an_instance in InstanceTypeMap:
        statusof_instance = get_status(an_instance)
        if(statusof_instance == 'running'):
            client.stop_instances(InstanceIds=[an_instance],Hibernate=False)
            waiter = client.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=[an_instance])
            print("Stopped the instance: ", an_instance)
        elif(statusof_instance == 'stopped'):
            print('The instance ', an_instance," is already stopped.")
        else:
            raise ValueError("Error! The selected instance entered an invalid state while this program executed! Instance: ", an_instance)
        
        client.modify_instance_attribute(InstanceId=an_instance,
                                         Attribute='instanceType', Value=InstanceTypeMap[an_instance])
        print(an_instance, "Resized the instance to: ", InstanceTypeMap[an_instance])
        
        # Leave instances in previous state if previous state was not running.
        if(statusof_instance == 'running'):
            client.start_instances(InstanceIds=[an_instance])
            print("Started ", an_instance)
        
        # Reset the auth tag to ensure that it won't unnecessarily run in the future.
        # format when calling the method: reset_tag(tag_name, instance-id, old_value, new_value)
        response = reset_tag('AutoResizerInstanceAuth', an_instance, 'true', 'false')
        print("Resetting authentication tag: ", response)

# Gets the current status of an instance.
def get_status(instance):
    instance = str(instance)
    response_raw = client.describe_instance_status(InstanceIds=[str(instance)],IncludeAllInstances=True)
    status = response_raw['InstanceStatuses'][0]['InstanceState']['Name']
    return status

# Takes a given instance ID and resets a tag to a desired value.
def reset_tag(tag, instance, current_value, new_value):
    client = boto3.client('ec2', region_name=region)
    response = client.delete_tags(Resources=[instance,],Tags=[{'Key':tag,'Value':current_value}])
    if(response['ResponseMetadata']['HTTPStatusCode'] == 200):
        create_response = client.create_tags(Resources=[instance,],Tags=[{'Key':tag,'Value':new_value}])
    else:
        raise ValueError("There was an unexpected error when resetting the tag: ", tag,". \r\nPlease check your permissions or the status of AWS to troubleshoot.")
    return create_response['ResponseMetadata']['HTTPStatusCode']

# This function checks to ensure that the list of instances selected all have the associated tag.
def tag_finder():
    try:
        TagListRaw = client.describe_instances(Filters=[{'Name':'instance-state-name','Values':['running','stopped']}],DryRun=False)
        TagList = {}
        for reservation in TagListRaw['Reservations']:
            for instance in reservation['Instances']:
                tags = instance['Tags']
                instanceIdToMap = instance['InstanceId']

                # Check for Required values
                for tag in tags:
                    if('AutoResizerInstanceType' in tag['Key']):
                        # Check for requested resize value and map it to the instance ID
                        TagList[instanceIdToMap] = tag['Value']
                    elif('AutoResizerInstanceAuth' in tag['Key']):
                        # Check for authentication tag and map it to the instance ID
                        GoodAuth[instanceIdToMap] = tag['Value']
                    else:
                        continue # Nothing else to do because the instance is not being targeted.
        TagList = authCheck(TagList, GoodAuth)
        return TagList
                                       
    except ValueError as err:
        print(err.args)

# Necessary for the auth validation check in Tag Checker
def authCheck(dict1, dict2):
    dict1 = dict(dict1)
    dict2 = dict(dict2)

    for key in dict1:
        if ((key in dict2.keys()) and dict2[key] == 'true'):
            continue # The value in the dictionary at key is the same in the other dictionary
        else:
            dict1 = removeKey(dict1, key)
    return dict1


# Needed for easy key removal from dictionaries
def removeKey(d, key):
    r = dict(d)
    del r[key]
    return r

def lambda_handler(event, context):
    resize_instance()