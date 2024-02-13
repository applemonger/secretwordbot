import lightbulb
import hikari
import os
from database import Database
from textwrap import dedent


COLOR = hikari.Color.of((59, 165, 93))
HINT_COLOR = hikari.Color.of((255, 198, 65))
GUILDS = [] if os.getenv("GUILD_ID") is None else [int(os.getenv("GUILD_ID"))]


bot = lightbulb.BotApp(
    token=os.getenv("TOKEN"),
    prefix=None,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT,
)


db = Database()


@bot.command
@lightbulb.command("help", "Learn more about Secret Word!", guilds=GUILDS)
@lightbulb.implements(lightbulb.SlashCommand)
async def help(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(title="Secret Word Help", color=COLOR)
    value = """
        Secret Word is a simple game: someone sets a secret word, and other people try 
        to guess it.
        1. Use `/start` to initialize the game with a secret word.
        2. Use `/hint` to set hints if you are the secret setter.
        3. Other people may guess by just typing into the channel. They can use the `/hints` command to get a list of all current hints.
        4. If their message contains the secret word, they can set a new secret word with `/secret`.
    """
    embed.add_field(name="Getting Started", value=dedent(value))
    await ctx.respond(embed)


@bot.command
@lightbulb.option("word", "Set the secret word", type=str)
@lightbulb.command("start", "Starts the game with the given word.", guilds=GUILDS)
@lightbulb.implements(lightbulb.SlashCommand)
async def start(ctx: lightbulb.Context) -> None:
    guild_id = int(ctx.guild_id)
    author_id = int(ctx.author.id)
    word = str(ctx.options.word)
    if db.guild_exists(guild_id):
        await ctx.respond(
            "The word is already set!", flags=hikari.MessageFlag.EPHEMERAL
        )
    else:
        db.start_guild(guild_id, author_id, word)
        # Create embed
        embed = hikari.Embed(title="New Secret Word!", color=COLOR)
        embed.add_field(name="A new secret word has been set.", value="Good luck!")
        embed.add_field(name="Set by:", value=f"<@{author_id}>")
        await ctx.respond(embed)


@bot.command
@lightbulb.option("word", "Secret word. Make it a good one!", type=str)
@lightbulb.command("secret", "Set the secret word.", guilds=GUILDS)
@lightbulb.implements(lightbulb.SlashCommand)
async def secret(ctx: lightbulb.Context) -> None:
    guild_id = int(ctx.guild_id)
    author_id = int(ctx.author.id)
    word = str(ctx.options.word)
    # Get current secret
    secret = db.get_secret(guild_id)
    if secret.guesser is not None and secret.guesser == author_id:
        db.set_word(guild_id, author_id, word)
        embed = hikari.Embed(title="New Secret Word!", color=COLOR)
        embed.add_field(name="A new secret word has been set.", value="Good luck!")
        embed.add_field(name="Set by:", value=f"<@{author_id}>")
        await ctx.respond(embed)
    else:
        await ctx.respond(
            "You are not the current Secret Word setter!",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@bot.command
@lightbulb.option("hint", "Hint to add", type=str)
@lightbulb.command("hint", "Add a hint for the secret word", guilds=GUILDS)
@lightbulb.implements(lightbulb.SlashCommand)
async def hint(ctx: lightbulb.Context) -> None:
    guild_id = int(ctx.guild_id)
    author_id = int(ctx.author.id)
    hint = str(ctx.options.hint)
    # Get current secret
    secret = db.get_secret(guild_id)
    if secret.author == author_id and secret.guesser is not None:
        hint_number = db.add_hint(guild_id, hint)
        embed = hikari.Embed(title="Hint Added!", color=HINT_COLOR)
        embed.add_field(name=f"Hint #{hint_number}", value=hint)
        await ctx.respond(embed)
    else:
        await ctx.respond(
            "You are not the current Secret Word setter!",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@bot.command
@lightbulb.command("hints", "Get all hints for the current secret word.", guilds=GUILDS)
@lightbulb.implements(lightbulb.SlashCommand)
async def hints(ctx: lightbulb.Context) -> None:
    guild_id = int(ctx.guild_id)
    # Get current secret
    secret = db.get_secret(guild_id)
    if secret.is_set():
        # Get current hints
        hints = db.get_hints(guild_id)
        embed = hikari.Embed(title="Hints", color=HINT_COLOR)
        hints_str = ""
        for i, hint in enumerate(hints):
            hints_str += f"#{i+1}: {hint}\n"
        if hints_str == "":
            hints_str = "No hints set yet. Use `/hint` to set a hint."
        embed.add_field(name="The current hints are...", value=hints_str)
        embed.add_field(name="The secret word is set by:", value=f"<@{secret.author}>")
        await ctx.respond(embed)
    else:
        embed = hikari.Embed(title="Hints", color=HINT_COLOR)
        embed.add_field(
            name="The secret word has not been set yet!",
            value="Set the secret word with `/secret`.",
        )
        await ctx.respond(embed)


@bot.listen()
async def guess(event: hikari.GuildMessageCreateEvent) -> None:
    # Do not respond to bots nor webhooks pinging us, only user accounts
    if not event.is_human:
        return
    # Get current secret
    guild_id = int(event.guild_id)
    secret = db.get_secret(guild_id)
    # Only check if a secret word is set
    if secret.is_set():
        # Get guesser
        guesser = int(event.message.author)
        # Secret author is the guesser
        author_is_not_guesser = secret.author != guesser
        # Word has not been guessed already
        word_has_not_been_guessed = secret.guesser is None
        # Guess contains the secret word
        secret_in_guess = secret.word.lower() in event.message.content.lower()
        # If the guesser is not the setter, and the message includes the word
        if author_is_not_guesser and word_has_not_been_guessed and secret_in_guess:
            embed = hikari.Embed(title="Secret Word Found!", color=COLOR)
            embed.add_field(
                name=f"The secret word was... {secret.word}!",
                value=f"<@{guesser}> may pick a new word with `/secret`.",
            )
            db.set_guesser(guild_id, guesser)
            db.clear_hints(guild_id)
            await event.message.respond(embed)


if __name__ == "__main__":
    bot.run()
