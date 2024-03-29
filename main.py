import discord
from discord import app_commands
import os
from dotenv import load_dotenv
from query_server import get_server
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

    await interaction.response.defer()
    guild_id = str(interaction.guild_id)
    server = {}

    # Gets the list of players via a TCP connection to the server
    server = await get_server(
        minecraftServerIps[guild_id]['ip'],
        minecraftServerIps[guild_id]['port']
    )

    # if not server:
    #     await interaction.followup.send(f"No Minecraft Server Found @ {minecraftServerIps[guild_id]['ip']}:{minecraftServerIps[guild_id]['port']}")
    #     return
    # elif
    #    await interaction.followup.send(f"Noone is home @{minecraftServerIps[guild_id]['ip']}:{minecraftServerIps[guild_id]['port']}")
    #    return

    if not server:
        await interaction.followup.send(embed=create_server_embed())
        return

    serverStatus = ":green_square:"
    serverVersion = server['version']['name']
    onlinePlayers = ""

    # Creates a list with player names on new lines for discord
    if server['players']['online'] > 0:
        for player in server['players']['sample']:
            # if (player['name'] != "Anonymous Player"):
            onlinePlayers += f"\n{player['name']}"
    else:
        onlinePlayers = ":cricket:"

    await interaction.followup.send(embed=create_server_embed(serverVersion, serverStatus, onlinePlayers, interaction.guild.name))


def create_server_embed(serverVersion="", serverStatus=":red_square:", onlinePlayers=":cricket:", guildName="Server Offline"):

    embed = discord.Embed(title=guildName)

    embed.add_field(name="Server Version:",
                    value=serverVersion, inline=False)
    embed.add_field(name="Server Status: ",
                    value=serverStatus, inline=True)

    embed.add_field(name="Online Players:", value=onlinePlayers, inline=False)
    return embed


@client.event
async def on_ready():

    print(f'Logged in as: {client.user}')
    # Copy and register new commands to dev-server on startup
    tree.copy_global_to(guild=client.get_guild(TEST_GUILD_ID))
    # Move to seperate command to prevent rate-limiting
    await tree.sync(guild=client.get_guild(TEST_GUILD_ID))

    print(f'Caching guilds...')  # Currently has no real use. Just sounds cool
    # guilds = [guild async for guild in client.fetch_guilds(limit=150)]
    print(f'Cached {len(guilds)} guilds.')

minecraftServerIps = read_json()
client.run(TOKEN)
