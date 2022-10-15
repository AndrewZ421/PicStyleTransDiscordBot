from ctypes import sizeof
import discord
from discord.ext import commands
from PIL import Image
import asyncio
from io import BytesIO
import uuid
import requests
import shutil
import os
import time


TOKEN = 'ODk1MTg0NzYyNzI0MDM2NjQ4.G8Dqa9.G2AGlHkYhEgs1Y6edQs7uHclIOpLVxpauDDkPs'
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!',intents=intents)

@client.event
async def on_ready():
    print('Connected to bot: {}'.format(client.user.name))
    print('Bot ID: {}'.format(client.user.id))

@client.command()
@commands.has_role('Admin')
async def info(ctx):
    title = "Click here to start"
    embed = discord.Embed(title=title, url="https://discord.com/channels/1030676263884562432/1030905514227412992",
                            description="Simpily type !start and follow the steps to build your own emoji!",
                            color=0x82111f)
    embed.set_thumbnail(url="https://hackwashu.com/img/about.562d9937.png")
    embed.add_field(name="!start", value="start to build your emoji", inline=False)
    embed.set_footer(text="Hack WashU", icon_url="https://hackwashu.com/img/about.562d9937.png")

    # embed.add_field(value="欢迎来到HR Space!")

    await ctx.send(embed=embed)

@client.command()
async def start(ctx, name):
    if ctx.channel.id == 1030905514227412992:
        guild = ctx.guild
        steps = 2
        cur_step = 1
        style_list = ['Starry Night','Skrik']
        start_message = await ctx.send(f"Step {cur_step}/{steps}: Upload your image here in 1 minute.")

        def check_image(message):
            return message.author == ctx.author and bool(message.attachments)
        def check_style(message):
            return message.author == ctx.author and message.content in style_list
        

        while True:
            try:
                if cur_step==1:
                    resp = await client.wait_for("message", timeout=60, check=check_image)
                    image = resp.attachments[0]
                    cur_step += 1
                    await ctx.send("Successfully saved your image.")
                elif cur_step==2:
                    style_str = '/'.join(style_list)
                    await ctx.send(f"Step {cur_step}/{steps}: Type your sytle here: {style_str}")
                    resp = await client.wait_for("message", timeout=60, check=check_style)
                    cur_step += 1
                elif cur_step==3:
                    await ctx.send(f"Generating your emoji...")
                    r = requests.get(image, stream=True)
                    start = time.time()
                    imageName = str(uuid.uuid4()) + '.jpg'
                    # imageName = 'input\\' + str(uuid.uuid4()) + '.jpg'
                    # print(imageName)
                    with open(imageName, 'wb') as out_file:
                        print('Saving image: ' + imageName)
                        shutil.copyfileobj(r.raw, out_file)
                    # operate  
                    # os.system("python evaluate.py --checkpoint check_point/wave.ckpt  --in-path " + imageName + " --out-path " + imageName)
                    os.system("python evaluate.py --checkpoint check_point/udnie.ckpt  --in-path " + imageName + " --out-path " + imageName)
                    print('Processing time:', time.time()-start)
                    file = discord.File(imageName)
                    await ctx.send(file=file)
                    emoji = Image.open(imageName)
                    # emoji.show()
                    newsize = (128, 128)
                    re_emoji = emoji.resize(newsize)
                    re_emoji.format = emoji.format
                    imgByteArr = BytesIO()
                    re_emoji.save(imgByteArr, format=re_emoji.format)
                    imgByteArr = imgByteArr.getvalue()
                    emoji = await guild.create_custom_emoji(name=name, image=imgByteArr)     
                    cur_step += 1
                else:
                    os.remove(imageName)
                    await ctx.send("Emoji successfully created!") 
                    break
            except asyncio.TimeoutError:
                await start_message.delete()
                await ctx.send("Session expired.")
                break

client.run(TOKEN)
