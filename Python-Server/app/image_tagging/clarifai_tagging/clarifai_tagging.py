from clarifai_grpc.grpc.api import service_pb2_grpc, service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel


class ClarifaiAI:

    def __init__(self, key):
        # Construct one of the channels you want to use
        self.channel = ClarifaiChannel.get_json_channel()
        self.key = key

    def get_tags(self, image_url, is_local_image, treshold):
        stub = service_pb2_grpc.V2Stub(self.channel)
        file_bytes = {}
        file = ""

        if is_local_image:
            file = "./uploads/" + image_url.split("/")[-1]
            with open(file, "rb") as f:
                file_bytes = f.read()
        else:
            file = image_url

        if is_local_image:
            request = service_pb2.PostModelOutputsRequest(
                model_id='aaa03c23b3724a16a56b629203edc62c',
                inputs=[
                    resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(base64=file_bytes)))
                ])
        else:
            request = service_pb2.PostModelOutputsRequest(
                model_id='aaa03c23b3724a16a56b629203edc62c',
                inputs=[
                    resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(url=file)))
                ])

        metadata = (('authorization', 'Key {0}'.format(self.key)),)

        response = stub.PostModelOutputs(request, metadata=metadata)

        if response.status.code != status_code_pb2.SUCCESS:
            raise Exception("Request failed, status code: " + str(response.status.code))

        tags = []
        for concept in response.outputs[0].data.concepts:
            if concept.value > treshold:
                tags.append(str(concept.name))

        print('Predicted:', tags)

        return tags
