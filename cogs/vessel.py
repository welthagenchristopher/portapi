import os
import time
import logging
import requests
import discord
from datetime import timedelta, date
from discord.ext import commands
from dotenv import load_dotenv
from ._formatter import Format


class VesselHandler(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.format = Format()
        load_dotenv()
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)
        self.header = {
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": os.getenv("PORTKEY"),
        }
        self.message_cache = {}

    async def embed_handler(
        self, interaction: discord.Interaction, content: list, page: int
    ):
        
        embed = discord.Embed(title=f"{content[0]['name']} movements")
        embed.set_author(name="Port Bot")

        for key, value in content[page].items():
            embed.add_field(name=key, value=value, inline=False)

        message = await interaction.followup.send(embed=embed, wait=True)
        self.message_cache[message.id] = {"content": content, "current_page": page}

        await message.add_reaction("\u2b05\ufe0f")  # Left arrow emoji
        await message.add_reaction("\u27a1\ufe0f")  # Right arrow emoji

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
       
        if user == self.bot.user:
            return

        message_id = reaction.message.id
        if message_id not in self.message_cache:
            return

        data = self.message_cache[message_id]
        content = data["content"]
        current_page = data["current_page"]

        if reaction.emoji == "\u2b05\ufe0f" and current_page > 0:
            current_page -= 1
        elif reaction.emoji == "\u27a1\ufe0f" and current_page < len(content) - 1:
            current_page += 1

        new_embed = discord.Embed(title=f"{content[0]['name']} movements")
        for key, value in content[current_page].items():
            new_embed.add_field(name=key, value=value, inline=False)

        await reaction.message.edit(embed=new_embed)
        self.message_cache[message_id]["current_page"] = current_page
        await reaction.remove(user)

    def vessel_request(self, vessel_name: str):
       
        date_past = date.today() - timedelta(days=30)
        date_future = date.today() + timedelta(days=30)
        vessel_list = []
        formatted_vessels = []

        url = (
            "https://api.portconnect.io/v1/scheduled-vessels"
            f"?vesselType=COMMERCIAL"
            f"&arrivalDateFrom={date_past}"
            f"&arrivalDateTo={date_future}"
        )

        try:
            response = requests.get(url, headers=self.header)
            response.raise_for_status()
            results = response.json()

            if not results:
                self.logger.info("Vessel list is empty.")
                return None

            for vessel in results:
                if vessel.get("vesselName") == vessel_name:
                    vessel_list.append(vessel)

            if not vessel_list:
                self.logger.info(f"Vessel '{vessel_name}' not found.")
                return None

            for vessel in vessel_list:
                self.logger.debug(vessel)
                if vessel["vesselStatus"] == "INPORT":
                    formatted_vessels.append(self.format.setvessel(vessel))
                elif vessel["vesselStatus"] == "DEPARTED":
                    formatted_vessels.append(self.format.outvessel(vessel))
                elif vessel["vesselStatus"] == "EXPECTED":
                    formatted_vessels.append(self.format.invessel(vessel))

            return formatted_vessels

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None

    @discord.app_commands.command()
    async def vessel(self, interaction: discord.Interaction, *, args: str):
        
        await interaction.response.defer()
        vessel_name = args.strip().upper()
        if not vessel_name:
            await interaction.followup.send("Please provide a valid vessel name.")
            return

        self.logger.info(f"Vessel '{vessel_name}' requested")
        content = self.vessel_request(vessel_name)

        if not content:
            await interaction.followup.send(
                "The vessel was not found in the Port Connect database. "
                "Please check for typos."
            )
            return

        await self.embed_handler(interaction, content, page=0)


async def setup(bot: commands.Bot):
    
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
    )
    await bot.add_cog(VesselHandler(bot))
