import os
import openai
import discord
import requests
from random import randrange
from src.aclient import client
from discord import app_commands
from src import log, art, personas, responses
from datetime import datetime, timedelta
from .views import PineoupasView

logger = log.setup_logger(__name__)


def run_discord_bot():
    @client.event
    async def on_ready():
        await client.send_start_prompt()
        await client.tree.sync()
        client.loop.create_task(client.process_messages())
        logger.info(f'{client.user} is now running!')

    @client.tree.command(name="chat", description="Have a chat with ChatGPT")
    async def chat(interaction: discord.Interaction, *, message: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **WARN: You already on replyAll mode. If you want to use the Slash Command, switch to normal mode by using `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({channel})")
        await client.enqueue_message(interaction, message)

    @client.tree.command(name="pineoupas", description="Tu pine ou tu pine pas ?")
    async def pineoupas(interaction: discord.Interaction):
        if interaction.user == client.user:
            return

        username = str(interaction.user)
        channel = str(interaction.channel)

        await interaction.response.defer()
        image_url = await client.get_woman()
        if image_url:
            embed = discord.Embed(title="Tu pine ou tu pine pas ?", color=0xee2bde)
            embed.set_image(url=image_url)
            requester = interaction.user.name
            requester_avatar = interaction.user.display_avatar
            current_time = datetime.now().strftime("%m-%d-%Y %H:%M")
            embed.set_footer(icon_url=requester_avatar ,text=f"Requested by {requester} • {current_time}")

            user_clicks = {}
            view = PineoupasView(timeout=12, user_clicks=user_clicks, client=client)

            message = await interaction.followup.send(embed=embed, view=view)
            view.message = message
            logger.info(f"\x1b[31m{username}\x1b[0m : /pineoupas in ({channel})")
        else:
            current_time = datetime.now()
            next_hour = (current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
            time_remaining = next_hour - current_time
            await interaction.followup.send(f"API requests limit, please wait `{time_remaining.seconds // 60}min {time_remaining.seconds % 60}secondes`")
            logger.info(f"\x1b[31m{username}\x1b[0m : /pineoupas exceeded - {time_remaining.seconds // 60}m{time_remaining.seconds % 60}s remaining")

    @client.tree.command(name="leaderboard", description="Display the users's reputation leaderboard")
    async def leaderboard(interaction: discord.Interaction, user: discord.User = None):
        if interaction.user == client.user:
            return

        username = str(interaction.user)
        channel = str(interaction.channel)

        await interaction.response.defer()
        if user is None:
            result = await client.get_leaderboard()
            if result:
                leaderboard_text = ""
                for idx, row in enumerate(result, start=1):
                    user_id, oui_count, non_count, rep = row
                    rank = await client.get_rank(rep)
                    user = await client.fetch_user(user_id)
                    if idx == 1:
                        medal = "🥇"
                    elif idx == 2:
                        medal = "🥈"
                    elif idx == 3:
                        medal = "🥉"
                    else:
                        medal = ""
                    leaderboard_text += f"{medal} **{user.name}** • • • Réputation: {rep} | {rank}\n"

                embed = discord.Embed(title="Leaderboard of `Tu pine ou tu pine pas ?`", color=0xee2bde, description=leaderboard_text)
                current_time = datetime.now().strftime("%m-%d-%Y %H:%M")
                requester = interaction.user.name
                requester_avatar = interaction.user.display_avatar
                embed.set_footer(icon_url=requester_avatar ,text=f"Requested by {requester} • {current_time}")
                await interaction.followup.send(embed=embed)
                logger.info(f"\x1b[31m{username}\x1b[0m : /leaderboard in ({channel})")
            else:
                await interaction.followup.send(f"oups, problème result !")
        else:
            user_id = user.id
            oui_count, non_count, rep = await client.get_user_count(user_id)
            rank = await client.get_rank(rep)
            

            embed = discord.Embed(title=f"**{user.name}'s statistics**", color=0xee2bde)
            embed.add_field(name="Reputation", value=f"{rep}", inline=False)
            embed.add_field(name="Total vote count", value=oui_count+non_count, inline=False)
            embed.add_field(name="Vote oui", value=oui_count, inline=True)
            embed.add_field(name="Vote non", value=non_count, inline=True)
            embed.add_field(name="Rank", value=rank, inline=False)

            embed.set_thumbnail(url=user.display_avatar)
            current_time = datetime.now().strftime("%m-%d-%Y %H:%M")
            requester = interaction.user.name
            requester_avatar = interaction.user.display_avatar
            embed.set_footer(icon_url=requester_avatar ,text=f"Requested by {requester} • {current_time}")

            await interaction.followup.send(embed=embed)
            logger.info(f"\x1b[31m{username}\x1b[0m : /leaderboard in ({channel})")

            

    @client.tree.command(name="private", description="Toggle private access")
    async def private(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if not client.isPrivate:
            client.isPrivate = not client.isPrivate
            logger.warning("\x1b[31mSwitch to private mode\x1b[0m")
            await interaction.followup.send(
                "> **INFO: Next, the response will be sent via private reply. If you want to switch back to public mode, use `/public`**")
        else:
            logger.info("You already on private mode!")
            await interaction.followup.send(
                "> **WARN: You already on private mode. If you want to switch to public mode, use `/public`**")

    @client.tree.command(name="public", description="Toggle public access")
    async def public(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.isPrivate:
            client.isPrivate = not client.isPrivate
            await interaction.followup.send(
                "> **INFO: Next, the response will be sent to the channel directly. If you want to switch back to private mode, use `/private`**")
            logger.warning("\x1b[31mSwitch to public mode\x1b[0m")
        else:
            await interaction.followup.send(
                "> **WARN: You already on public mode. If you want to switch to private mode, use `/private`**")
            logger.info("You already on public mode!")


    @client.tree.command(name="replyall", description="Toggle replyAll access")
    async def replyall(interaction: discord.Interaction):
        client.replying_all_discord_channel_id = str(interaction.channel_id)
        await interaction.response.defer(ephemeral=False)
        if client.is_replying_all == "True":
            client.is_replying_all = "False"
            await interaction.followup.send(
                "> **INFO: Next, the bot will response to the Slash Command. If you want to switch back to replyAll mode, use `/replyAll` again**")
            logger.warning("\x1b[31mSwitch to normal mode\x1b[0m")
        elif client.is_replying_all == "False":
            client.is_replying_all = "True"
            await interaction.followup.send(
                "> **INFO: Next, the bot will disable Slash Command and responding to all message in this channel only. If you want to switch back to normal mode, use `/replyAll` again**")
            logger.warning("\x1b[31mSwitch to replyAll mode\x1b[0m")


    @client.tree.command(name="chat-model", description="Switch different chat model")
    @app_commands.choices(choices=[
        app_commands.Choice(name="Official GPT-3.5", value="OFFICIAL"),
        app_commands.Choice(name="Ofiicial GPT-4.0", value="OFFICIAL-GPT4"),
        app_commands.Choice(name="Website ChatGPT-3.5", value="UNOFFICIAL"),
        app_commands.Choice(name="Website ChatGPT-4.0", value="UNOFFICIAL-GPT4"),
        app_commands.Choice(name="Bard", value="Bard"),
        app_commands.Choice(name="Bing", value="Bing"),
    ])

    async def chat_model(interaction: discord.Interaction, choices: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=False)
        original_chat_model = client.chat_model
        original_openAI_gpt_engine = client.openAI_gpt_engine

        try:
            if choices.value == "OFFICIAL":
                client.openAI_gpt_engine = "gpt-3.5-turbo"
                client.chat_model = "OFFICIAL"
            elif choices.value == "OFFICIAL-GPT4":
                client.openAI_gpt_engine = "gpt-4"
                client.chat_model = "OFFICIAL"
            elif choices.value == "UNOFFICIAL":
                client.openAI_gpt_engine = "gpt-3.5-turbo"
                client.chat_model = "UNOFFICIAL"
            elif choices.value == "UNOFFICIAL-GPT4":
                client.openAI_gpt_engine = "gpt-4"
                client.chat_model = "UNOFFICIAL"
            elif choices.value == "Bard":
                client.chat_model = "Bard"
            elif choices.value == "Bing":
                client.chat_model = "Bing"
            else:
                raise ValueError("Invalid choice")

            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(f"> **INFO: You are now in {client.chat_model} model.**\n")
            logger.warning(f"\x1b[31mSwitch to {client.chat_model} model\x1b[0m")

        except Exception as e:
            client.chat_model = original_chat_model
            client.openAI_gpt_engine = original_openAI_gpt_engine
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(f"> **ERROR: Error while switching to the {choices.value} model, check that you've filled in the related fields in `.env`.**\n")
            logger.exception(f"Error while switching to the {choices.value} model: {e}")


    @client.tree.command(name="reset", description="Complete reset conversation history")
    async def reset(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.chat_model == "OFFICIAL":
            client.chatbot = client.get_chatbot_model()
        elif client.chat_model == "UNOFFICIAL":
            client.chatbot.reset_chat()
            await client.send_start_prompt()
        elif client.chat_model == "Bard":
            client.chatbot = client.get_chatbot_model()
            await client.send_start_prompt()
        elif client.chat_model == "Bing":
            await client.chatbot.reset()
        await interaction.followup.send("> **INFO: I have forgotten everything.**")
        personas.current_persona = "standard"
        logger.warning(
            f"\x1b[31m{client.chat_model} bot has been successfully reset\x1b[0m")

    @client.tree.command(name="help", description="List bot commands")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        embed=discord.Embed(title="List of all commands", color=0xee2bde)
        embed.set_thumbnail(url="https://www.gendarmerie.interieur.gouv.fr/storage/var/gendarmerie_pjgn/storage/images/_aliases/gie_large/9/2/4/0/40429-1-fre-FR/DR.png")
        embed.add_field(name="`/chat` ", value="Have a chat with ChatGPT", inline=False)
        embed.add_field(name="`/pineoupas` ", value="Choose wisely...", inline=False)
        embed.add_field(name="`/draw` ", value="Generate an image with the Dalle2 model", inline=False)
        embed.add_field(name="`/switchpersona` ", value="Switch to a different ChatGPT", inline=False)
        embed.add_field(name="`/private` ", value="The bot's reply will only be seen by the person who used the command", inline=False)
        embed.add_field(name="`/public` ", value="The bot will directly reply on the channel", inline=False)
        embed.add_field(name="`/replyall` ", value="ChatGPT switch between replyAll mode and default mode (bot will reply to all messages in the channel without using slash commands)", inline=False)
        embed.add_field(name="`/reset` ", value="Clear ChatGPT conversation history", inline=False)
        embed.add_field(name="`/chat-model` ", value="Switch different chat model", inline=False)

        requester = interaction.user.name
        requester_avatar = interaction.user.display_avatar
        current_time = datetime.now().strftime("%m-%d-%Y %H:%M")
        embed.set_footer(icon_url=requester_avatar ,text=f"Requested by {requester} • {current_time}")

        await interaction.followup.send(embed=embed)

        logger.info(
            "\x1b[31mSomeone needs help!\x1b[0m")
               

    @client.tree.command(name="draw", description="Generate an image with the Dalle2 model")
    async def draw(interaction: discord.Interaction, *, prompt: str):
        if interaction.user == client.user:
            return

        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /draw [{prompt}] in ({channel})")

        await interaction.response.defer(thinking=True, ephemeral=client.isPrivate)
        try:
            path = await art.draw(prompt)

            file = discord.File(path, filename="image.png")
            title = f'> **prompt:** {prompt} \n\n'
            embed = discord.Embed(title=title)
            embed.set_image(url="attachment://image.png")

            requester = interaction.user.name
            requester_avatar = interaction.user.display_avatar
            current_time = datetime.now().strftime("%m-%d-%Y %H:%M")
            embed.set_footer(icon_url=requester_avatar ,text=f"Requested by {requester} • {current_time}")

            await interaction.followup.send(file=file, embed=embed)

        except openai.InvalidRequestError as e:
            await interaction.followup.send(
                f"> **ERROR: Inappropriate request 😿** \nDetails: {str(e)}")
            logger.info(
            f"\x1b[31m{username}\x1b[0m made an inappropriate request.!")

        except Exception as e:
            await interaction.followup.send(
                f"> **ERROR: Something went wrong 😿** \Details: {str(e)}")
            logger.exception(f"Error while generating image: {e}")


    @client.tree.command(name="switchpersona", description="Switch between optional chatGPT jailbreaks")
    @app_commands.choices(persona=[
        app_commands.Choice(name="Random", value="random"),
        app_commands.Choice(name="Standard", value="standard"),
        app_commands.Choice(name="Do Anything Now 11.0", value="dan"),
        app_commands.Choice(name="Superior Do Anything", value="sda"),
        app_commands.Choice(name="Evil Confidant", value="confidant"),
        app_commands.Choice(name="BasedGPT v2", value="based"),
        app_commands.Choice(name="Developer Mode v2", value="dev"),
        app_commands.Choice(name="DUDE V3", value="dude_v3"),
        app_commands.Choice(name="AIM", value="aim"),
        app_commands.Choice(name="UCAR", value="ucar"),
        app_commands.Choice(name="Jailbreak", value="jailbreak")
    ])
    async def switchpersona(interaction: discord.Interaction, persona: app_commands.Choice[str]):
        if interaction.user == client.user:
            return

        await interaction.response.defer(thinking=True)
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : '/switchpersona [{persona.value}]' ({channel})")

        persona = persona.value

        if persona == personas.current_persona:
            await interaction.followup.send(f"> **WARN: Already set to `{persona}` persona**")

        elif persona == "standard":
            if client.chat_model == "OFFICIAL":
                client.chatbot.reset()
            elif client.chat_model == "UNOFFICIAL":
                client.chatbot.reset_chat()
            elif client.chat_model == "Bard":
                client.chatbot = client.get_chatbot_model()
            elif client.chat_model == "Bing":
                client.chatbot = client.get_chatbot_model()

            personas.current_persona = "standard"
            await interaction.followup.send(
                f"> **INFO: Switched to `{persona}` persona**")

        elif persona == "random":
            choices = list(personas.PERSONAS.keys())
            choice = randrange(0, 6)
            chosen_persona = choices[choice]
            personas.current_persona = chosen_persona
            await responses.switch_persona(chosen_persona, client)
            await interaction.followup.send(
                f"> **INFO: Switched to `{chosen_persona}` persona**")


        elif persona in personas.PERSONAS:
            try:
                await responses.switch_persona(persona, client)
                personas.current_persona = persona
                await interaction.followup.send(
                f"> **INFO: Switched to `{persona}` persona**")
            except Exception as e:
                await interaction.followup.send(
                    "> **ERROR: Something went wrong, please try again later! 😿**")
                logger.exception(f"Error while switching persona: {e}")

        else:
            await interaction.followup.send(
                f"> **ERROR: No available persona: `{persona}` 😿**")
            logger.info(
                f'{username} requested an unavailable persona: `{persona}`')

    @client.event
    async def on_message(message):
        if client.is_replying_all == "True":
            if message.author == client.user:
                return
            if client.replying_all_discord_channel_id:
                if message.channel.id == int(client.replying_all_discord_channel_id):
                    username = str(message.author)
                    user_message = str(message.content)
                    channel = str(message.channel)
                    logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
                    await client.enqueue_message(message, user_message)
            else:
                logger.exception("replying_all_discord_channel_id not found, please use the commnad `/replyall` again.")

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    client.run(TOKEN)
