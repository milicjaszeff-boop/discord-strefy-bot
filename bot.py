import discord
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

    os.execv(sys.executable, ['python'] + sys.argv)


# START
bot.run(TOKEN)
