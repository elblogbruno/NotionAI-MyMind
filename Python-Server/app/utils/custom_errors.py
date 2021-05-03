class OnImageNotFound(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
        #args[1].imageStatusCode = 409
        args[1].statusCode = 200
    def __str__(self):
        if self.message:
            return 'OnImageNotFound, {0} '.format(self.message)
        else:
            return 'OnImageNotFound has been raised'


class OnUrlNotValid(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
        args[1].statusCode = 500

    def __str__(self):
        if self.message:
            return 'OnImageUrlNotValid, {0} '.format(self.message)
        else:
            return 'OnImageUrlNotValid has been raised'



class OnTokenV2NotValid(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'OnTokenV2NotValid, {0} '.format(self.message)
        else:
            return 'OnTokenV2NotValid has been raised'

class OnCollectionNotAvailable(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'OnCollectionNotAvailable, {0} '.format(self.message)
        else:
            return 'OnCollectionNotAvailable has been raised'

class OnServerNotConfigured(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'OnServerNotConfigured, {0} '.format(self.message)
        else:
            return 'OnServerNotConfigured has been raised'