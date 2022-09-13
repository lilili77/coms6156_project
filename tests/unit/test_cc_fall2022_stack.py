import aws_cdk as core
import aws_cdk.assertions as assertions

from cc_fall2022.cc_fall2022_stack import CcFall2022Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in cc_fall2022/cc_fall2022_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CcFall2022Stack(app, "cc-fall2022")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
