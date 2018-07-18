import TestCase.SDK.base as base

class imagesList(base.SDKbase):

    def __init__(self):
        super(imagesList, self).__init__()

    def run(self, **kwargs):
        print kwargs
        print self.client.list_images()