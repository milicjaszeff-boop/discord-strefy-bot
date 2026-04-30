import discord
from discord.ext import commands
from discord import Embed
from dotenv import load_dotenv
import os
import aiosqlite
import sys

# Wczytanie .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot
bot = commands.Bot(command_prefix='!', intents=intents)

DATABASE = "database.db"

# Role z dostępem
allowed_roles = [
    "【📄】Zarząd",
    "【👑】Zastępca OG",
    "【👑】OG"
]


# Tworzenie bazy danych
async def setup_database():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS strefy (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                strefy INTEGER DEFAULT 0
            )
        """)
        await db.commit()


# Funkcja odświeżania topki
async def refresh_topka():

    for guild in bot.guilds:

        channel = discord.utils.get(
            guild.text_channels,
            name="⭐topka-stref"
        )

        if channel is None:
            continue

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                "SELECT username, strefy FROM strefy ORDER BY strefy DESC LIMIT 10"
            )

            rows = await cursor.fetchall()

        ranking = ""

        for index, row in enumerate(rows, start=1):
            ranking += f"{index}. {row[0]} — {row[1]} stref\n"

        if ranking == "":
            ranking = "Brak danych."

        embed = Embed(
            title="🏆 TOP 10 STREF",
            description=ranking,
            color=discord.Color.gold()
        )

        messages = [msg async for msg in channel.history(limit=20)]

        bot_message = None

        for msg in messages:
            if msg.author.id == bot.user.id and msg.embeds:
                bot_message = msg
                break

        if bot_message:
            await bot_message.edit(embed=embed)
        else:
            await channel.send(embed=embed)


# Bot gotowy
@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

    await setup_database()
    await refresh_topka()


# RESET TOPKI
@bot.command()
async def resetstref(ctx):

    user_roles = [role.name for role in ctx.author.roles]

    if not any(role in allowed_roles for role in user_roles):
        await ctx.send("Nie masz permisji do użycia tej komendy.")
        return

    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM strefy")
        await db.commit()

    await refresh_topka()
    await ctx.send("Topka stref została zresetowana.")


# KOMENDA !strefa
@bot.command()
async def strefa(ctx, nazwa_strefy=None):

    if not nazwa_strefy:
        await ctx.send("Podaj nazwę strefy.")
        return

    mentions = ctx.message.mentions

    if len(mentions) == 0:
        await ctx.send("Musisz oznaczyć graczy.")
        return

    async with aiosqlite.connect(DATABASE) as db:

        for user in mentions:

            cursor = await db.execute(
                "SELECT * FROM strefy WHERE user_id = ?",
                (str(user.id),)
            )

            row = await cursor.fetchone()

            if row:
                await db.execute(
                    "UPDATE strefy SET strefy = strefy + 1 WHERE user_id = ?",
                    (str(user.id),)
                )
            else:
                await db.execute(
                    "INSERT INTO strefy (user_id, username, strefy) VALUES (?, ?, ?)",
                    (str(user.id), user.name, 1)
                )

        await db.commit()

    await ctx.send(f"Zapisano strefę: {nazwa_strefy}")
    await refresh_topka()


# RESET JEDNEGO GRACZA
@bot.command()
async def resetujgracz(ctx, member: discord.Member = None):

    user_roles = [role.name for role in ctx.author.roles]

    if not any(role in allowed_roles for role in user_roles):
        await ctx.send("Nie masz permisji do użycia tej komendy.")
        return

    if member is None:
        await ctx.send("Oznacz gracza.")
        return

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            "DELETE FROM strefy WHERE user_id = ?",
            (str(member.id),)
        )

        await db.commit()

    await refresh_topka()
    await ctx.send(f"Zresetowano strefy gracza {member.mention}")


# ODSWIEZ TOPKE
@bot.command()
async def odswieztopke(ctx):

    await refresh_topka()
    await ctx.send("Topka została odświeżona.")


# RESET BOTA
@bot.command()
async def reset(ctx):

    user_roles = [role.name for role in ctx.author.roles]

    if not any(role in allowed_roles for role in user_roles):
        await ctx.send("Nie masz permisji do użycia tej komendy.")
        return

    await ctx.send("Restartuję bota...")

    os.execv(sys.executable, [sys.executable] + sys.argv)


# START
bot.run(TOKEN)
