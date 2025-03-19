import discord
import os
import json
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
    links_games4u = []
    links_magipack = []

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
                    elif link_url.startswith("https://games4u.org"):
                        links_games4u.append(f"[{link_text}]({link_url})")
                    elif link_url.startswith("https://www.magipack.games"):
                        links_magipack.append(f"[{link_text}]({link_url})")

    return links_elamigos, links_steamrip, links_dodi, links_games4u, links_magipack


# ---- SLASH COMMANDS ----
@bot.tree.command(
    name="search", description="Offline database search for cracked games."
)
async def search(interaction: discord.Interaction, input: str):
    await interaction.response.defer(thinking=True)

    links_elamigos, links_steamrip, links_dodi, links_games4u, links_magipack = (
        load_links()
    )
    input = input.lower()
    results_elamigos = [link for link in links_elamigos if input in link.lower()]
    results_steamrip = [link for link in links_steamrip if input in link.lower()]
    results_dodi = [link for link in links_dodi if input in link.lower()]
    results_games4u = [link for link in links_games4u if input in link.lower()]
    results_magipack = [link for link in links_magipack if input in link.lower()]

    if (
        not results_elamigos
        and not results_steamrip
        and not results_dodi
        and not results_games4u
        and not results_magipack
    ):
        await interaction.followup.send(
            f"Oops! I couldnt find any results for '{input}' :("
        )
        return

    # EMOJIS - Change to your own ids or just use regular emojis on field names
    elamigos_emoji = config["ELAMIGOS_EMOJI"]
    steamrip_emoji = config["STEAMRIP_EMOJI"]
    dodi_emoji = config["DODI_EMOJI"]
    games4u_emoji = config["GAMES4U_EMOJI"]
    magipack_emoji = config["MAGIPACK_EMOJI"]

    embed = discord.Embed(
        title=f"🔎 Results for '{input}'", color=discord.Color.dark_gray()
    )
    if results_elamigos:
        embed.add_field(
            name=f"{elamigos_emoji} ELAMIGOS",
            value="\n".join(results_elamigos[:3]),
            inline=False,
        )
    if results_steamrip:
        embed.add_field(
            name=f"{steamrip_emoji} STEAMRIP",
            value="\n".join(results_steamrip[:3]),
            inline=False,
        )
    if results_dodi:
        embed.add_field(
            name=f"{dodi_emoji} DODI REPACKS",
            value="\n".join(results_dodi[:3]),
            inline=False,
        )
    if results_games4u:
        embed.add_field(
            name=f"{games4u_emoji} GAMES4U",
            value="\n".join(results_games4u[:3]),
            inline=False,
        )
    if results_magipack:
        embed.add_field(
            name=f"{magipack_emoji} MAGIPACK",
            value="\n".join(results_magipack[:3]),
            inline=False,
        )

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


@bot.tree.command(name="all_purpose", description="All purpose search tools.")
async def all_purpose(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = discord.Embed(
        title="All Purpose Search Tools",
        description="- [RuTracker](https://rutracker.org/) - My favorite.\n"
        "- [1337x](https://www1.13377x.tw/) - A good old one.",
    )

    await interaction.followup.send(embed=embed)


bot.run(TOKEN)
