import sys
import time
import xml.etree.ElementTree as XML
import requests
from colorama import Fore


def ip_checker() -> str:
    try:
        ip = requests.get('https://api.ipify.org', timeout=30)
        if ip.status_code == 200:
            return ip.text
        else:
            print('SERVER NOT RESPONDING: https://api.ipify.org')
            sys.exit()
    except requests.exceptions.ConnectionError:
        print('NO CONNECTION')


def session(host: str) -> dict:
    response = requests.get(f'http://{host}/api/webserver/SesTokInfo')
    root = XML.ElementTree(XML.fromstring(response.content)).getroot()
    headers = {'__RequestVerificationToken': f'{root[1].text}',
               '_ResponseSource': 'Broswer',
               'Cookie': f'SessionID={root[0].text}'}
    return headers


def net_mode(host: str) -> str:
    response = requests.get(f'http://{host}/api/net/net-mode')
    root = XML.ElementTree(XML.fromstring(response.content)).getroot()
    net = root[0].text
    return net


def device_name(host: str) -> str:
    response = requests.get(f'http://{host}/api/device/information')
    root = XML.ElementTree(XML.fromstring(response.content)).getroot()
    name = root[0].text
    return name


def ip_maker(host: str, net_send: str) -> None:
    headers = session(host)
    payload = f"<?xml version='1.0' encoding='UTF-8'?><request><NetworkMode>{net_send}" \
              f"</NetworkMode><NetworkBand>3FFFFFFF</NetworkBand><LTEBand>800C5</LTEBand></request>"
    requests.post(f'http://{host}/api/net/net-mode', data=payload, headers=headers)


class Modem:

    def __init__(self, host: str = '192.168.8.1', lte=False):
        self.mode = lte
        self.host = host
        self.time_control = time.time()
        self.old_ip = ip_checker()
        self.make_ip()

    def make_ip(self):
        _net = net_mode(self.host)
        if _net == '02':
            ip_maker(self.host, net_send='03')
        elif self.mode:
            ip_maker(self.host, net_send='02')
            ip_maker(self.host, net_send='03')
        else:
            ip_maker(self.host, net_send='02')
        new_ip = ip_checker()
        if self.old_ip != new_ip:
            print(Fore.BLUE +
                  f'{device_name(self.host)}: {new_ip} time: {round(time.time() - self.time_control)}sec')
        else:
            self.make_ip()


#Modem(lte=True)
