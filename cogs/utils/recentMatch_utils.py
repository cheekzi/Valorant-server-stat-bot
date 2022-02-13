import json
import requests
import re
import aiohttp
from collections import OrderedDict
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

async def GetMatchData(username , tagline):

    
    history_api = f"https://api.tracker.gg/api/v2/valorant/rap-matches/riot/{username}%23{tagline}"
    async with aiohttp.ClientSession() as session:
        async with session.get(history_api) as r:
            data = json.loads(await r.text())

    matches = data["data"]["matches"]
    for match in matches:
        if "modeName" in match["metadata"]:
            if match["metadata"]["modeName"] == "Competitive":
                return match["attributes"]["id"]
    return None

async def match_stats(match_id):
    match_api = f"https://api.tracker.gg/api/v2/valorant/rap-matches/{match_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(match_api, json={}) as r:
            data = (await r.json())["data"]

    MATCH_DATA = {}
    PLAYER_DATA = {}

    red_team = data["segments"][0]
    blue_team = data["segments"][1]
    players = data["segments"][2:12]

    MATCH_DATA["match_info"] = {}
    MATCH_DATA["match_info"]["duration"] = data["metadata"]["duration"]
    MATCH_DATA["match_info"]["start"] = data["metadata"]["dateStarted"]
    MATCH_DATA["match_info"]["map_name"] = data["metadata"]["mapName"]
    MATCH_DATA["match_info"]["map_image_url"] = data["metadata"]["mapImageUrl"]

    MATCH_DATA["Red"] = {}
    MATCH_DATA["Red"]["rounds_won"] = red_team["stats"]["roundsWon"]["displayValue"]
    MATCH_DATA["Red"]["won"] = red_team["metadata"]["hasWon"]

    MATCH_DATA["Blue"] = {}
    MATCH_DATA["Blue"]["rounds_won"] = blue_team["stats"]["roundsWon"]["displayValue"]
    MATCH_DATA["Blue"]["won"] = blue_team["metadata"]["hasWon"]

    for player in players:
        metadata = player["metadata"]
        display_name = metadata["platformInfo"]["platformUserIdentifier"]
        team = metadata["teamId"]
        agent = metadata["agentName"]
        agentImageUrl = metadata["agentImageUrl"]

        stats = player["stats"]
        rank = stats["rank"]["displayValue"]
        score = stats["scorePerRound"]["displayValue"]
        kills = stats["kills"]["displayValue"]
        deaths = stats["deaths"]["displayValue"]
        assists = stats["assists"]["displayValue"]
        kdRatio = stats["kdRatio"]["displayValue"]
        damagePerRound = stats["damagePerRound"]["displayValue"]

        PLAYER_DATA[display_name] = {}
        PLAYER_DATA[display_name]["team"] = team
        PLAYER_DATA[display_name]["agent"] = agent
        PLAYER_DATA[display_name]["agent_image_url"] = agentImageUrl
        PLAYER_DATA[display_name]["rank"] = rank
        PLAYER_DATA[display_name]["score"] = score
        PLAYER_DATA[display_name]["kills"] = kills
        PLAYER_DATA[display_name]["deaths"] = deaths
        PLAYER_DATA[display_name]["assists"] = assists
        PLAYER_DATA[display_name]["kd_ratio"] = kdRatio

    return MATCH_DATA, PLAYER_DATA





