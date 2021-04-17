from discord.ext.commands.errors import CommandInvokeError, CommandNotFound
import requests
import json
from discord.ext import commands, tasks
import discord
import os

refresh_time = 5

url = 'https://twitter.com/i/api/2/timeline/media/96900937.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&send_error_codes=true&simple_quoted_tweet=true&count=20&ext=mediaStats%2ChighlightedLabel'

def bypass_authenication():
    authentication_url = 'https://api.twitter.com/1.1/guest/activate.json'
    auth_header = {
        'Host': 'api.twitter.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'authorization': os.environ.get('BEARER_TOKEN'),
        'content-type': 'application/x-www-form-urlencoded',
        'Origin': 'https://twitter.com',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'TE': 'Trailers'
    }
    response = requests.post(authentication_url, headers=auth_header)
    return response.content.decode('utf-8')


headers = {
    'Host': 'twitter.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'content-type': 'application/x-www-form-urlencoded',
    'authorization': os.environ.get('BEARER_TOKEN'),
    'x-guest-token': '1341730556556427265',
    'x-twitter-client-language': 'en',
    'x-twitter-active-user': 'yes',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'TE': 'Trailers',
}


def invite_embed():
    embed = discord.Embed(title='R.O.C.E Invite',
                          url='https://discord.com/api/oauth2/authorize?client_id=791616714570858496&permissions=1073769536&scope=bot',
                          description='Invite R.O.C.E on your server.')
    return embed

def source_embed():
    source_code = 'https://github.com/0x0is1/R.O.C.E'
    embed = discord.Embed(title='R.O.C.E Source code',
                          url=source_code,
                          description='Get R.O.C.E Source Code.')
    return embed

def register_text_channel(channel_id, status, regkey):
    activation_info = json.load(open('info.json', 'r'))
    if regkey == 'reg':
        activation_info[0][str(channel_id)] = str(status)
    if regkey == 'dereg':
        activation_info[0].pop(str(channel_id))
    
    with open('info.json', 'w') as filename:
        json.dump(activation_info, filename)

def fetch_n_parse_data():
    response = requests.get(url, headers=headers)
    data = response.content.decode('utf-8')
    parsed_data = json.loads(data)['globalObjects']['tweets']
    return parsed_data

def sort_data():
    return json.dumps(fetch_n_parse_data(), sort_keys=True)


def help_embed():
    embed = discord.Embed(title="Rational Operative Communication Entity", color=0x03f8fc)
    embed.add_field(
        name="Description:", value="This bot is designed for NEWS distribution over discord servers.", inline=False)
    embed.add_field(
        name="**Commands:**\n", value="`enable` : Command used for enabling news bot in this channel. \n `disable` : Command used for disabling news bot in this channel.", inline=False)
    embed.add_field(
        name="Invite: ", value="You can get invite link by typing `invite`")
    embed.add_field(
        name="Source: ", value="You can get source code by typing `source`")
    embed.add_field(
        name="Credits: ", value="You can get credits info by typing `credits`")
    return embed

def set_status_res_emb(status):
    embed = discord.Embed(color=0x03f8fc)
    embed.add_field(name='Status',
                    value='`{}`'.format(status), inline=False)
    return embed

previous_tweet_id = ''
bot = commands.Bot(command_prefix=';')
bot.remove_command('help')

@bot.command(name="help", description="Returns all commands available")
@commands.has_role('starks')
async def help(ctx):
    embed = help_embed()
    await ctx.send(embed=embed)

