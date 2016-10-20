
class Config(object):
    ''' manage configuration '''

    def __init__(self, config):
        self.bind = config.get("bind", "")
        self.port = config.get("port", 69)
        self.timeout = config.get("timeout", 5)
        self.retry = config.get("retry", 5)
