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
    return access_token, entitlements_token, user_id

def getVersion():
    versionData = requests.get("https://valorant-api.com/v1/version")
    versionDataJson = versionData.json()['data']
    final = f"{versionDataJson['branch']}-shipping-{versionDataJson['buildVersion']}-{versionDataJson['version'][-6:]}"
    return final

def priceconvert(skinUuid, offers_data):
    for row in offers_data["Offers"]:
        if row["OfferID"] == skinUuid:
            for cost in row["Cost"]:
                return row["Cost"][cost]
            
    

def skins(entitlements_token, access_token, user_id, region):

    headers = {
        'X-Riot-Entitlements-JWT': entitlements_token,
        'Authorization': f'Bearer {access_token}',
    }

    r = requests.get(f'https://pd.{region}.a.pvp.net/store/v2/storefront/{user_id}', headers=headers)

    skins_data = r.json()
    single_skins = skins_data["SkinsPanelLayout"]["SingleItemOffers"]


    r = requests.get('https://valorant-api.com/v1/weapons/skins')
    content_data = r.json()
    
    r = requests.get('https://valorant-api.com/v1/bundles')
    bundle_data = r.json()



    headers = {
        'X-Riot-Entitlements-JWT': entitlements_token,
        'Authorization': f'Bearer {access_token}',
        'X-Riot-ClientVersion': getVersion(),
        "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
    }

    data = requests.get(f"https://pd.{region}.a.pvp.net/store/v1/offers/", headers=headers)

    offers_data = data.json()


    for row_small in bundle_data['data']:
        if skins_data["FeaturedBundle"]["Bundle"]["DataAssetID"] == row_small['uuid']:
            bundle_image = row_small['displayIcon']
            bundle_name = row_small['displayName']

    daily_reset = skins_data["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]
    
    if daily_reset >= 3600:
        daily_reset_in_ = round(daily_reset / 3600, 0) 
        time_unit = "Hrs"
     
    else:
        daily_reset_in_ = round(daily_reset / 60, 2) 
        time_unit = "Mins"
    
    skins_list = {
        "bundle_name": bundle_name,
        "bundle_image": bundle_image,
        "SingleItemOffersRemainingDurationInSeconds": daily_reset_in_,
        "time_units":time_unit
    }

    skin_counter = 0
   
    for skin in single_skins:
        for row_small in content_data['data']:
            
            if skin in str(row_small):

                if skin_counter == 0:
                    skins_list['skin1_name'] = row_small['displayName']
                    skins_list['skin1_image'] = row_small['displayIcon']
                    skins_list['skin1_price'] = priceconvert(skin, offers_data)
                elif skin_counter == 1:
                    skins_list['skin2_name'] = row_small['displayName']
                    skins_list['skin2_image'] = row_small['displayIcon']
                    skins_list['skin2_price'] = priceconvert(skin, offers_data)
                elif skin_counter == 2:
                    skins_list['skin3_name'] = row_small['displayName']
                    skins_list['skin3_image'] = row_small['displayIcon']
                    skins_list['skin3_price'] = priceconvert(skin, offers_data)
                elif skin_counter == 3:
                    skins_list['skin4_name'] = row_small['displayName']
                    skins_list['skin4_image'] = row_small['displayIcon']
                    skins_list['skin4_price'] = priceconvert(skin, offers_data)
                skin_counter += 1 

    return skins_list


def check_item_shop(username, password):
    user_data = username_to_data(username, password)
    access_token = user_data[0]
    entitlements_token = user_data[1]
    user_id = user_data[2]
    skin_data = skins(entitlements_token, access_token, user_id)
    skin_list = [skin_data["skin1_name"], skin_data["skin2_name"], skin_data["skin3_name"], skin_data["skin4_name"], skin_data["SingleItemOffersRemainingDurationInSeconds"]]
    return skin_list
