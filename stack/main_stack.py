from aws_cdk import (aws_cognito, aws_ec2, aws_ecs, aws_rds,
                     aws_secretsmanager, Stack, aws_secretsmanager,
                     aws_apigateway, aws_elasticloadbalancingv2, aws_logs,
                     aws_elasticbeanstalk as elasticbeanstalk, aws_s3_assets,
                     aws_iam, aws_logs, aws_sns, aws_lambda,
                     aws_sns_subscriptions, RemovalPolicy, CfnOutput)
from constructs import Construct
import json
import os


class MainStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # --------------------- VPC ---------------------
        vpc = aws_ec2.Vpc(self, 'MyVPC', cidr='10.0.0.0/16', max_azs=2)

        # --------------------- Cluster ---------------------
        cluster = aws_ecs.Cluster(self, 'MyCluster', vpc=vpc)

        # --------------------- RDS ---------------------
        # Templated secret with username and password fields
        rds_secret = aws_secretsmanager.Secret(
            self,
            "RdsSecret",
            generate_secret_string=aws_secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"username": "postgres"}),
                generate_string_key="password",
                exclude_characters='/@" '))

        # Using the templated secret as credentials
        postgresRDS = aws_rds.DatabaseInstance(
            self,
            "PostgresInstance",
            engine=aws_rds.DatabaseInstanceEngine.POSTGRES,
            instance_type=aws_ec2.InstanceType.of(aws_ec2.InstanceClass.T4G,
                                                  aws_ec2.InstanceSize.MICRO),
            credentials=aws_rds.Credentials.from_secret(rds_secret),
            publicly_accessible=True,
            vpc=vpc,
            vpc_subnets=aws_ec2.SubnetSelection(
                subnet_type=aws_ec2.SubnetType.PUBLIC))

        postgresRDS.connections.allow_from_any_ipv4(aws_ec2.Port.all_traffic())
        # Sometimes vpc is not initialized first causing "Cannot create a publicly accessible DBInstance. The specified VPC has no internet gateway attached." error
        # Hopefully adding this dependency can solve the problem
        # If occasionally the error still occurs, simply deploy the stack again
        postgresRDS.node.add_dependency(vpc)

        # --------------------- Cognito ---------------------
        user_pool = aws_cognito.UserPool(self,
                                         "UserPool",
                                         user_pool_name="zoomflex-userpool",
                                         self_sign_up_enabled=True)

        user_pool_client = aws_cognito.UserPoolClient(
            self,
            "UserPoolClient",
            user_pool=user_pool,
            auth_flows=aws_cognito.AuthFlow(user_password=True,
                                            admin_user_password=True))

        # --------------------- Lambda ---------------------
        fn = aws_lambda.Function(
            self,
            "NotificationFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=aws_lambda.Code.from_asset("lambda"),
            #  vpc=vpc
        )

        # --------------------- SNS ---------------------
        topic = aws_sns.Topic(self, "MyTopic")
        topic.add_subscription(aws_sns_subscriptions.LambdaSubscription(fn))

        # --------------------- EB ---------------------
        # S3 asset for eb
        eb_asset = aws_s3_assets.Asset(self,
                                       "BundledAsset",
                                       path=os.getcwd() +
                                       "/microservices/room")

        appName = "MyCfnApplication"
        cfn_application = elasticbeanstalk.CfnApplication(
            self,
            "MyCfnApplication",
            application_name=appName,
        )

        cfn_application_version = elasticbeanstalk.CfnApplicationVersion(
            self,
            "MyCfnApplicationVersion",
            application_name=appName,
            source_bundle=elasticbeanstalk.CfnApplicationVersion.
            SourceBundleProperty(s3_bucket=eb_asset.s3_bucket_name,
                                 s3_key=eb_asset.s3_object_key))

        eb_ec2_role_name = "aws-elasticbeanstalk-ec2-role"
        cfn_environment = elasticbeanstalk.CfnEnvironment(
            self,
            "MyCfnEnvironment",
            application_name=appName,
            solution_stack_name=
            "64bit Amazon Linux 2 v3.4.1 running Python 3.8",
            option_settings=[
                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration",
                    option_name="InstanceType",
                    value="t3.small"),
                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration",
                    option_name="IamInstanceProfile",
                    value=eb_ec2_role_name),
                # elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                #     namespace="aws:elasticbeanstalk:container:python",
                #     option_name="WSGIPath",
                # ),
                # Logs
                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:elasticbeanstalk:cloudwatch:logs",
                    option_name="StreamLogs",
                    value="true"),
                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:elasticbeanstalk:cloudwatch:logs",
                    option_name="DeleteOnTerminate",
                    value="true"),
                # Env var
                elasticbeanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:elasticbeanstalk:application:environment",
                    option_name="DBSECRET",
                    value=rds_secret.secret_full_arn)
            ],
            version_label=cfn_application_version.ref)
        cfn_application_version.node.add_dependency(cfn_application)

        # Grant eb access to secret
        eb_ec2_role = aws_iam.Role.from_role_name(self, "eb_ec2_role",
                                                  eb_ec2_role_name)
        rds_secret.grant_read(eb_ec2_role)

        # --------------------- EC2 ---------------------
        ec2log_group = aws_logs.LogGroup(
            self,
            "EC2CustomLogGroup",
            removal_policy=RemovalPolicy.DESTROY,
        )

        cluster.add_capacity("Capacity",
                             instance_type=aws_ec2.InstanceType("t2.small"),
                             desired_capacity=1)
        task_definition = aws_ecs.Ec2TaskDefinition(self, "TaskDef")
        ec2container = task_definition.add_container(
            "DefaultContainer",
            image=aws_ecs.ContainerImage.from_asset('microservices',
                                                    file="video/Dockerfile"),
            memory_limit_mib=512,
            port_mappings=[aws_ecs.PortMapping(container_port=80)],
            environment={"TopicARN": topic.topic_arn},
            secrets={
                "dbsecret": aws_ecs.Secret.from_secrets_manager(rds_secret)
            },
            logging=aws_ecs.LogDrivers.aws_logs(
                stream_prefix="ec2log",
                log_group=ec2log_group,
            ))

        ec2_service = aws_ecs.Ec2Service(self,
                                         "Ec2Service",
                                         cluster=cluster,
                                         task_definition=task_definition,
                                         desired_count=1)
        task_definition.node.add_dependency(postgresRDS)

        # --------------------- ECS ---------------------
        fargatelog_group = aws_logs.LogGroup(
            self,
            "FargateCustomLogGroup",
            removal_policy=RemovalPolicy.DESTROY,
        )

        fargate_task_definition = aws_ecs.FargateTaskDefinition(
            self,
            "FargateTaskDef",
            memory_limit_mib=512,
        )
        container = fargate_task_definition.add_container(
            "Container",
            image=aws_ecs.ContainerImage.from_asset('microservices',
                                                    file="user/Dockerfile"),
            port_mappings=[aws_ecs.PortMapping(container_port=80)],
            environment={
                "cognito_userPoolId": user_pool.user_pool_id,
                "cognito_userPoolClientId":
                user_pool_client.user_pool_client_id,
            },
            secrets={
                "dbsecret": aws_ecs.Secret.from_secrets_manager(rds_secret)
            },
            logging=aws_ecs.LogDrivers.aws_logs(
                stream_prefix="fargatelog",
                log_group=fargatelog_group,
            ))

        fargate_task_definition.add_to_task_role_policy(
            aws_iam.PolicyStatement(effect=aws_iam.Effect.ALLOW,
                                    actions=["cognito-idp:*"],
                                    resources=["*"]))

        fargate_service = aws_ecs.FargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=fargate_task_definition,
            desired_count=1)
        fargate_task_definition.node.add_dependency(postgresRDS)

        # --------------------- LB ---------------------
        lb = aws_elasticloadbalancingv2.ApplicationLoadBalancer(
            self, "LB", vpc=vpc, internet_facing=True)
        # Add a listener and open up the load balancer's security group
        listener = lb.add_listener(
            "Listener",
            port=80,
            # 'open: true' is the default, you can leave it out if you want. Set it
            # to 'false' and use `listener.connections` if you want to be selective
            # about who can access the load balancer.
            open=True)
        # Add target to the listener.
        listener.add_action(
            "Fixed",
            action=aws_elasticloadbalancingv2.ListenerAction.fixed_response(
                200,
                content_type="text/plain",
                message_body="LB No match found"))
        listener.add_targets(
            "Ec2",
            port=80,
            priority=1,
            conditions=[
                aws_elasticloadbalancingv2.ListenerCondition.path_patterns(
                    ["/video", "/video/*"])
            ],
            targets=[ec2_service])
        listener.add_targets(
            "Fargate",
            port=80,
            priority=2,
            conditions=[
                aws_elasticloadbalancingv2.ListenerCondition.path_patterns(
                    ["/user", "/user/*"])
            ],
            targets=[fargate_service])

        # --------------------- API Gateway ---------------------
        # Note: After updating the microservices, make sure to manually deploy API again to connect to updated url.
        api = aws_apigateway.RestApi(
            self,
            "api",
            default_cors_preflight_options=aws_apigateway.CorsOptions(
                allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
                allow_methods=aws_apigateway.Cors.ALL_METHODS))

        api.root.add_method(
            "GET",
            aws_apigateway.MockIntegration(integration_responses=[
                aws_apigateway.IntegrationResponse(
                    status_code="200",
                    response_templates={
                        "application/json":
                        "{'validPath':['/room','/room/dbtest','/user','/user/dbtest','/video','/video/dbtest']}"
                    },
                )
            ],
                                           request_templates={
                                               "application/json":
                                               "{ 'statusCode': 200 }"
                                           }),
            method_responses=[
                aws_apigateway.MethodResponse(status_code="200")
            ])

        room = api.root.add_resource("room")
        room.add_method(
            "ANY",
            aws_apigateway.HttpIntegration(
                f"http://{cfn_environment.attr_endpoint_url}/room",
                http_method="ANY"))
        room.add_proxy(
            any_method=True,
            default_method_options=aws_apigateway.MethodOptions(
                request_parameters={"method.request.path.proxy": True}),
            default_integration=aws_apigateway.HttpIntegration(
                f"http://{cfn_environment.attr_endpoint_url}/room/{{proxy}}",
                proxy=True,
                options=aws_apigateway.IntegrationOptions(request_parameters={
                    "integration.request.path.proxy":
                    "method.request.path.proxy"
                }),
                http_method="ANY"))

        video = api.root.add_resource("video")
        video.add_method(
            "ANY",
            aws_apigateway.HttpIntegration(
                f"http://{lb.load_balancer_dns_name}/video",
                http_method="ANY"))
        video.add_proxy(
            any_method=True,
            default_method_options=aws_apigateway.MethodOptions(
                request_parameters={"method.request.path.proxy": True}),
            default_integration=aws_apigateway.HttpIntegration(
                f"http://{lb.load_balancer_dns_name}/video/{{proxy}}",
                proxy=True,
                options=aws_apigateway.IntegrationOptions(request_parameters={
                    "integration.request.path.proxy":
                    "method.request.path.proxy"
                }),
                http_method="ANY"))

        user = api.root.add_resource("user")
        user.add_method(
            "ANY",
            aws_apigateway.HttpIntegration(
                f"http://{lb.load_balancer_dns_name}/user", http_method="ANY"))
        user.add_proxy(
            any_method=True,
            default_method_options=aws_apigateway.MethodOptions(
                request_parameters={"method.request.path.proxy": True}),
            default_integration=aws_apigateway.HttpIntegration(
                f"http://{lb.load_balancer_dns_name}/user/{{proxy}}",
                proxy=True,
                options=aws_apigateway.IntegrationOptions(request_parameters={
                    "integration.request.path.proxy":
                    "method.request.path.proxy"
                }),
                http_method="ANY"),
        )

        # --------------------- Output ---------------------
        # Use ApiUrl for all requests
        CfnOutput(self, 'ApiURL', value=api.url)
        CfnOutput(self,
                  'LoadBalancerServiceURL',
                  value=f"http://{lb.load_balancer_dns_name}")
        CfnOutput(self,
                  'ElasticBeanstalkURL',
                  value=cfn_environment.attr_endpoint_url)
        CfnOutput(self, 'UserPoolId', value=user_pool.user_pool_id)
        CfnOutput(self,
                  'UserPoolClientId',
                  value=user_pool_client.user_pool_client_id)
