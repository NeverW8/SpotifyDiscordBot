import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from secrets import TOKEN, client_id, client_secret, redirect_uri, scope

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# function to search Spotify for a track and return the first result
async def search_track(query):
    results = sp.search(q=query, limit=1)
    if len(results["tracks"]["items"]) > 0:
        return results["tracks"]["items"][0]
    else:
        return None


# function to play a track in a voice channel
async def play_track(ctx, track):
    if track is None:
        await ctx.send("Sorry, I couldn't find that track.")
        return

    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    source = track["preview_url"]
    ctx.voice_client.play(discord.FFmpegPCMAudio(source), after=lambda e: print("Player error: %s" % e) if e else None)
    await ctx.send(f"Now playing: {track['name']} by {track['artists'][0]['name']}")


@bot.command()
async def play(ctx, *, query):
    track = await search_track(query)
    await play_track(ctx, track)


@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused playback.")
    else:
        await ctx.send("Nothing is playing.")


@bot.command()
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed playback.")
    else:
        await ctx.send("Playback is not paused.")


@bot.command()
async def stop(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped playback.")
    else:
        await ctx.send("Nothing is playing.")


@bot.command()
async def join(ctx):
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)
    await ctx.send(f"Connected to {voice_channel.name}.")

    # set the timeout for the voice client
    bot_voice_client = ctx.guild.voice_client
    bot_voice_client.activity_timeout = 300  # in seconds


@bot.command()
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")

bot.run(TOKEN)
