import nextcord
from nextcord.ext import tasks, commands
from nextcord import Interaction, SlashOption
import itertools
import aiohttp
import random
import json

# Lesen der Konfigurationsdatei und Laden der Daten in das config-Dictionary
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Festlegen der Intents für den Bot, um Nachrichten und Nachrichteninhalte zu erhalten
intents = nextcord.Intents.default()
intents.messages = True
intents.message_content = True

# Erstellen einer Bot-Instanz mit den oben festgelegten Intents
bot = commands.Bot(intents=intents)

# Extrahieren von Informationen aus der Konfigurationsdatei
discord_token = config['token']  # Token aus der Konfigurationsdatei 
guild_id = int(config['guild_id'])  # Guild-ID aus der Konfigurationsdatei 
service_id = config['service_id']  # service_id aus der Konfigurationsdatei 
api_token = config['api_token']  # api_token aus der Konfigurationsdatei 
allowed_user_id = config['allowed_user_id']  # allowed_user_id aus der Konfigurationsdatei 

# Liste von Statusmeldungen für den Bot
statuses = ["Le Datalachs"]

# Funktion zum Ausführen von API-Aktionen
async def execute_api_action(action):
    async with aiohttp.ClientSession() as session:
        api_url = f"https://backend.datalix.de/v1/service/{service_id}/{action}?token={api_token}"
        async with session.post(api_url) as response:
            return await response.text()

# Slash-Befehl zum Starten des Servers
@bot.slash_command(name="start", description="Startet den Server", guild_ids=[guild_id])
async def start(interaction: nextcord.Interaction):
    if interaction.user.id == allowed_user_id:
        await interaction.response.send_message("Starte Server...")
        response = await execute_api_action("start")
        await interaction.followup.send(f"Server gestartet: {response}")
    else:
        await interaction.response.send_message("Die Durchführung dieser Aktion setzt eine vorherige Genehmigung voraus, die im vorliegenden Fall für Ihre Benutzeridentifikation nicht verzeichnet ist.")

# Slash-Befehl zum Stoppen des Servers
@bot.slash_command(name="stop", description="Stoppt den Server")
async def stop(interaction: nextcord.Interaction):
    if interaction.user.id == allowed_user_id:
        await interaction.response.send_message("Stoppe Server...")
        response = await execute_api_action("stop")
        await interaction.followup.send(f"Server gestoppt: {response}")
    else:
        await interaction.response.send_message("Die Durchführung dieser Aktion setzt eine vorherige Genehmigung voraus, die im vorliegenden Fall für Ihre Benutzeridentifikation nicht verzeichnet ist.")

# Slash-Befehl zum Herunterfahren des Servers
@bot.slash_command(name="shutdown", description="Fährt den Server herunter")
async def shutdown(interaction: nextcord.Interaction):
    if interaction.user.id == allowed_user_id:
        await interaction.response.send_message("Fahre Server herunter...")
        response = await execute_api_action("shutdown")
        await interaction.followup.send(f"Server heruntergefahren: {response}")
    else:
        await interaction.response.send_message("Die Durchführung dieser Aktion setzt eine vorherige Genehmigung voraus, die im vorliegenden Fall für Ihre Benutzeridentifikation nicht verzeichnet ist.")

# Slash-Befehl zum Neustarten des Servers
@bot.slash_command(name="reboot", description="Reboot den Server", guild_ids=[guild_id])
async def reboot(interaction: nextcord.Interaction):
    if interaction.user.id == allowed_user_id:
        await interaction.response.send_message("Reboote Server...")
        response = await execute_api_action("restart")
        await interaction.followup.send(f"Server rebootet: {response}")
    else:
        await interaction.response.send_message("Die Durchführung dieser Aktion setzt eine vorherige Genehmigung voraus, die im vorliegenden Fall für Ihre Benutzeridentifikation nicht verzeichnet ist.")

# Slash-Befehl zur Anzeige der Bot-Ping-uhrzeit .-.
@bot.slash_command(name="ping", description="Zeigt die Latenz des Bots")
async def ping(interaction: nextcord.Interaction):
    latency = round(bot.latency * 1000)
    embed = nextcord.Embed(
        title="Bot Ping",
        description=f'Die aktuelle Latenz des Bots beträgt: {latency}ms',
        color=nextcord.Color.blue()
    )
    embed.add_field(name="API Latenz:", value=f'{latency}ms', inline=True)
    current_date = nextcord.utils.utcnow().strftime('%d.%m.%Y')
    embed.set_footer(text=f"Aktuelles Datum: {current_date}")
    await interaction.response.send_message(embed=embed)

# Slash-Befehl zur Anzeige von Informationen über DDOS-Angriffe
@bot.slash_command(name="ddos", description="Zeigt Informationen über DDOS-Angriffe", guild_ids=[guild_id])
async def ddos(interaction: nextcord.Interaction):
    if interaction.user.id == allowed_user_id:
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            api_url = f"https://backend.datalix.de/v1/service/{service_id}/incidents?token={api_token}"
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    incidents = data.get("data", [])
                    if incidents:
                        sorted_incidents = sorted(incidents, key=lambda x: float(x['mbps']), reverse=True)
                        biggest_attack = sorted_incidents[0]
                        last_attack = incidents[-1]
                        weakest_attack = sorted_incidents[-1]
                        embed = nextcord.Embed(title="DDOS", description="DDOS-Angriffe", color=nextcord.Color.blue())
                        embed.add_field(name="Big Attack", value=f"IP: {biggest_attack['ip']}\nMBps: {biggest_attack['mbps']}\nPPS: {biggest_attack['pps']}\nMethode: {biggest_attack['method']}", inline=False)
                        embed.add_field(name="Latest Attack", value=f"IP: {last_attack['ip']}\nMBps: {last_attack['mbps']}\nPPS: {last_attack['pps']}\nMethode: {last_attack['method']}", inline=False)
                        embed.add_field(name="SKID Attack", value=f"IP: {weakest_attack['ip']}\nMBps: {weakest_attack['mbps']}\nPPS: {weakest_attack['pps']}\nMethode: {weakest_attack['method']}", inline=False)
                        await interaction.followup.send(embed=embed)
                    else:
                        empty_embed = nextcord.Embed(title="DDOS", description="Aktuell liegen keine DDOS-Angriffsdaten vor.", color=nextcord.Color.blue())
                        await interaction.followup.send(embed=empty_embed)
                else:
                    await interaction.followup.send("Fehler beim Abrufen der DDOS-Angriffsdaten. Bitte versuche es später erneut.")
    else:
        await interaction.response.send_message("Du hast keine Berechtigung, diesen Befehl auszuführen.", ephemeral=True)

# Aufgabe zum Ändern des Bot-Status alle 10 Sekunden
@tasks.loop(seconds=10)
async def change_status():
    current_status = next(bot.status_cycle)
    await bot.change_presence(activity=nextcord.Game(name=current_status))

@bot.event
async def on_ready():
    print(f'Bot ist eingewählt als {bot.user.name}')
    bot.status_cycle = itertools.cycle(statuses)
    change_status.start()

# Starten des Bots mit dem Discord-Token
bot.run(discord_token)
