import discord
from discord.ext import commands
import json
from discord_components import *
import youtube_dl

with open ('././config/config.json', 'r') as f:
  config = json.load(f, strict=False)
  prefix = config['prefix']


class music(commands.Cog):
  def __init__(self, client):
    self.client = client


    @commands.command(aliases=['p'])
    async def play(self, ctx):
      if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel!")
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
        await voice_channel.connect()
      ctx.voice_client.stop()
      FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
      YDL_OPTIONS = {'format':"bestaudio"}
      
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url]
        source = await dicord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        ctx.voice_client.play(source)
    
    @commands.command(aliases=['d'])
    async def disconnect(self,ctx):
      await ctx.voice_client.disconnect()
                                  
    @commands.command(aliases=['p'])
    async def pause(self,ctx):
      awit ctx.voice_client.pause()
    
    @commands.command(aliases=['r'])
    async def resume(self,ctx):
      awit ctx.voice_client.resume()

def setup(client):
	client.add_cog(music(client))
	print("music      | Imported")   
