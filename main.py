import discord
import os
import json
import re
import requests
from discord.ext import commands
from bs4 import BeautifulSoup

with open("./config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)

TOKEN = config["TOKEN"]
PREFIX = config["PREFIX"]
HTML_FOLDER = config["HTML_FOLDER"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"🤖 {bot.user} online")
    try:
        synced = await bot.tree.sync()
        print(f"📌 {len(synced)} slash commands synced.")
    except Exception as e:
        print(f"Sync error: {e}")
    print("-----")


# ---- FUNCTIONS ----
def load_links():
    links_elamigos = []
    links_steamrip = []
    links_dodi = []

    # FOR OTHERS
    if not os.path.exists(HTML_FOLDER):
        os.makedirs(HTML_FOLDER)

    for filename in os.listdir(HTML_FOLDER):
        if filename.endswith(".html"):
            filepath = os.path.join(HTML_FOLDER, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
                for link in soup.find_all("a", href=True):
                    link_text = link.get_text(strip=True)
                    link_url = link["href"].strip()

                    if not link_url.startswith("https://"):
                        link_url = f"https://steamrip.com{link_url}"

                    if link_url.startswith("https://elamigos.site"):
                        links_elamigos.append(f"[{link_text}]({link_url})")
                    elif link_url.startswith("https://steamrip.com"):
                        links_steamrip.append(f"[{link_text}]({link_url})")
                    elif link_url.startswith("https://dodi-repacks.site"):
                        links_dodi.append(f"[{link_text}]({link_url})")

    return links_elamigos, links_steamrip, links_dodi


# ---- SLASH COMMANDS ----
@bot.tree.command(
    name="search-games", description="Offline database search for cracked games."
)
async def search(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)

    # FORMATTING QUERY
    if re.search(r"[@#$%^*]", query):
        await interaction.followup.send("Special characters are not allowed.")
        return

    # FOR FITGIRL
    results_fitgirl = []
    search_query = query.replace(" ", "+")

    url = f"https://fitgirl-repacks.site/?s={search_query}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            for post in soup.find_all("article"):
                title_tag = post.find("h1", class_="entry-title")
                if title_tag:
                    link = title_tag.find("a", href=True)
                    link_text = link.get_text(strip=True)
                    link_url = link["href"].strip()

                    if not link_url.startswith("https://"):
                        link_url = f"https://fitgirl-repacks.site{link_url}"

                    if query.lower() in link_text.lower():
                        results_fitgirl.append(f"[{link_text}]({link_url})")
        else:
            print("ERROR: Could not connect to https://fitgirl-repacks.site/")
    except requests.RequestException:
        print("ERROR: Could not connect to https://fitgirl-repacks.site/")

    # FOR OTHERS
    links_elamigos, links_steamrip, links_dodi = load_links()
    query = query.lower()
    results_elamigos = [link for link in links_elamigos if query in link.lower()]
    results_steamrip = [link for link in links_steamrip if query in link.lower()]
    results_dodi = [link for link in links_dodi if query in link.lower()]

    if (
        not results_elamigos
        and not results_steamrip
        and not results_dodi
        and not results_fitgirl
    ):
        await interaction.followup.send(
            f"Oops! I couldnt find any results for '{query}' :("
        )
        return

    # EMOJIS - Change to your own ids or just use regular emojis on field names
    elamigos_emoji = config["ELAMIGOS_EMOJI"]
    steamrip_emoji = config["STEAMRIP_EMOJI"]
    dodi_emoji = config["DODI_EMOJI"]
    fitgirl_emoji = config["FITGIRL_EMOJI"]

    embed = discord.Embed(
        title=f"🔎 Results for '{query}'", color=discord.Color.dark_gray()
    )
    if results_elamigos:
        embed.add_field(
            name=f"{elamigos_emoji} ELAMIGOS",
            value="\n".join(f"- {game}" for game in results_elamigos[:3]),
            inline=False,
        )
    if results_steamrip:
        embed.add_field(
            name=f"{steamrip_emoji} STEAMRIP",
            value="\n".join(f"- {game}" for game in results_steamrip[:3]),
            inline=False,
        )
    if results_dodi:
        embed.add_field(
            name=f"{dodi_emoji} DODI REPACKS",
            value="\n".join(f"- {game}" for game in results_dodi[:3]),
            inline=False,
        )
    if results_fitgirl:
        embed.add_field(
            name=f"{fitgirl_emoji} FITGIRL REPACKS (online-search)",
            value="\n".join(f"- {game}" for game in results_fitgirl[:3]),
            inline=False,
        )

    await interaction.followup.send(embed=embed)


@bot.tree.command(
    name="search-movies", description="Online database search for torrent movies."
)
async def search_movies(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)

    results = []

    # FORMATING query
    if re.search(r"[@#$%^*]", query):
        await interaction.followup.send("Special characters are not allowed.")
        return
    search_query = query.replace(" ", "%20")
    dot_query = query.replace(" ", ".")

    # REQUESTING
    url = f"https://www.1377x.to/search/{search_query}/1/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                link_text = link.get_text(strip=True)
                link_url = link["href"].strip()

                if not link_url.startswith("https://"):
                    link_url = f"https://www.1377x.to{link_url}"

                if (
                    query.lower() in link_text.lower()
                    or dot_query.lower() in link_text.lower()
                ):
                    results.append(f"[{link_text}]({link_url})")
        else:
            await interaction.followup.send(
                "Error while accessing 1337x. Try again later."
            )
            return
    except requests.RequestException:
        await interaction.followup.send(
            "⚠️ Could not connect to 1337x. Try again later."
        )
        return

    if not results:
        await interaction.followup.send(
            f"No movies found for '{query}'.\n**Warning:** 1337x uses a bad search engine, try using single words."
        )
        return

    embed = discord.Embed(
        title=f"🎬 Movies results for '{query}'",
        description="\n".join(results[:5]),
        color=discord.Color.dark_gray(),
    )

    await interaction.followup.send(embed=embed)


@bot.tree.command(
    name="top-games", description="shows the most played games on steam at the moment."
)
async def top_games(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    url = "https://steamcharts.com/top"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            games = []
            for row in soup.select("tr")[1:11]:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    rank = cols[0].text.strip()
                    name = cols[1].text.strip()
                    players = cols[2].text.strip()

                    games.append(f"**{rank}** {name} - 🎮 {players} players")
                else:
                    await interaction.followup.send(
                        "Steamcharts changed it's structure, pls contact `politicalizando`"
                    )
                    return
        else:
            await interaction.followup.send(
                "Could not fetch data from https://steamcharts.com/top"
            )
            return
    except requests.RequestException:
        await interaction.followup.send(
            "Could not connect to https://steamcharts.com/top"
        )
        return

    embed = discord.Embed(
        title="🔥 Top 10 most played games on Steam",
        description="\n".join(games),
        url="https://steamcharts.com/top",
        color=discord.Color.dark_gray(),
    )
    embed.set_footer(text="Get them with `/search-games`!")

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="games", description="Popular websites for cracked games.")
async def games(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    embed = discord.Embed(
        title="Cracked Games Websites", color=discord.Color.dark_gray()
    )
    embed.add_field(  # DDL
        name="Direct Download Links (DDL)",
        value="- [SteamRIP](https://steamrip.com/)\n"
        "- [ElAmigos](https://elamigos.site/)",
        inline=False,
    )
    embed.add_field(  # Torrents
        name="Torrents (Repacks)",
        value="- [Fitgirl](https://fitgirl-repacks.site/popular-repacks/)\n"
        "- [Dodi](https://dodi-repacks.site/)",
        inline=False,
    )

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="emulators", description="Popular emulators and roms websites.")
async def emulators(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    embed = discord.Embed(
        title="Emulators and Roms Popular Websites", color=discord.Color.dark_gray()
    )
    embed.add_field(
        name="Multisystem",
        value="- [OpenEmu](https://openemu.org/) - MacOS\n"
        "- [RetroArch](https://www.retroarch.com/) - Windows\n"
        "- [Retrodeck](https://retrodeck.net/) - Linux",
        inline=False,
    )
    embed.add_field(
        name="Microsoft", value="- [Xenia](https://xenia.jp/) - Xbox 360", inline=False
    )
    embed.add_field(
        name="Sony",
        value="- [DuckStation](https://www.duckstation.org/) - PS1\n"
        "- [PCSX2](https://pcsx2.net/) - PS2\n"
        "- [RPCS3](https://rpcs3.net/) - PS3\n"
        "- [PPSSPP](https://www.ppsspp.org/) - PSP\n"
        "- [VITA3K](https://vita3k.org/) - PSVITA",
        inline=False,
    )
    embed.add_field(
        name="Nintendo",
        value="- [SNES9X](https://www.snes9x.com/) - SNES\n"
        "- [MGba](https://mgba.io/) - Game Boy Advance\n"
        "- [Suyu](https://suyu.dev/) - Switch\n"
        "- [Torzu](https://torzu.dev/) - Switch",
        inline=False,
    )
    embed.add_field(
        name="Roms",
        value="- [GameGinie](https://www.gameginie.com/)\n"
        "- [ROMSPURE](https://romspure.cc/) - Over 30,000 verified roms.\n"
        "- [RomHacking](https://www.romhacking.net/) - Hub for roms modifications.\n"
        "- [ConsoleRoms](https://www.consoleroms.com/) - Console roms and emulators.\n"
        "- [Vimms Lair](https://vimm.net/)",
        inline=False,
    )

    await interaction.followup.send(embed=embed)


@bot.tree.command(
    name="softwares",
    description="A selection of good websites for downloading cracked softwares.",
)
async def softwares(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    embed = discord.Embed(
        title="Cracked Softwares",
        description="- [AudioZ](https://audioz.download/) - Music production softwares\n"
        '- [Cracksurl](https://cracksurl.com/) - "The ultimate software hub"\n'
        "- [Monkrus](https://w16.monkrus.ws/) - All Adobe softwares",
        color=discord.Color.dark_gray(),
    )

    await interaction.followup.send(embed=embed)


@bot.tree.command(
    name="books", description="Popular websites for downloading and reading books."
)
async def books(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = discord.Embed(
        title="Free Books for Download", color=discord.Color.dark_gray()
    )
    embed.add_field(
        name="Browser Reading",
        value="- [Read Comic Online](https://readcomiconline.li/) - Free and online comics.\n"
        "- [Novel Buddy](https://novelbuddy.com/official) - Light novels.",
        inline=False,
    )
    embed.add_field(
        name="Direct Download Links (DDL)",
        value="- [Z-Lib](https://z-library.sk/) - Most popular online library.\n"
        "- [Z-Lib #2](https://z-lib.io/)\n"
        "- [Annas Archive](https://Annas-archive.org)\n"
        "- [Archive Organization](https://archive.org/)\n"
        "- [LibGen](https://libgen.mx)\n"
        "- [PdfDrive](https://pdfdrive.com)\n"
        "- [GetComics](https://getcomics.org/)",
        inline=False,
    )
    embed.add_field(
        name="Manga",
        value="- [MangaBuddy](https://mangabuddy.com/) - Huge database.\n"
        "- [MangaFire](https://mangafire.to/)",
        inline=False,
    )
    embed.add_field(
        name="IMPORTANT NOTE", value="Try also searching for `<bookname> PDF`"
    )

    await interaction.followup.send(embed=embed)


@bot.tree.command(
    name="media", description="Websites for watching online movies for free."
)
async def media(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    embed = discord.Embed(title="Free Media", color=discord.Color.dark_gray())
    embed.add_field(
        name="Online",
        value="- [Hura Watch](https://hurawatch.cc/home)\n"
        "- [Alphatron](https://alphatron.tv/)\n"
        "- [123Netmovies](https://123netmovies.com/)",
        inline=False,
    )
    embed.add_field(
        name="Torrent or DDL",
        value="- [Ashutosh Git Page](https://github.com/Ashutoshwahane/TorrentFiles/)\n"
        "- [FMHY](https://fmhy.pages.dev/torrentpiracyguide#torrent-sites)\n"
        "- [1337x](https://www.1377x.to/popular-movies) - Best one.",
        inline=False,
    )

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="vpns", description="Unordened list of the best VPNs.")
async def vpns(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    embed = discord.Embed(
        title="VPNs",
        description="- [ProtonVPN](https://protonvpn.com/) - Free version cant torrent.\n"
        "- [Mullvad](https://mullvad.net/en) - Paid only.\n"
        "- [Windscribe](https://windscribe.com/) - Free and P2P.",
        color=discord.Color.dark_gray(),
    )

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="all-purpose", description="All purpose search tools.")
async def all_purpose(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = discord.Embed(
        title="All Purpose Search Tools",
        description="- [RuTracker](https://rutracker.org/) - My favorite.\n"
        "- [1337x](https://www1.13377x.tw/) - A good old one.",
    )

    await interaction.followup.send(embed=embed)


# Getting started command (U can change or delete this one if u want)
@bot.tree.command(
    name="getting-started",
    description="A guide to help new members navigate The Pirate Way server.",
)
async def getting_started(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    # Server description
    embed = discord.Embed(
        title="Getting Started",
        description="**Welcome to The Pirate Way!**\n\n"
        "The Pirate Way is the ultimate hub for piracy on Discord, where you can easily search or ask for "
        "games, movies, books, and so much more. Dive in and explore a wealth of resources curated just for you.",
        color=discord.Color.dark_gray(),
    )

    # Useful commands field
    embed.add_field(
        name="Useful Commands",
        value=(
            "**/search** - Offline search for cracked games.\n"
            "**/search-movies** - Online search for torrent movies.\n\n"
            "For more website-based resources, try commands like **/games**, **/emulators**, **/softwares**, "
            "**/books**, **/media**, **/vpns**, and **/all_purpose** to access curated lists of piracy content."
        ),
        inline=False,
    )

    await interaction.followup.send(embed=embed)


bot.run(TOKEN)
