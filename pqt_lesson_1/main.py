from ipaddress import ip_address
from subprocess import Popen, PIPE, TimeoutExpired
from tabulate import tabulate
from threading import Thread
import platform



class ThreadPing(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def ping(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    try:
        adress = ip_address(ip)
    except ValueError:
        print('Invalid adress')
        return 
    proc = Popen(['ping', param, '1', str(adress)], stderr=PIPE, stdout=PIPE)
    try:
        outs, errs = proc.communicate(timeout=1)
        return {'reachable': ip}
    except TimeoutExpired:
        proc.kill()
        return {'unreachable': ip}


def host_ping(ipses):
    results = []
    for i in ipses:
        th = ThreadPing(target=ping, args=(i, ))
        th.start()
        if th.join():
            results.append(th.join())
            
    return results
        
def host_range_ping():
    ip = input('Введите ip адрес: ')
    try:
        ip = ip_address(ip)
        base_ip = '.'.join(str(ip).split('.')[:-1])
        last_oct = int(str(ip).split('.')[-1])
        distance = int(input('Введите количество: '))
        list_ip = []
        for ip in range(last_oct, distance + last_oct):
            list_ip.append(f'{base_ip}.{ip}')

        return host_ping(list_ip)
    except ValueError:
        print('Invalid ip')
        return
    
def host_range_ping_tab():
    print(tabulate(host_range_ping(), headers='keys'))



if __name__ == '__main__':

    host_range_ping_tab()

