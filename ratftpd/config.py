
class Config(object):
    ''' manage configuration '''

    def __init__(self, config):
        self.bind = config.get("bind", "0.0.0.0")
        self.port = config.get("port", 69)
