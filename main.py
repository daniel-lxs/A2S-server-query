#!/usr/bin/env python3

import re
import paramiko
import sys
import datetime
import yaml
from disnake.ext import tasks, commands
from disnake import Embed
from emoji import emojize
from query import query
from config import Config

config = Config("./config.yml")


async def generate_message(servers):
    try:
        results = await query(servers, timeout=config.timeout)
        online_servers = []
        offline_servers = []
        for result in results:
            endpoint = f"{result['ip']}:{result['port']}"
            content = ""
            is_online = "ex" not in result
            emoji = "🟢" if is_online else "🔴"

            if is_online:
                player_count = result["player_count"]
                campaign = result["campaign"]
                server_name = result["name"]
                max_players = result["max_players"]
                content += f"Players: {player_count}/{max_players}, Map: {campaign}"

                if len(result["players"]):
                    players = "\n".join(
                        f"  {p}" for p in result["players"] if p)
                    content += f"\n{players}"

                content += f"\n[🔗Connect](https://connectsteam.me/?{endpoint})"

                online_servers.append(
                    {
                        "name": f"{emoji} {server_name}  ```{endpoint}```",
                        "value": f"{content}",
                        "inline": False,
                    }
                )
            else:
                exception_text = result["ex"]
                content += f"{exception_text}"

                offline_servers.append(
                    {
                        "name": f"{emoji} Offline  ```{endpoint}```",
                        "value": f"{content}",
                        "inline": False,
                    }
                )

        embed_dict = {
            "title": "Server Status",
            "description": "",
            "color": 0xFEE75C,
            "timestamp": datetime.datetime.now().isoformat(),
            "fields": [],
        }

        # Add online servers to the fields
        embed_dict["fields"].extend(online_servers)

        # Add offline servers to the fields
        embed_dict["fields"].extend(offline_servers)

        print("/servers: ok")
    except Exception as ex:
        exception_text = str(ex)
        print(f"/servers: ex: {exception_text}")
        embed_dict = {
            "title": "Exception",
            "description": exception_text,
            "color": 0xFF0000,
            "timestamp": datetime.datetime.now().isoformat(),
            "author": {
                "name": "Server Status",
                "url": "https://disnake.dev/",
                "icon_url": "https://disnake.dev/assets/disnake-logo.png",
            },
        }

    print("/servers: end")
    return embed_dict


async def get_total_player_count(servers, errors=False):
    total_player_count = 0
    try:
        results = await query(servers, timeout=config.timeout)
        for result in results:
            if "player_count" in result:
                total_player_count += result["player_count"]
    except Exception:
        pass

    if errors:
        errors = [result.get("ex", None) for result in results]
        return total_player_count, errors
    else:
        return total_player_count


