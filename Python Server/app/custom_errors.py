class OnImageNotFound(Exception):
    def __init__(self, * args):
        if args:
                self.message = args[0]
        else :
                self.message = None
        args[1].imageStatusCode = 404
    def __str__(self):
        if self.message:
                return 'OnImageNotFound, {0} '.format(self.message)
        else :
                return 'OnImageNotFound has been raised'
class OnImageUrlNotValid(Exception):
    def __init__(self, * args):
        if args:
                self.message = args[0]
        else :
                self.message = None
        args[1].imageStatusCode = 500
    def __str__(self):
        if self.message:
                return 'OnImageUrlNotValid, {0} '.format(self.message)
        else :
                return 'OnImageUrlNotValid has been raised'
class EmbedableContentNotFound(Exception):
    def __init__(self, * args):
        if args:
                self.message = args[0]
        else :
                self.message = None
        args[1].statusCode = 409
        args[1].row.remove() #removes the row beacuse it will be blank
    def __str__(self):
        if self.message:
                return 'EmbedableContentNotFound, {0} '.format(self.message)
        else :
                return 'EmbedableContentNotFound has been raised'