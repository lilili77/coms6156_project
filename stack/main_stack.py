from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3,
    aws_s3_deployment,
    aws_ec2, aws_ecs, aws_ecs_patterns,
    aws_rds, aws_secretsmanager,
    aws_apigateway,
    aws_elasticloadbalancingv2,
    aws_logs,
    aws_elasticbeanstalk as elasticbeanstalk,
    aws_s3_assets,
    CfnOutput
)
from constructs import Construct
import json

import os

class MainStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        
        ## VPC
        vpc = aws_ec2.Vpc(self, 'MyVPC', cidr='10.0.0.0/16', max_azs=2)

        ## Cluster
        cluster = aws_ecs.Cluster(self, 'MyCluster', vpc=vpc)

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

        ## EB
        # S3 asset
        eb_asset = aws_s3_assets.Asset(self, "BundledAsset",
            path=os.getcwd()+"/flaskapp3" #os.path.join(os.getcwd(), "markdown-asset")
        )

        appName = "MyCfnApplication"
        cfn_application = elasticbeanstalk.CfnApplication(self, "MyCfnApplication",
            application_name=appName,
        )
        
        cfn_application_version = elasticbeanstalk.CfnApplicationVersion(self, "MyCfnApplicationVersion",
            application_name=appName,
            source_bundle=elasticbeanstalk.CfnApplicationVersion.SourceBundleProperty(
                s3_bucket=eb_asset.s3_bucket_name,
                s3_key=eb_asset.s3_object_key
            )
        )

        cfn_environment = elasticbeanstalk.CfnEnvironment(self, "MyCfnEnvironment",
            application_name=appName,
            solution_stack_name="64bit Amazon Linux 2 v3.4.0 running Python 3.8",
            option_settings=[
                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration",
                    option_name="InstanceType",
                    value="t3.small"
                ),
                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration",
                    option_name="IamInstanceProfile",
                    value="aws-elasticbeanstalk-ec2-role"
                ),
                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:elasticbeanstalk:container:python",
                    option_name="WSGIPath",
                )
            ],
            version_label=cfn_application_version.ref
        )
        cfn_application_version.node.add_dependency(cfn_application)

        ## EC2
        cluster.add_capacity("Capacity",
            instance_type=aws_ec2.InstanceType("t2.small"),
            desired_capacity=1
        )
        task_definition = aws_ecs.Ec2TaskDefinition(self, "TaskDef")
        ec2container = task_definition.add_container("DefaultContainer",
            image=aws_ecs.ContainerImage.from_asset('flaskapp'),
            memory_limit_mib=512,
            port_mappings=[aws_ecs.PortMapping(container_port=80)],
            secrets={"dbsecret":aws_ecs.Secret.from_secrets_manager(templated_secret)},
            logging=aws_ecs.LogDrivers.aws_logs(stream_prefix="ec2log",log_retention=aws_logs.RetentionDays.ONE_DAY)
        )
        ec2_service = aws_ecs.Ec2Service(self, "Ec2Service",
            cluster=cluster,
            task_definition=task_definition
        )
        task_definition.node.add_dependency(postgresRDS)

        ## ECS
        fargate_task_definition = aws_ecs.FargateTaskDefinition(self, "FargateTaskDef",
            memory_limit_mib=512,
        )
        container = fargate_task_definition.add_container("Container",
            image=aws_ecs.ContainerImage.from_asset('flaskapp2'),
            port_mappings=[aws_ecs.PortMapping(container_port=80)],
            secrets={"dbsecret":aws_ecs.Secret.from_secrets_manager(templated_secret)},
            logging=aws_ecs.LogDrivers.aws_logs(stream_prefix="fargatelog",log_retention=aws_logs.RetentionDays.ONE_DAY)
        )
        fargate_service = aws_ecs.FargateService(self, "Service",
            cluster=cluster,
            task_definition=fargate_task_definition,
            desired_count=1
        )
        fargate_task_definition.node.add_dependency(postgresRDS)

        ## LB
        lb = aws_elasticloadbalancingv2.ApplicationLoadBalancer(self, "LB",
            vpc=vpc,
            internet_facing=True
        )
        # Add a listener and open up the load balancer's security group
        # to the world.
        listener = lb.add_listener("Listener",
            port=80,
            # 'open: true' is the default, you can leave it out if you want. Set it
            # to 'false' and use `listener.connections` if you want to be selective
            # about who can access the load balancer.
            open=True
        )
        # Add target to the listener.
        listener.add_action("Fixed",
            action=aws_elasticloadbalancingv2.ListenerAction.fixed_response(200,
                content_type="text/plain",
                message_body="No match found"
            )
        )
        listener.add_targets("Ec2",
            port=80,
            priority=1,
            conditions=[
                aws_elasticloadbalancingv2.ListenerCondition.path_patterns(["/ec2","/ec2/*"])
            ],
            targets=[ec2_service]
        )
        listener.add_targets("Fargate",
            port=80,
            priority=2,
            conditions=[
                aws_elasticloadbalancingv2.ListenerCondition.path_patterns(["/fargate","/fargate/*"])
            ],
            targets=[fargate_service]
        )

        ## API Gateway
        api = aws_apigateway.RestApi(self, "api")
        proxy = api.root.add_proxy(
            any_method=True,
            default_method_options=aws_apigateway.MethodOptions(
                request_parameters={"method.request.path.proxy":True}
            ),
            default_integration=aws_apigateway.HttpIntegration(
                f"http://{lb.load_balancer_dns_name}/{{proxy}}",
                proxy=True,
                options=aws_apigateway.IntegrationOptions(request_parameters={"integration.request.path.proxy":"method.request.path.proxy"})
            )
        )

        ## S3 static website
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
        CfnOutput(self, 'LBServiceURL', value=f"http://{lb.load_balancer_dns_name}")
        CfnOutput(self, 'EBURL', value=cfn_environment.attr_endpoint_url)
        CfnOutput(self, 'EBBucket', value=eb_asset.s3_bucket_name)
        CfnOutput(self, 'EBKey', value=eb_asset.s3_object_key)
        
        