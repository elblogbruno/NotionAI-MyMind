from clarifai_grpc.grpc.api import service_pb2_grpc, service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel

class ClarifaiAI:
    def __init__(self,key):
        # Construct one of the channels you want to use
        self.channel = ClarifaiChannel.get_json_channel()
        self.key = key
    def get_tags(self,image_url):
        stub = service_pb2_grpc.V2Stub(self.channel)

        request = service_pb2.PostModelOutputsRequest(
            model_id='aaa03c23b3724a16a56b629203edc62c',
            inputs=[
            resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(url=image_url)))
            ])
        metadata = (('authorization', 'Key 7d13a00d87c5408b96fa94d16ad3c521'),)

        response = stub.PostModelOutputs(request, metadata=metadata)

        if response.status.code != status_code_pb2.SUCCESS:
            raise Exception("Request failed, status code: " + str(response.status.code))

        tags = []
        for concept in response.outputs[0].data.concepts:
            tags.append(str(concept.name))
            print(concept.name)

        str1 = ','.join(str(e) for e in tags)
        return str1