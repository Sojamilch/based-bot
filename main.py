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


def read_json():
    with open("minecraft.json", "r") as file:
        loadedJson = json.load(file)

    return loadedJson


@client.event
async def on_guild_join(guild):
    # Literally Useless
    guilds.append(guild)
    print(f'Joined server: {guild.name}')
    print(f'Total Servers: {len(guilds)}')
    await tree.sync(guild=guild)


@tree.command(name='sync-commands', description='Owner only', guild=client.get_guild(TEST_GUILD_ID))
async def sync_commands(interaction: discord.Interaction):
    # Dev command to sync commands across all servers
    if interaction.user.id == OWNER_ID:
        await tree.sync()
        print('Command Tree Synced')
        await interaction.response.send_message("Command Tree Synced...", ephemeral=True)
    else:
        await interaction.response.send_message("You must be the owner to use this command", ephemeral=True)


@tree.command(name='set-server-ip', description='Sets the minecraft server IP & Port')
async def set_server_ip(interaction: discord.Interaction, ip: str = '127.0.0.1', port: int = 25565):

    # Initial setup before player list can be achieved (No IPv6 support)
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must be and Administrator to run this command.", ephemeral=True)
        return

    minecraftServerIps[str(interaction.guild_id)] = {'ip': ip, 'port': port}

    with open('minecraft.json', 'w') as file:
        json.dump(minecraftServerIps, file)

    await interaction.response.send_message(f"Server Set {ip}:{port}", ephemeral=True)


@tree.command(name='get-server-players', description='Gets the players currently on the server')
async def get_server_players(interaction: discord.Interaction):

    guild_id = str(interaction.guild_id)
    try:
        # Gets the list of players via a TCP connection to the server
        players = get_players(
            minecraftServerIps[guild_id]['ip'],
            minecraftServerIps[guild_id]['port']
        )

    except:
        await interaction.response.send_message(f"No Minecraft Server Found @ {minecraftServerIps[guild_id]['ip']}:{minecraftServerIps[guild_id]['port']}", ephemeral=True)
        return

    embed = discord.Embed(title=interaction.guild.name)
    onlinePlayers = ""

    # Creates a list with player names on new lines for discord
    for player in players:
        if (player == "Anonymous Player"):
            continue
        onlinePlayers += f"\n{player['name']}"

    embed.add_field(name="Online Players:", value=onlinePlayers, inline=False)
    await interaction.response.send_message(embed=embed)


@client.event
async def on_ready():

    print(f'Logged in as: {client.user}')
    # Copy and register new commands to dev-server on startup
    tree.copy_global_to(guild=client.get_guild(TEST_GUILD_ID))
    # Move to seperate command to prevent rate-limiting
    await tree.sync(guild=client.get_guild(TEST_GUILD_ID))

    print(f'Caching guilds...')  # Currently has no real use. Just sounds cool
    guilds = [guild async for guild in client.fetch_guilds(limit=150)]
    print(f'Cached {len(guilds)} guilds.')

minecraftServerIps = read_json()
client.run(TOKEN)