class Bot(commands.InteractionBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.warning = " " + emojize(":warning:")
        # Dictionary to store the last sent message for each channel
        self.last_sent_messages_servers = {}
        self.last_sent_messages_other = {}

        # Start the servers_task_loop
        self.servers_task_loop.start()

    # Define the task loop that updates the message content
    @tasks.loop(minutes=1)  # Adjust the seconds to match the interval you want
    async def servers_task_loop(self):
        await self.update_message_content()

    @servers_task_loop.before_loop
    async def before_servers_task_loop(self):
        await self.wait_until_ready()

    @tasks.loop(minutes=5)
    async def update_player_count_task(self):
        print(f"==================================================")
        print(f"update_player_count_task: tick")
        try:
            count_players = len(config.player_count_channel_id) > 0
            if count_players:
                player_count, errors = await get_total_player_count(
                    config.servers["L4D2"], errors=True
                )
                print(
                    f"update_player_count_task: active players: {player_count}")
                for channel_id in config.player_count_channel_id.split(","):
                    print(
                        f"update_player_count_task: getting channel with id: {channel_id}"
                    )
                    channel = self.get_channel(int(channel_id))
                    print(f"update_player_count_task: got channel '{channel}'")
                    warning = ""
                    if None not in errors:
                        warning = self.warning
                    await channel.edit(name=f"Left 4 Dead: {player_count}{warning}")
                    print(f"update_player_count_task: edit channel completed")
        except Exception as ex:
            print(f"update_player_count_task: ex: {ex}")

    async def update_message_content(self):
        try:
            updated_msg_servers = await generate_message(config.servers["L4D2"])
            updated_msg_others = await generate_message(config.servers["Other"])

            for channel_id, sent_message in self.last_sent_messages_servers.items():
                if sent_message is not None:
                    print(f"{channel_id}: updating message")
                    await sent_message.edit(embed=Embed.from_dict(updated_msg_servers))

            for channel_id, sent_message in self.last_sent_messages_other.items():
                if sent_message is not None:
                    print(f"{channel_id}: updating message")
                    await sent_message.edit(embed=Embed.from_dict(updated_msg_others))

        except Exception as ex:
            print(f"update_message_content: ex: {ex}")


bot = Bot()


@bot.slash_command(description="Query the WhoCares L4D2 servers")
async def servers(context):
    print(f"==================================================")
    print(f"/servers: begin: user:{context.author.name}")
    await context.response.defer(with_message=False, ephemeral=False)
    msg = await generate_message(config.servers["L4D2"])
    await context.send(embed=Embed.from_dict(msg))  # Send the initial message

    bot.last_sent_messages_servers[
        context.channel.id
    ] = await context.original_response()


@bot.slash_command(description="Query the WhoCares L4D2 servers")
async def servers2(context):
    print(f"==================================================")
    print(f"/servers2: begin: user:{context.author.name}")
    await context.response.defer(with_message=False, ephemeral=False)
    msg = await generate_message(config.servers["Other"])
    await context.send(embed=Embed.from_dict(msg))  # Send the initial message

    bot.last_sent_messages_other[context.channel.id] = await context.original_response()


@bot.slash_command(description="Ban an IP address")
async def banip(ctx, ip: str, bantime: str):
    await ctx.response.defer()
    # Check if the user has the Moderator role
    moderator_role = ctx.guild.get_role(config.moderator_role_id)
    if moderator_role is None or moderator_role not in ctx.author.roles:
        await ctx.send("You don't have permission to use this command.")
        return

    ctx.response.defer()

    # Convert bantime to seconds
    if not re.match(r"^\d+[smh]*$", bantime):
        await ctx.send(
            "Invalid bantime format. Use something like '10s', '12m', '2h', '2h12m10s'."
        )
        return

    time_units = {"s": 1, "m": 60, "h": 3600}
    seconds = int(bantime[:-1]) * time_units.get(bantime[-1], 1)

    # SSH connection and command execution
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(config.server, username=config.username,
                    password=config.password)
        cmd_to_execute = (
            f"nft add element ip filter blacklist {{ {ip} timeout {seconds}s }}"
        )
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)

        ssh_stdout.read().decode("utf-8").strip()

        await ctx.send(content=f"IP address banned: {ip}")
    except Exception as ex:
        await ctx.send(content=f"An error occurred: {ex}")
    finally:
        ssh.close()


@bot.slash_command(description="Unban an IP address")
async def unbanip(ctx, ip: str):
    await ctx.response.defer()
    # Check if the user has the Moderator role
    moderator_role = ctx.guild.get_role(config.moderator_role_id)
    if moderator_role is None or moderator_role not in ctx.author.roles:
        await ctx.send("You don't have permission to use this command.")
        return

    # SSH connection and command execution
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(config.server, username=config.username,
                    password=config.password)
        cmd_to_execute = f"nft delete element ip filter blacklist {{ {ip} }}"
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)

        ssh_stdout.read().decode("utf-8").strip()

        # Edit the original response
        await ctx.send(content=f"IP address unbanned: {ip}")
    except Exception as ex:
        # Edit the original response in case of an error
        await ctx.send(content=f"An error occurred: {ex}")
    finally:
        ssh.close()


@bot.slash_command(description="Reload the configuration file")
async def reload_config(ctx):
    await ctx.response.defer()

    # Check if the user has the Moderator role
    moderator_role = ctx.guild.get_role(config.moderator_role_id)
    if moderator_role is None or moderator_role not in ctx.author.roles:
        await ctx.send("You don't have permission to use this command.")
        return

    # Attempt to reload the configuration
    try:
        config.reload()  # Implement the reload method in your Config class
        await ctx.send("Configuration reloaded successfully.")
    except Exception as ex:
        await ctx.send(f"An error occurred while reloading the configuration: {ex}")


@bot.event
async def on_ready():
    print("on_ready: begin")
    bot.update_player_count_task.start()
    print("on_ready: end")


bot.run(config.token)
