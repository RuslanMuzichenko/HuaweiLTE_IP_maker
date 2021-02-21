import urllib3
import xml.etree.ElementTree as XML
import requests
import time
from colorama import Fore

class HuaweiLTE(object):

    def __init__(self):
        host = 'http://192.168.8.1/'
        self.host = host
        ctrl_time = time.time()
        self.ctrl_time = ctrl_time
        try:
            ip = requests.get('https://ipinfo.io', timeout=30).json()
            old_ip =  ip['ip']
            self.old_ip = old_ip
            self.session()
        except:
            self.session()
            self.reboot()

    def session(self):
        http = urllib3.PoolManager()
        self.http = http
        response_body = http.request('GET', f'{self.host}api/webserver/SesTokInfo')
        tree = XML.ElementTree(XML.fromstring(response_body.data))
        root = tree.getroot()
        session = root[0].text
        tokken = root[1].text
        self.session = session
        self.tokken = tokken
        response_body = http.request('GET', f'{self.host}api/device/information')
        tree = XML.ElementTree(XML.fromstring(response_body.data))
        root = tree.getroot()
        modem = root[0].text
        self.modem = modem


    def reboot(self):
        headers = {'__RequestVerificationToken': f'{self.tokken}',
                   '_ResponseSource': 'Broswer',
                   'Cookie': f'SessionID={self.session}'
                   }
        data = "<?xml version='1.0' encoding='UTF-8'?><request><Control>1</Control></request>"
        result = self.http.request('POST', f'{self.host}api/device/control', body=data, headers=headers)
        if 'OK' in result.data.decode():
            print(f'{self.modem} перезагружен')


    def ip_make(self):
        response_body = self.http.request('GET', f'{self.host}api/net/net-mode')
        tree = XML.ElementTree(XML.fromstring(response_body.data))
        root = tree.getroot()
        Net = root[0].text
        if Net == '02':
            Net_send = '03'
        else:
            Net_send = '02'
        headers = {'__RequestVerificationToken': f'{self.tokken}',
                   '_ResponseSource': 'Broswer',
                   'Cookie': f'SessionID={self.session}'
                   }
        data = f"<?xml version='1.0' encoding='UTF-8'?><request><NetworkMode>{Net_send}</NetworkMode><NetworkBand>3FFFFFFF</NetworkBand><LTEBand>800C5</LTEBand></request>"
        result = self.http.request('POST', f'{self.host}api/net/net-mode', body=data, headers=headers)
        if 'OK' in result.data.decode():
            ip = requests.get('https://ipinfo.io', timeout=30).json()
            new_ip = ip['ip']
            if self.old_ip != new_ip:
                cure_time = round(time.time() - self.ctrl_time)
                print(Fore.BLUE + f'{self.modem}: получен IP: {new_ip } за {cure_time}sec')
        else:
            HuaweiLTE().ip_make()

HuaweiLTE().ip_make()