@tasks.loop(seconds=refresh_time)
async def main_fun():
    global previous_tweet_id
    global refresh_time
    try:
        last_tweet = list(json.loads(sort_data()).values())[19]
        if last_tweet['id_str'] != previous_tweet_id:
            embed = discord.Embed(title='ROCE News', color=0x03f8fc)
            text = last_tweet['full_text'].split('https://')[0]
            img_url = last_tweet['entities']['media'][0]['media_url_https']
            dhurl = last_tweet['entities']['urls'][0]['url']
            hurl= last_tweet['entities']['urls'][0]['expanded_url']
            embed.add_field(name='Headline', value=text, inline=False)
            embed.set_image(url=img_url)
            embed.add_field(name='Visit for more:', value='[{}]({})'.format(dhurl, hurl))
            channels = json.load(open('info.json', 'r'))[0]
            channel_ids = list(channels.keys())
            for channel_id in channel_ids:
                if channels[channel_id] == 'ON':
                    channel_ob = bot.get_channel(int(channel_id))
                    await channel_ob.send(embed=embed)
            previous_tweet_id = last_tweet['id_str']
            
    except KeyError:
        print('Reauthorizing Headers.')
        headers['x-guest-token'] = json.loads(bypass_authenication())['guest_token']
        print('Completed.')

    except requests.exceptions.SSLError:
        refresh_time = 10

@bot.command()
@commands.has_role('starks')
async def invite(ctx):
    embed=invite_embed()
    await ctx.send(embed=embed)


@bot.command()
@commands.has_role('starks')
async def status(ctx):
    channel_id = ctx.message.channel.id
    channels = json.load(open('info.json', 'r'))[0]
    channel_ids = list(channels.keys())
    if str(channel_id) in channel_ids:
        embed = discord.Embed(color=0x03f8fc)
        embed.add_field(name='Status: ', value=channels[str(channel_id)], inline=False)
        await ctx.send(embed=embed)


@bot.command()
@commands.has_role('starks')
async def deregister(ctx):
    channel_id = ctx.message.channel.id
    channels = json.load(open('info.json', 'r'))[0]
    channel_ids = list(channels.keys())
    if str(channel_id) in channel_ids:
        register_text_channel(str(channel_id), '', 'dereg')
        embed = discord.Embed(color=0x03f8fc)
        embed.add_field(name='Info: ',
                        value='This channel is no more subscribed for R.O.C.E \n Use `enable` or `disable` commands to resubscribe.', inline=False)
        await ctx.send(embed=embed)

@bot.command()
@commands.has_role('starks')
async def source(ctx):
    embed = source_embed()
    await ctx.send(embed=embed)


@bot.command()
@commands.has_role('starks')
async def credits(ctx):
    embed = discord.Embed(
        title="R.O.C.E: \n Rational Operative Communication Entity", color=0x03f8fc)
    embed.add_field(name='Developed by ', value='0x0is1', inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_role('starks')
async def ping(ctx):
    await ctx.send('Pong! `{}ms`'.format(round(bot.latency * 1000)))

@bot.event
async def on_ready():
    print('Bot status: Online.')
    main_fun.start()

pre_reaction_message_id = 0

@bot.command()
@commands.has_role('starks')
async def enable(ctx):
    channel_id = ctx.message.channel.id
    register_text_channel(channel_id, 'ON', 'reg')
    await ctx.message.add_reaction('✅')

@bot.command()
@commands.has_role('starks')
async def disable(ctx):
    channel_id = ctx.message.channel.id
    register_text_channel(channel_id, 'OFF', 'reg')
    await ctx.message.add_reaction('✅')

@disable.error
async def disable_error(ctx, error):
    await ctx.send('`Access Denied.` \n Please be the `starks` to use this command.')

@enable.error
async def enable_error(ctx, error):
    await ctx.send('`Access Denied.` \n Please be the `starks` to use this command.')

@deregister.error
async def enable_error(ctx, error):
    await ctx.send('`Access Denied.` \n Channel is not registered previously. \n use `enable` or `disable` command to register.')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send('`Unknown command` \n Please use right command to operate. `help` for commands details.')
    if isinstance(error, CommandInvokeError):
        return

auth_token = os.environ.get('ROCE_BOT_TOKEN')
bot.run(auth_token)
#print(bypass_authenication())
