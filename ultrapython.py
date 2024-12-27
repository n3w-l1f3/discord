import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import json
import asyncio

# Configurations
TOKEN = 'TU_TOKEN'
PREFIX = '!'

# Bot Initialization
intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Autoroles
@bot.event
async def on_member_join(member):
    guild = member.guild
    role = discord.utils.get(guild.roles, name="Member")  # Replace with the desired role name
    if role:
        await member.add_roles(role)
        await member.send(f"Welcome to {guild.name}, {member.mention}! You have been assigned the {role.name} role.")

# Embed Messages
@bot.command()
async def embed(ctx, title, *, content):
    embed = discord.Embed(title=title, description=content, color=0x00ff00)
    embed.set_footer(text="Embed Message System")
    await ctx.send(embed=embed)

# Advanced Tickets
@bot.command()
async def ticket(ctx):
    ticket_category = discord.utils.get(ctx.guild.categories, name="Tickets")
    if not ticket_category:
        ticket_category = await ctx.guild.create_category("Tickets")

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    ticket_channel = await ctx.guild.create_text_channel(f"ticket-{ctx.author.name}", category=ticket_category, overwrites=overwrites)

    embed = discord.Embed(title="Ticket Support", description=f"Welcome, {ctx.author.mention}! A staff member will assist you shortly.", color=0x3498db)
    await ticket_channel.send(embed=embed)

    close_button = Button(label="Close Ticket", style=discord.ButtonStyle.danger)

    async def close_callback(interaction):
        if interaction.user == ctx.author or interaction.user.guild_permissions.manage_channels:
            await ticket_channel.delete()

    close_button.callback = close_callback
    view = View()
    view.add_item(close_button)
    await ticket_channel.send(view=view)

# Feedback Modal
class FeedbackModal(Modal):
    def __init__(self):
        super().__init__(title="Submit Feedback")
        self.add_item(TextInput(label="Feedback", placeholder="Type your feedback here...", style=discord.TextStyle.paragraph))

    async def on_submit(self, interaction):
        feedback_channel = discord.utils.get(interaction.guild.text_channels, name="feedback")
        if not feedback_channel:
            feedback_channel = await interaction.guild.create_text_channel("feedback")

        embed = discord.Embed(title="New Feedback", description=self.children[0].value, color=0xffc300)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await feedback_channel.send(embed=embed)
        await interaction.response.send_message("Thank you for your feedback!", ephemeral=True)

@bot.command()
async def feedback(ctx):
    modal = FeedbackModal()
    await ctx.send_modal(modal)

# Poll System
@bot.command()
async def poll(ctx, question, *options):
    if len(options) < 2 or len(options) > 10:
        await ctx.send("You must provide between 2 and 10 options.")
        return

    embed = discord.Embed(title="Poll", description=question, color=0x1abc9c)
    fields = [f"{chr(65 + i)}: {option}" for i, option in enumerate(options)]
    embed.add_field(name="Options", value="\n".join(fields), inline=False)
    poll_message = await ctx.send(embed=embed)

    for i in range(len(options)):
        await poll_message.add_reaction(chr(127462 + i))

# Staff Review System
@bot.command()
async def review(ctx, member: discord.Member, *, review_text):
    review_channel = discord.utils.get(ctx.guild.text_channels, name="staff-reviews")
    if not review_channel:
        review_channel = await ctx.guild.create_text_channel("staff-reviews")

    embed = discord.Embed(title="Staff Review", color=0xff5733)
    embed.add_field(name="Reviewer", value=ctx.author.mention, inline=False)
    embed.add_field(name="Staff Member", value=member.mention, inline=False)
    embed.add_field(name="Review", value=review_text, inline=False)
    await review_channel.send(embed=embed)
    await ctx.send("Thank you for your feedback!")

# User Information
@bot.command()
async def userinfo(ctx, member: discord.Member):
    embed = discord.Embed(title=f"User Information - {member.name}", color=0x7289da)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=False)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

# Bot Events
@bot.event
async def on_ready():
    print(f"{bot.user.name} is online and ready to assist!")
    for guild in bot.guilds:
        print(f"Connected to: {guild.name}")

bot.run(TOKEN)
