class FrontDeckInfo:
    def __init__(self, *args, **kwargs):
        self.link = kwargs.get('link')
        self.hs_class = kwargs.get('hs_class')
        self.rating = kwargs.get('rating')
        self.last_edit = kwargs.get('last_edit')
        self.views = kwargs.get('views')
        self.comments = kwargs.get('comments')

    def __dir__(self):
        return ['link', 'hs_class', 'rating']

    def __str__(self, *args, **kwargs):
        instance_str = ""
        instance_str += self.__class__.__name__ + ": "
        instance_str += ", ".join([attr + ": " + self.__getattribute__(attr) for attr in dir(self)])

        return instance_str


