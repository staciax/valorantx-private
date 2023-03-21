import asyncio
from valorantx.ext import chat

client = chat.ClientMITM(prefix='!')

# design 01

replaces = {
    ':heart:': '❤️',
    ':smile:': '😄',
    ':joy:': '😂',
}

for name, emoji in replaces.items():
    client.add_replacement(name, emoji)

# design 02

client.set_replacements(replaces)

# design 03 (from a json file)

client.load_replacements('replacements.json')

# ws event

@client.event
async def on_ready():
    print('Ready!')

@client.event
async def on_message(message: chat.Message):
    # Replacing the :heart: emoji with ❤️
    if 'hi' in message.content:
        await message.edit(content=message.content.replace(':heart:', '❤️'))

# chat command

@client.command(hidden=True)
async def ping(ctx: chat.Context):
    await ctx.send('Pong!')

@client.command('spam', aliases=['s'])
async def spam(ctx: chat.Context, times: int, *, content: str):
    if times > 10:
        return await ctx.send(content)

    for _ in range(times):
        await ctx.send(content)
        await asyncio.sleep(0.5)

client.run()
