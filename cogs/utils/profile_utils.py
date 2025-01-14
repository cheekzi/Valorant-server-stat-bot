import aiohttp
import asyncio
import json
import requests
from collections import OrderedDict
import re
import socket

def username_to_data(username, password):
    headers = OrderedDict({
        'User-Agent': 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)'
    })

    session = requests.session()
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
    # print('User ID: ' + user_id)
    headers['X-Riot-Entitlements-JWT'] = entitlements_token
    del headers['Host']
    session.close()
    return headers, {}, user_id




def getingamename(region, user_id):
    req_data = requests.get(f"https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/{region}/{user_id}") 
    whole_data = req_data.json()

    
    
    return whole_data




async def profile_stats(username, tagline):
    

    profile_api = f"https://api.tracker.gg/api/v2/valorant/standard/profile/riot/{username}%23{tagline}"
    async with aiohttp.ClientSession() as session:
        async with session.get(profile_api, json={}) as r:
            data = (await r.json())["data"]

    user = data["platformInfo"]["platformUserIdentifier"]
    avatarUrl = data["platformInfo"]["avatarUrl"]

    stats = data["segments"][0]["stats"]
    wins = stats["matchesWon"]["displayValue"]
    losses = stats["matchesLost"]["displayValue"]
    win_pct = stats["matchesWinPct"]["displayValue"]
    hs_pct = stats["headshotsPercentage"]["displayValue"]
    kd_ratio = stats["kDRatio"]["displayValue"]
    damagePerRound = stats["damagePerRound"]["displayValue"]
    time_played = stats["timePlayed"]["displayValue"]
    rank = stats["rank"]["metadata"]["tierName"]
    rankIconUrl = stats["rank"]["metadata"]["iconUrl"]

    DATA = dict(
        user=user,
        avatarUrl=avatarUrl,
        wins=wins,
        losses=losses,
        win_pct=win_pct,
        hs_pct=hs_pct,
        kd_ratio=kd_ratio,
        damagePerRound=damagePerRound,
        time_played=time_played,
        rank=rank,
        rankIconUrl=rankIconUrl,
    )

    return DATA

async def loggedInStats(username, tagline):
    profile_api = f"https://api.tracker.gg/api/v2/valorant/standard/profile/riot/{username}%23{tagline}"
    async with aiohttp.ClientSession() as session:
        async with session.get(profile_api, json={}) as r:
            data = (await r.json())["data"]
    
    user = data["platformInfo"]["platformUserIdentifier"]
    avatarUrl = data["platformInfo"]["avatarUrl"]
    
    stats = data["segments"][0]["stats"]
    rank = stats["rank"]["metadata"]["tierName"]
    rankIconUrl = stats["rank"]["metadata"]["iconUrl"]
    time_played = stats["timePlayed"]["displayValue"]
    
    req_data = requests.get(f"https://api.henrikdev.xyz/valorant/v1/account/{username}/{tagline}")
    req_data = req_data.json()
    account_level = req_data["data"]["account_level"]
    
    DATA = dict(
        user=user,
        avatarUrl=avatarUrl,
        rank=rank,
        rankIconUrl=rankIconUrl,
        account_level=account_level,
        time_played=time_played,
    )

    return DATA
    
