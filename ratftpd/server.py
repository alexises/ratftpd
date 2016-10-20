from fbtftp.base_server import BaseServer

def print_server_stats(stats):
    counters = stats.get_and_reset_all_counters()
    print('Server stats - every {} seconds'.format(stats.interval))
    print(counters)


class RatftpServer(BaseServer):
     ''' Base tftp server class '''
     def __init__(self, bind, port):
         super().__init__(bind, port, 5, 5, print_server_stats)
