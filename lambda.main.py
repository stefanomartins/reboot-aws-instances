import boto3
import os
import json

AWS_REGION = os.getenv("AWS_REGION")

def get_message_from_event(event: str) -> dict:
    message = json.dumps(event["Records"][0]["Sns"]["Message"])
    message = message.replace("\\", "").replace("\"", "", 1)[::-1].replace("\"", "", 1)[::-1]
    message = json.loads(message)
    return message

def is_elb(message: dict) -> bool:
    if message["Trigger"]["Namespace"] == "AWS/ELB":
        return True
    else:
        return False

def is_elbv2(message: dict) -> bool:
    if message["Trigger"]["Namespace"] == "AWS/ApplicationELB":
        return True
    else:
        return False

def elb_get_instances(message: dict) -> dict:
    elb_name = message["Trigger"]["Dimensions"][0]["value"]
    elb = boto3.client("elb", region_name=AWS_REGION)
    instances = elb.describe_instance_health(LoadBalancerName=elb_name)
    return instances["InstanceStates"]

def elbv2_get_instances(message: dict) -> dict:
    elbv2 = boto3.client("elbv2", region_name=AWS_REGION)
    tg_name = message["Trigger"]["Dimensions"][0]["value"].split("/")[1]
    r = elbv2.describe_target_groups(Names=[tg_name])
    arn = r["TargetGroups"][0]["TargetGroupArn"]
    instances = elbv2.describe_target_health(TargetGroupArn=arn)
    return instances["TargetHealthDescriptions"]

def ec2_reboot_instance(instance_id: str) -> dict:
    ec2 = boto3.client("ec2", region_name=AWS_REGION)
    r = ec2.reboot_instances(InstanceIds=[instance_id])
    return r

def lambda_handler(event, context):
    message = get_message_from_event(event=event)

    if is_elb(message=message):
        print("É um ELB Classic")
        instances = elb_get_instances(message=message)
        for instance in instances:
            if instance["State"] == "InService":
                print(f"Instância {instance['InstanceId']} saudável")
            elif instance["State"] == "OutOfService":
                print(f"Problema com a instância: {instance['InstanceId']}. Reiniciando.")
                ec2_reboot_instance(instance_id=instance["InstanceId"])

    elif is_elbv2(message=message):
        print("É um ELBv2")
        instances = elbv2_get_instances(message=message)
        for instance in instances:
            if instance["TargetHealth"]["State"] == "healthy":
                print(f"Instância {instance['Target']['Id']} saudável")
            elif instance["TargetHealth"]["State"] == "unhealthy":
                print(f"Problema com a instância: {instance['Target']['Id']}. Reiniciando.")
                ec2_reboot_instance(instance_id=instance["Target"]["Id"])