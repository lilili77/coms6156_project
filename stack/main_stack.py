from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3,
    aws_s3_deployment,
    aws_ec2, aws_ecs, aws_ecs_patterns,
    aws_rds, aws_secretsmanager,
    aws_apigateway,
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
            instance_type=aws_ec2.InstanceType.of(aws_ec2.InstanceClass.T4G, aws_ec2.InstanceSize.MICRO),
            credentials=aws_rds.Credentials.from_secret(templated_secret),
            vpc=vpc
        )

        ## ECS frontend by ALB
        cluster = aws_ecs.Cluster(self, 'MyCluster', vpc=vpc)
        load_balanced_fargate_service = aws_ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            task_image_options=aws_ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=aws_ecs.ContainerImage.from_asset('flaskapp'), # .from_registry("amazon/amazon-ecs-sample")
                secrets={"dbsecret":aws_ecs.Secret.from_secrets_manager(templated_secret)}
            )
        )

        ## API Gateway
        api = aws_apigateway.RestApi(self, "api")
        user = api.root.add_resource("user")
        video = api.root.add_resource("video")
        room = api.root.add_resource("room")
        user.add_method("GET", aws_apigateway.HttpIntegration(
            f"http://{load_balanced_fargate_service.load_balancer.load_balancer_dns_name}"
        ))
        
        # # S3 static website
        # website_bucket = aws_s3.Bucket(
        #     self,
        #     "WebsiteBucket",
        #     website_index_document="index.html",
        #     website_error_document="404.html",
        #     public_read_access=True
        # )
        
        # aws_s3_deployment.BucketDeployment(self, "DeployWebsite",
        #     sources=[aws_s3_deployment.Source.asset("../frontend/out")], #Resource not found
        #     destination_bucket=website_bucket,
        # )

        ## Output
        CfnOutput(self, 'ServiceURL', value="http://{}".format(
            load_balanced_fargate_service.load_balancer.load_balancer_dns_name))
