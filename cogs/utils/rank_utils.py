import requests
from collections import OrderedDict
import re
import socket
import ssl
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
    data = {
        'type': 'auth',
        'username': username,
        'password': password
    }
    r = session.put(f'https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')

    data = pattern.findall(r.json()['response']['parameters']['uri'])[0]
    access_token = data[0]


    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': "entitlements.auth.riotgames.com",
        'User-Agent': 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)',
        'Authorization': f'Bearer {access_token}',
    }
    r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
    entitlements_token = r.json()['entitlements_token']

    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': "auth.riotgames.com",
        'User-Agent': 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)',
        'Authorization': f'Bearer {access_token}',
    }

    r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})
    user_id = r.json()['sub']
    #print('User ID: ' + user_id)
    session.close()
    return access_token, entitlements_token, user_id



def getrank(region, user_id, access_token, entitlements_token):
    version = requests.get("https://valorant-api.com/v1/version").json()
    headers = {
        'Authorization': f"Bearer {access_token}",
        'X-Riot-Entitlements-JWT': entitlements_token,
        'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
        'X-Riot-ClientVersion': version['data']['riotClientVersion'],
        "User-Agent": "RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)"
    }
    ranks = requests.get(f"https://pd.{region}.a.pvp.net/mmr/v1/players/{user_id}", headers=headers).json()
    seasons = requests.get(f"https://shared.{region}.a.pvp.net/content-service/v3/content", headers=headers).json()
    max_rank = 0
    current_rank = (0, 0)

    for season in seasons["Seasons"]:
        if not ranks["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]:
            return ((0, 0), 0)
        if season["ID"] not in ranks["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]:
            continue
        if season["IsActive"]:
            current_rank = (ranks["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season["ID"]]["CompetitiveTier"], ranks["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season["ID"]]["RankedRating"])
        if ranks["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season["ID"]]["CompetitiveTier"] > max_rank:
            max_rank = ranks["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season["ID"]]["CompetitiveTier"]
    return (current_rank, max_rank)

def getrank_name(name, tag):
    return requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{name}/{tag}").json()

def getMMRHistory(region, user_id, access_token, entitlements_token, range):
    headers = {
        'Authorization': f"Bearer {access_token}",
        'X-Riot-Entitlements-JWT': entitlements_token,
        'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
        "User-Agent": "RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)"
    }
    mmr_history = requests.get(f"https://pd.{region}.a.pvp.net/mmr/v1/players/{user_id}/competitiveupdates?queue=competitive&endIndex={range}", headers=headers).json()
    return mmr_history

def getMMRHistory_name(name, tag):
    return requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr-history/eu/{name}/{tag}").json()

