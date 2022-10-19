from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_ec2, aws_ecs, aws_ecs_patterns,
    CfnOutput
)
from constructs import Construct

class MainStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        vpc = aws_ec2.Vpc(self, 'MyVPC', cidr='10.0.0.0/16')

        cluster = aws_ecs.Cluster(self, 'MyCluster', vpc=vpc)
        load_balanced_fargate_service = aws_ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            task_image_options=aws_ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=aws_ecs.ContainerImage.from_asset('flaskapp') # .from_registry("amazon/amazon-ecs-sample")
                
            )
        )

        CfnOutput(self, 'SericeURL', value="http://{}".format(
            load_balanced_fargate_service.load_balancer.load_balancer_dns_name))
