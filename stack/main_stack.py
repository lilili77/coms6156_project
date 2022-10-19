from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_ec2, aws_ecs, aws_ecs_patterns,
    aws_rds, aws_secretsmanager,
    CfnOutput
)
from constructs import Construct
import json

class MainStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        
        ## VPC
        vpc = aws_ec2.Vpc(self, 'MyVPC', cidr='10.0.0.0/16')

        ## RDS Postgres
        # Templated secret with username and password fields
        templated_secret = aws_secretsmanager.Secret(self, "TemplatedSecret",
            generate_secret_string=aws_secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"username": "postgres"}),
                generate_string_key="password",
                exclude_characters='/@" '
            )
        )
        # Using the templated secret as credentials
        postgresRDS = aws_rds.DatabaseInstance(self, "PostgresInstance",
            engine=aws_rds.DatabaseInstanceEngine.POSTGRES,
            credentials=aws_rds.Credentials.from_secret(templated_secret),
            vpc=vpc
        )

        ## ECS frontended by ALB
        cluster = aws_ecs.Cluster(self, 'MyCluster', vpc=vpc)
        load_balanced_fargate_service = aws_ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            task_image_options=aws_ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=aws_ecs.ContainerImage.from_asset('flaskapp'), # .from_registry("amazon/amazon-ecs-sample")
                secrets={"dbsecret":aws_ecs.Secret.from_secrets_manager(templated_secret)}
            )
        )

        ## Output
        CfnOutput(self, 'SericeURL', value="http://{}".format(
            load_balanced_fargate_service.load_balancer.load_balancer_dns_name))
