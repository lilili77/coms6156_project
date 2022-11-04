from aws_cdk import (aws_cognito, aws_s3, aws_s3_deployment, RemovalPolicy,
                     Stack, CfnOutput)

from constructs import Construct


class FrontendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Cognito
        aws_cognito.UserPool(self,
                             "userPool",
                             user_pool_name="zoomflex-userpool")

        # S3 static website
        website_bucket = aws_s3.Bucket(self,
                                       "WebsiteBucket",
                                       removal_policy=RemovalPolicy.DESTROY,
                                       auto_delete_objects=True,
                                       website_index_document="index.html",
                                       website_error_document="404.html",
                                       public_read_access=True)

        deployment = aws_s3_deployment.BucketDeployment(
            self,
            "DeployWebsite",
            sources=[aws_s3_deployment.Source.asset("../frontend/out")],
            destination_bucket=website_bucket,
        )

        CfnOutput(self,
                  'FEURL',
                  value=deployment.deployed_bucket.bucket_website_url)
