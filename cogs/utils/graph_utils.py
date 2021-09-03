import  requests
import re
import aiohttp
import asyncio
import json
import traceback

async def runAPI(username, password):
    async with aiohttp.ClientSession() as session:
        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
        }
        await session.post("https://auth.riotgames.com/api/v1/authorization", json=data)

        data = {"type": "auth", "username": username, "password": password}

        async with session.put(
            "https://auth.riotgames.com/api/v1/authorization", json=data
        ) as r:
            data = await r.json()
        # print(data)
        pattern = re.compile(
            "access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)"
        )
        data = pattern.findall(data["response"]["parameters"]["uri"])[0]
        access_token = data[0]
        # print('Access Token: ' + access_token)
        id_token = data[1]
        expires_in = data[2]

        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        async with session.post(
            "https://entitlements.auth.riotgames.com/api/token/v1",
            headers=headers,
            json={},
        ) as r:
            data = await r.json()
        entitlements_token = data["entitlements_token"]
        # print('Entitlements Token: ' + entitlements_token)

        async with session.post(
            "https://auth.riotgames.com/userinfo", headers=headers, json={}
        ) as r:
            data = await r.json()
        user_id = data["sub"]
        # print('User ID: ' + user_id)
        headers["X-Riot-Entitlements-JWT"] = entitlements_token
        await session.close()

        return user_id, headers

async def parse_stats(name, tag, headers, num_matches=3):
    print(str(name) + str(tag))
    req = requests.get(f"https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}").json()
    print(str(req))
    user_id = req['data']['puuid']
    try:
        async with aiohttp.ClientSession() as session:
            headers["X-Riot-ClientVersion"] = "release-02.01-shipping-6-511946"
            headers[
                "X-Riot-ClientPlatform"
            ] = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
            async with session.get(
                f"https://pd.eu.a.pvp.net/mmr/v1/players/{user_id}/competitiveupdates?startIndex=0&endIndex=10",
                headers=headers,
            ) as r:
                data = json.loads(await r.text())
                
            matches = data["Matches"]
                
            async with session.get(
                f"https://pd.eu.a.pvp.net/mmr/v1/players/{user_id}/competitiveupdates?startIndex=11&endIndex=20",
                headers=headers,
            ) as r:
                data = json.loads(await r.text())

            matches.extend(data["Matches"])
            
            async with session.get(
                f"https://pd.eu.a.pvp.net/mmr/v1/players/{user_id}/competitiveupdates?startIndex=21&endIndex=50",
                headers=headers,
            ) as r:
                data = json.loads(await r.text())
              
            matches.extend(data["Matches"])
            print(str(matches))

            DATA = {}
            count = 0
            for match in matches:
                if match["TierAfterUpdate"] == 0:
                    continue
                else:
                    before = match["RankedRatingBeforeUpdate"]
                    after = match["RankedRatingAfterUpdate"]
                    map_id = match["MatchID"]
                    diff = match["RankedRatingEarned"]
                    DATA[map_id] = {}
                    DATA[map_id]["ranked_rating"] = after

                    if match["TierAfterUpdate"] > match["TierBeforeUpdate"]:  # Promoted
                        DATA[map_id]["movement"] = "PROMOTED"
                    elif (
                        match["TierAfterUpdate"] < match["TierBeforeUpdate"]
                    ):  # Demoted
                        DATA[map_id]["movement"] = "DEMOTED"
                    else:
                        if diff > 0:
                            DATA[map_id]["movement"] = "INCREASE"
                        elif diff < 0:
                            DATA[map_id]["movement"] = "DECREASE"
                        else:
                            DATA[map_id]["movement"] = "STABLE"
                    DATA[map_id]["rating_change"] = diff
                    count += 1
                    DATA[map_id]["competitive_tier"] = match["TierAfterUpdate"]
                    start_time = match["MatchStartTime"] / 1000

                if count >= num_matches:  # [num] recent competitve matches found
                    break

            if count <= 0:
                return
            else:
                return DATA
    except:
        print(traceback.format_exc())
