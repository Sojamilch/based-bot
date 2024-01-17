import discord
from discord import app_commands
import os
from dotenv import load_dotenv
from query_server import get_players
import json

load_dotenv()

TOKEN = os.getenv('TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
TEST_GUILD_ID = int(os.getenv('TEST_GUILD_ID'))

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

guilds = []
minecraftServerIps = {}


@client.event
async def on_guild_join(guild):
    guilds.append(guild)
    print(f'Joined server: {guild.name}')
    print(f'Total Servers: {len(guilds)}')
    await tree.sync(guild=guild)


@tree.command(name='sync-commands', description='Owner only')
async def sync_commands(interaction: discord.Interaction):
    if interaction.user.id == OWNER_ID:
        await tree.sync()
        print('Command Tree Synced')
        await interaction.response.send_message("Command Tree Synced...", ephemeral=True)
    else:
        print(type(interaction.user.id), type(OWNER_ID))
        await interaction.response.send_message("You must be the owner to use this command", ephemeral=True)


@tree.command(name='set-server-ip', description='Sets the minecraft server IP & Port')
async def set_server_ip(interaction: discord.Interaction, ip: str = '127.0.0.1', port: int = 25565):

    minecraftServerIps[interaction.guild_id] = {'ip': ip, 'port': port}

    await interaction.response.send_message(f"Added server {ip}:{port}", ephemeral=True)


@tree.command(name='get-server-players', description='Gets the players currently on the server')
async def get_server_players(interaction: discord.Interaction):
    try:
        players = get_players(minecraftServerIps[interaction.guild_id]
                              ['ip'], minecraftServerIps[interaction.guild_id]['port'])

    except:
        await interaction.response.send_message("No Minecraft Server Found...", ephemeral=True)
        return

    embed = discord.Embed(title=interaction.guild.name)
    onlinePlayers = ""
    for player in players:
        if (player == "Anonymous Player"):
            continue
        onlinePlayers += f"\n{player['name']}"

    embed.add_field(name="Online Players:", value=onlinePlayers, inline=False)
    await interaction.response.send_message(embed=embed)


@client.event
async def on_ready():

    print(f'Logged in as: {client.user}')
    tree.copy_global_to(guild=client.get_guild(TEST_GUILD_ID))
    # await tree.sync(guild=client.get_guild(TEST_GUILD_ID))

    # print(f'Caching guilds...')
    # guilds = [guild async for guild in client.fetch_guilds(limit=150)]
    # print(f'Cached {len(guilds)} guilds.')

client.run(TOKEN)