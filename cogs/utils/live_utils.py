import requests


def get_live(region, user_id, access_token, entitlements_token):
    version = requests.get("https://valorant-api.com/v1/version").json()
    headers = {
        'Authorization': f"Bearer {access_token}",
        'X-Riot-Entitlements-JWT': entitlements_token
    }

    try:
        match_id = requests.get(f"https://glz-{region}-1.{region}.a.pvp.net/core-game/v1/players/{user_id}", headers=headers).json()['MatchID']
        return (True, requests.get(f"https://glz-{region}-1.{region}.a.pvp.net/core-game/v1/matches/{match_id}", headers=headers).json())
    except:
        match_id = requests.get(f"https://glz-{region}-1.{region}.a.pvp.net/pregame/v1/players/{user_id}", headers=headers).json()['MatchID']
        return (False, requests.get(f"https://glz-{region}-1.{region}.a.pvp.net/pregame/v1/matches/{match_id}", headers=headers).json())


def get_names(user_ids, access_token, entitlements_token):
    headers = {
        'Authorization': f"Bearer {access_token}",
        'X-Riot-Entitlements-JWT': entitlements_token
    }

    res = requests.put(f"https://pd.eu.a.pvp.net/name-service/v2/players", headers=headers, json=user_ids).json()
    return {player["Subject"]: (player['GameName'], player['TagLine']) for player in res}