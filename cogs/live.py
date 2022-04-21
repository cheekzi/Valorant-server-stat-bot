import discord
from discord.ext import commands
import requests
import json
from .utils.rank_utils import username_to_data, getrank, getMMRHistory
from .utils.live_utils import get_live, get_names
from discord_components import *

with open('././config/config.json', 'r') as f:
    config = json.load(f, strict=False)
    prefix = config['prefix']


class live(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def live(self, ctx):
        author_id = str(ctx.author.id)

        try:
            user = await self.client.pg_con.fetchrow("SELECT * FROM riotpwd WHERE user_id = $1", author_id)
            username = user['username']
            password = user['password']
            region = user['region']
            try:
                if user:
                    await ctx.send("Loading match...")
                    dic = {
                        0: "Unranked",
                        1: "Unranked",
                        3: "Iron 1",
                        4: "Iron 2",
                        5: "Iron 3",
                        6: "Bronze 1",
                        7: "Bronze 2",
                        8: "Bronze 3",
                        9: "Silver 1",
                        10: "Silver 2",
                        11: "Silver 3",
                        12: "Gold 1",
                        13: "Gold 2",
                        14: "Gold 3",
                        15: "Platin 1",
                        16: "Platin 2",
                        17: "Platin 3",
                        18: "Diamond 1",
                        19: "Diamond 2",
                        20: "Diamond 3",
                        21: "Immortal 1",
                        22: "Immortal 2",
                        23: "Immortal 3",
                        24: "Radiant"
                    }
                    (access_token, entitlements_token, user_id) = username_to_data(username, password)
                    (val, stats) = get_live(region, user_id, access_token, entitlements_token)

                    Players = stats['Players'] if val else stats["AllyTeam"]["Players"]
                    players_puuid = [player['Subject'] for player in Players]
                    players_dic = get_names(players_puuid, access_token, entitlements_token)
                    for player in Players:
                        id = player['Subject']
                        color = player['TeamID'] if val else stats['AllyTeam']['TeamID']
                        rank = getrank(region, id, access_token, entitlements_token)
                        agent_icon = requests.get(f"https://valorant-api.com/v1/agents/{player['CharacterID']}").json()['data']['displayIconSmall'] if player['CharacterID'] else  "https://raw.githubusercontent.com/typhonshambo/Valorant-server-stat-bot/main/assets/valorantRankImg/0.png"
                        mmr_history = getMMRHistory(region, id, access_token, entitlements_token, 3)
                        mmr = []
                        for i in mmr_history['Matches']:
                            change = i["RankedRatingEarned"]
                            mmr.append(f"🔼 {change}") if change >= 0 else mmr.append(f"🔽 {change}")

                        embed = discord.Embed(
                            color=discord.Color.blue() if color == "Blue" else discord.Color.red(),
                            title=dic[rank[0][0]],
                            description=f"**{rank[0][1]} / 100** RR, Peak **{dic[rank[1]]}**"
                        )
                        link_url = f"https://tracker.gg/valorant/profile/riot/{players_dic[id][0]}%23{players_dic[id][1]}/overview"
                        link_url = link_url.replace(" ", "%20")
                        embed.set_author(name=f"{players_dic[id][0]}#{players_dic[id][1]}", url=link_url, icon_url=agent_icon)
                        if mmr:
                            embed.add_field(name="Rank Change", value=" | ".join(mmr), inline=False)
                        embed.set_thumbnail(
                            url=f"https://raw.githubusercontent.com/typhonshambo/Valorant-server-stat-bot/main/assets/valorantRankImg/{rank[0][0]}.png")
                        embed.set_footer(text=f"Level {player['PlayerIdentity']['AccountLevel']}")

                        await ctx.send(embed=embed)


            except Exception as e:
                print(e)
                print(k)
                embed = discord.Embed(
                    color=discord.Color.red()
                )
                embed.add_field(name="SOME ERROR OCCURED...", value="""
                you are `not in a match`""", inline=False)

                embed.set_thumbnail(url="https://i.imgur.com/A45DVhf.gif")
                await ctx.send(
                    embed=embed,
                    components=[
                        [
                            Button(label="Support Server", style=5, url="https://discord.gg/m5mSyTV7RR"),
                            Button(label="Vote", style=5, url="https://top.gg/bot/864451929346539530/vote")
                        ]
                    ]
                )

        except:
            print(k)
            embed = discord.Embed(
                color=discord.Color.red()
            )
            embed.add_field(name="HOLD ON MAN !", value=f"""
            you need to login to your account before you can use this command,
            use `{prefix}login` to login to your account
            """)
            await ctx.send(embed=embed)



def setup(client):
    client.add_cog(live(client))
    print("live         | Imported")