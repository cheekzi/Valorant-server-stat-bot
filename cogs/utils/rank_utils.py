import  requests
import re

def username_to_data(username, password):
    print("lol")
    session = requests.session()
    data = {
        'client_id': 'play-valorant-web-prod',
        'nonce': '1',
        'redirect_uri': 'https://playvalorant.com/opt_in',
        'response_type': 'token id_token',
    }
    r = session.post('https://auth.riotgames.com/api/v1/authorization', json=data)
    print(r)

    data = {
        'type': 'auth',
        'username': username,
        'password': password
    }
    r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data)
    print(r)
    pattern = re.compile(
        'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    data = pattern.findall(r.json()['response']['parameters']['uri'])[0]
    access_token = data[0]
    print(data)

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
    entitlements_token = r.json()['entitlements_token']

    r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})
    user_id = r.json()['sub']

    session.close()
    print([access_token, entitlements_token, user_id])
    return [access_token, entitlements_token, user_id]




def getrank(region, user_id):
    return requests.get(f"https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/{region}/{user_id}").json()

def getrank_name(name, tag):
    return requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{name}/{tag}").json()

def getMMRHistory(region, user_id):
    return requests.get(f"https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr-history/{region}/{user_id}").json()

def getMMRHistory_name(name, tag):
    return requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr-history/eu/{name}/{tag}").json()
