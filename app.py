#!/usr/bin/env python3

import aws_cdk as cdk

from stack.main_stack import MainStack
from stack.frontend_stack import FrontendStack

app = cdk.App()

MainStack(
    app,
    "COMS6156ProjectStack",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */
    env=cdk.Environment(account='074126400183', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)

# FrontendStack(
#     app,
#     "COMS6156FrontendStack",
#     env=cdk.Environment(account='074126400183', region='us-east-1'),
# )

app.synth()
