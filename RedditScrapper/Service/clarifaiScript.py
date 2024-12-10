
##################################################################################################
# In this section, we set the user authentication, user and app ID, model details, and the URL
# of the image we want as an input. Change these strings to run your own example.
#################################################################################################

# Your PAT (Personal Access Token) can be found in the Account's Security section
PAT = '51a43bfe37ce47dca127491f8046065b'
# Specify the correct user_id/app_id pairings
# Since you're making inferences outside your app's scope
USER_ID = 'clarifai'
APP_ID = 'main'
# Change these to whatever model and image URL you want to use
MODEL_ID = 'moderation-recognition'
MODEL_VERSION_ID = 'aa8be956dbaa4b7a858826a84253cab9'
IMAGE_URL = 'https://summitdetox.com/wp-content/uploads/2020/03/weed-drug-abuse.jpg'

############################################################################
# YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE TO RUN THIS EXAMPLE
############################################################################

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', 'Key ' + PAT),)

userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)
def checkDrugFromImage(ImageUrl):
    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
        user_app_id=userDataObject,  # The userDataObject is created in the overview and is required when using a PAT
        model_id=MODEL_ID,
        version_id=MODEL_VERSION_ID,  # This is optional. Defaults to the latest model version
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    image=resources_pb2.Image(
                        url=ImageUrl
                    )
                )
            )
        ]
    ),
    metadata=metadata
)
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

# Since we have one input, one output will exist here
    output = post_model_outputs_response.outputs[0]

    # print("Predicted concepts:")
    res = {}
    for i in output.data.concepts:
        res[i.name] = i.value
    return res

# Uncomment this line to print the full Response JSON
#print(output)

