import discord
import os
from discord.ext import commands
from bs4 import BeautifulSoup

TOKEN = ''
PREFIX = '?'
HTML_FOLDER = 'html'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} online')
    try:
        synced = await bot.tree.sync()
        print(f'📌 {len(synced)} slash commands synced.')
    except Exception as e:
        print(f'Erro ao sincronizar: {e}')
    print('-----')

# ---- FUNCTIONS ----
def load_links():
    links_elamigos = []
    links_steamrip = []

    if not os.path.exists(HTML_FOLDER):
        os.makedirs(HTML_FOLDER)

    for filename in os.listdir(HTML_FOLDER):
        if filename.endswith('.html'):
            filepath = os.path.join(HTML_FOLDER, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                for link in soup.find_all('a', href=True):
                    link_text = link.get_text(strip=True)
                    link_url = link['href'].strip()

                    if not link_url.startswith('https://'):
                        link_url = f'https://steamrip.com{link_url}'

                    if link_url.startswith('https://elamigos.site'):
                        links_elamigos.append(f"[{link_text}]({link_url})")
                    if link_url.startswith('https://steamrip.com'):
                        links_steamrip.append(f"[{link_text}]({link_url})")

                    
    
    return links_elamigos, links_steamrip

# ---- SLASH COMMANDS ----
@bot.tree.command(name='search', description='Offline database search for cracked games.')
async def search(interaction: discord.Interaction, input: str):
    await interaction.response.defer(thinking=True)

    links_elamigos, links_steamrip = load_links()
    input = input.lower()
    results_elamigos = [link for link in links_elamigos if input in link.lower()]
    results_steamrip = [link for link in links_steamrip if input in link.lower()]

    if not results_elamigos and not results_steamrip:
        await interaction.response.send_message('Oops! I couldnt find any results :(')
        return

    embed = discord.Embed(title=f"🔎 Results for '{input}'", color=discord.Color.green())
    if results_elamigos:
        embed.add_field(name='🌐 ELAMIGOS', value='\n'.join(results_elamigos[:5]), inline=False)
    if results_steamrip:
        embed.add_field(name='🔥 STEAMRIP', value='\n'.join(results_steamrip[:5]), inline=False)


    await interaction.followup.send(embed=embed)


bot.run(TOKEN)