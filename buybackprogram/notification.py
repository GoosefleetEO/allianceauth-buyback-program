"""
notifications helper
"""
from django.contrib.auth.models import User

from allianceauth.notifications import notify
from allianceauth.services.hooks import get_extension_logger

from buybackprogram.app_settings import allianceauth_discordbot_active

logger = get_extension_logger(__name__)


def send_user_notification(user: User, level: str, message: dict) -> None:

    # Send AA text notification
    notify(
        user=user,
        title=message["title"],
        level=level,
        message=message["description"],
    )

    # Check if the discordproxy module is active. We will use it as our priority app for notifications
    try:

        from discordproxy.client import DiscordClient
        from discordproxy.discord_api_pb2 import Embed
        from discordproxy.exceptions import DiscordProxyException

        logger.debug("User has a active discord account")

        client = DiscordClient()

        embed = Embed(
            description=message["description"],
            title=message["title"],
            footer=Embed.Footer(text=message["footer"]),
        )

        try:
            logger.debug("Sending notification for discord user %s" % user.discord.uid)
            client.create_direct_message(user_id=user.discord.uid, embed=embed)
        except DiscordProxyException as ex:
            logger.error("An error occured when trying to create a message: %s" % ex)

    except ModuleNotFoundError:
        # If discordproxy app is not active we will check if aa-discordbot is active
        if allianceauth_discordbot_active():
            import aadiscordbot.tasks

            aadiscordbot.tasks.send_direct_message_by_user_id.delay(
                user.pk, message["description"]
            )

            logger.debug("Sent discord DM to user %s" % user.pk)
        else:
            logger.debug(
                "No discord notification modules active. Will not send user notifications"
            )


def send_message_to_discord_channel(
    channel_id: int, message: str, embed: bool = False
) -> None:

    # Check if the discordproxy module is active. We will use it as our priority app for notifications
    try:

        from discordproxy.client import DiscordClient
        from discordproxy.discord_api_pb2 import Embed
        from discordproxy.exceptions import DiscordProxyException

        client = DiscordClient()

        embed = Embed(
            description=message["description"],
            title=message["title"],
            footer=Embed.Footer(text=message["footer"]),
        )

        try:
            client.create_channel_message(channel_id=channel_id, embed=embed)
        except DiscordProxyException as ex:
            logger.error("An error occured when trying to create a message: %s" % ex)

    except ModuleNotFoundError:
        if allianceauth_discordbot_active():
            import aadiscordbot.tasks

            aadiscordbot.tasks.send_channel_message_by_discord_id.delay(
                channel_id, message["description"], embed
            )
        else:
            logger.debug(
                "No discord notification modules active. Will not send user channel notifications"
            )
