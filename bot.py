import discord
from discord.ext import commands
from datetime import datetime, timedelta

class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.modlog_channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user}')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Change to '👋-welcome' channel
        welcome_channel = discord.utils.get(member.guild.text_channels, name='👋-welcome')
        
        if welcome_channel:
            welcome_message = f"""
👋 Welcome to RIVALS, {member.mention}! ⚔️🔥

🎮 Get ready to compete and rise to the top in epic battles! 🏆💥

🚀 Here’s what to do next:
📜 Read the rules – Keep the competition fair and fun!
🎭 Get your roles – Personalize your experience!
🎮 Join the action – Prove your skills in the arena!

💬 Say hi in the chat & start your journey to victory! 🔥

🏆 Only the strongest will survive… Are you ready? 💥
"""
            await welcome_channel.send(welcome_message)

        # Send the same message in DMs
        try:
            dm_message = f"""
👋 Welcome to RIVALS, {member.name}! ⚔️🔥

🎮 Get ready to compete and rise to the top in epic battles! 🏆💥

🚀 Here’s what to do next:
📜 Read the rules – Keep the competition fair and fun!
🎭 Get your roles – Personalize your experience!
🎮 Join the action – Prove your skills in the arena!

💬 Say hi in the chat & start your journey to victory! 🔥

🏆 Only the strongest will survive… Are you ready? 💥
"""
            await member.send(dm_message)
        except discord.errors.Forbidden:
            print(f"Could not send DM to {member.name}. They have DMs disabled.")

    @commands.command()
    async def test_welcome(self, ctx, member: discord.Member):
        """Test the welcome message before the user joins."""
        # Change to '👋-welcome' channel
        welcome_channel = discord.utils.get(ctx.guild.text_channels, name='👋-welcome')
        if welcome_channel:
            welcome_message = f"""
👋 Welcome to RIVALS, {member.mention}! ⚔️🔥

🎮 Get ready to compete and rise to the top in epic battles! 🏆💥

🚀 Here’s what to do next:
📜 Read the rules – Keep the competition fair and fun!
🎭 Get your roles – Personalize your experience!
🎮 Join the action – Prove your skills in the arena!

💬 Say hi in the chat & start your journey to victory! 🔥

🏆 Only the strongest will survive… Are you ready? 💥
"""
            await welcome_channel.send(welcome_message)
            await ctx.send(f"Test welcome message sent to {welcome_channel.mention} for {member.mention}.")

            # Also send welcome message in DM
            try:
                await member.send(welcome_message)
                await ctx.send(f"Test welcome DM sent to {member.mention}")
            except discord.errors.Forbidden:
                await ctx.send(f"Could not send DM to {member.mention}, they have DMs disabled.")
        else:
            await ctx.send("Could not find a channel named '👋-welcome'.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'{member.name} has been banned.')
        if self.modlog_channel:
            await self.modlog_channel.send(f'{member.name} was banned. Reason: {reason}')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f'{user.name} has been unbanned.')
        if self.modlog_channel:
            await self.modlog_channel.send(f'{user.name} was unbanned.')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'{member.name} has been kicked.')
        if self.modlog_channel:
            await self.modlog_channel.send(f'{member.name} was kicked. Reason: {reason}')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount+1)
        await ctx.send(f'Deleted {amount} messages.')
        if self.modlog_channel:
            await self.modlog_channel.send(f'{amount} messages were deleted in {ctx.channel.name}.')

    @commands.command()
    async def status(self, ctx, *, status: str):
        await self.bot.change_presence(activity=discord.Game(name=status))
        await ctx.send(f'Bot status updated to: {status}')

    @commands.command()
    async def time(self, ctx):
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        await ctx.send(f'Current time: {now}')

    @commands.command()
    async def serverinfo(self, ctx):
        server = ctx.guild

        # Get server member count
        member_count = server.member_count

        # Get roles breakdown
        role_breakdown = {role.name: sum(1 for member in server.members if role in member.roles) for role in server.roles}

        # Get message activity in the last hour, day, and week
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        one_week_ago = datetime.utcnow() - timedelta(weeks=1)

        message_count_hour = 0
        message_count_day = 0
        message_count_week = 0

        for channel in server.text_channels:
            async for message in channel.history(after=one_hour_ago):
                message_count_hour += 1
            async for message in channel.history(after=one_day_ago):
                message_count_day += 1
            async for message in channel.history(after=one_week_ago):
                message_count_week += 1

        # Get channel activity (message counts)
        active_channels = {}
        async for channel in server.text_channels:
            message_count = 0
            async for message in channel.history(after=one_week_ago):
                message_count += 1
            if message_count > 0:
                active_channels[channel.name] = message_count

        # Create an embed with server information
        embed = discord.Embed(title=f"Server Info for {server.name}", description=f"Owner: {server.owner}", color=discord.Color.blue())
        embed.add_field(name="Total Members", value=member_count)
        embed.add_field(name="Messages in Last Hour", value=message_count_hour)
        embed.add_field(name="Messages in Last Day", value=message_count_day)
        embed.add_field(name="Messages in Last Week", value=message_count_week)
        embed.add_field(name="Role Breakdown", value="\n".join([f"{role}: {count}" for role, count in role_breakdown.items()]), inline=False)
        embed.add_field(name="Active Channels (Last 7 Days)", value="\n".join([f"{channel}: {count} messages" for channel, count in active_channels.items()]), inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member):
        embed = discord.Embed(title=member.name, description=f'ID: {member.id}', color=discord.Color.green())
        embed.add_field(name='Joined On', value=member.joined_at.strftime('%Y-%m-%d'))
        embed.add_field(name='Roles', value=', '.join([r.name for r in member.roles]))
        await ctx.send(embed=embed)

    @commands.command()
    async def send(self, ctx, channel: discord.TextChannel, *, message: str):
        await channel.send(message)
        await ctx.send(f'Message sent to {channel.mention}')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def logchannel(self, ctx, channel: discord.TextChannel):
        """Sets the channel where moderation logs will be sent."""
        self.modlog_channel = channel
        await ctx.send(f'Moderation logs will be sent to {channel.mention}.')

    @commands.command()
    async def modlog(self, ctx):
        """Displays the moderation log."""
        if self.modlog_channel:
            async for message in self.modlog_channel.history(limit=5):
                await ctx.send(f'{message.author}: {message.content}')
        else:
            await ctx.send("No moderation log channel has been set.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, role_name: str, emoji: str):
        """Send a message that users can react to in order to get a role."""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is None:
            await ctx.send(f"The role '{role_name}' doesn't exist.")
            return

        message = await ctx.send(f"React with {emoji} to get the '{role_name}' role.")
        await message.add_reaction(emoji)

        def check(reaction, user):
            return user != self.bot.user and str(reaction.emoji) == emoji and reaction.message.id == message.id

        async def assign_role():
            while True:
                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                member = ctx.guild.get_member(user.id)
                if member and role not in member.roles:
                    await member.add_roles(role)
                    await ctx.send(f'{user.name} has been given the {role_name} role.')

        self.bot.loop.create_task(assign_role())

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.add_cog(MyBot(bot))  # Add the MyBot Cog with await

bot.run("Your Bot Token Here")    # Replace with your bot's token
