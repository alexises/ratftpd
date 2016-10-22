from fbtftp.base_server import BaseServer
from fbtftp.base_handler import BaseHandler

def print_server_stats(stats):
    counters = stats.get_and_reset_all_counters()
    print('Server stats - every {} seconds'.format(stats.interval))
    print(counters)

class RatftpServerHandler(BaseHandler):
    def __init__(self, server_addr, peer, path, options, config, stats_callback):
        self.config = config.getConfig(peer)
        super().__init__(server_addr, peer, path, options, stats_callback)

class RatftpServer(BaseServer):
    ''' Base tftp server class '''
    def __init__(self, bind, port, timeout, retry, config):
        self.config = config
        super().__init__(bind, port, timeout, retry, print_server_stats)

    def get_handler(self, server_addr, peer, path, options):
        return RatftpServerHandler(
            server_addr, peer, path, options, self.config,
            self._handler_stats_callback)
