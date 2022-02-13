import ssl
import requests
from collections import OrderedDict
import re
import socket
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager

def username_to_data(username, password):
    class SSLAdapter(HTTPAdapter):
        def init_poolmanager(self, connections, maxsize, block=False):
            self.poolmanager = PoolManager(num_pools=connections,
                                        maxsize=maxsize,
                                        block=block,
                                        ssl_version=ssl.PROTOCOL_TLSv1_2)

    headers = OrderedDict({
        'User-Agent': 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)'
    })

    session = requests.session()
    session.mount('https://auth.riotgames.com/api/v1/authorization', SSLAdapter())
    session.headers = headers

    data = {
        'client_id': 'play-valorant-web-prod',
        'nonce': '1',
        'redirect_uri': 'https://playvalorant.com/opt_in',
        'response_type': 'token id_token',
    }
    r = session.post(f'https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
    print(r)
    print(r.text)
    data = {
        'type': 'auth',
        'username': username,
        'password': password
    }
    r = session.put(f'https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
    print(r)
    print(r.text)
    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    data = pattern.findall(r.json()['response']['parameters']['uri'])[0]
    print(data)
    access_token = data[0]
    print('Access Token: ' + access_token)

    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': "entitlements.auth.riotgames.com",
        'User-Agent': 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)',
        'Authorization': f'Bearer {access_token}',
    }
    r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
    entitlements_token = r.json()['entitlements_token']
    print('Entitlements Token: ' + entitlements_token)

    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': "auth.riotgames.com",
        'User-Agent': 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)',
        'Authorization': f'Bearer {access_token}',
    }

    r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})
    user_id = r.json()['sub']
    # print('User ID: ' + user_id)
    headers['X-Riot-Entitlements-JWT'] = entitlements_token
    del headers['Host']
    session.close()
    return headers, {}, user_id



def getrank(region, user_id):
    return requests.get(f"https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/{region}/{user_id}").json()

def getrank_name(name, tag):
    return requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{name}/{tag}").json()

def getMMRHistory(region, user_id):
    return requests.get(f"https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr-history/{region}/{user_id}").json()

def getMMRHistory_name(name, tag):
    return requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr-history/eu/{name}/{tag}").json()
