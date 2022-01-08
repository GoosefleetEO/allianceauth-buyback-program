"""
notifications helper
"""
from django.contrib.auth.models import User

from allianceauth.notifications import notify
from allianceauth.services.hooks import get_extension_logger

from buybackprogram.app_settings import (
    aa_discordproxy_active,
    allianceauth_discordbot_active,
)

logger = get_extension_logger(__name__)


def send_user_notification(
    user: User, level: str, title: str, message: str, tracking: str, contract: str
) -> None:

    # Send AA text notification
    notify(
        user=user,
        title=title,
        level=level,
        message=message,
    )

    # Check if the discordproxy module is active. We will use it as our priority app for notifications
    if aa_discordproxy_active():

        # If user has the discord service activated
        if hasattr(user, "discord"):

            from discordproxy.client import DiscordClient
            from discordproxy.discord_api_pb2 import Embed

            client = DiscordClient()
            embed = Embed(
                description="Your buyback contract {0} has been accepted and the contract has been completed.".format(
                    tracking.tracking_number
                ),
                title="Contract accepted",
            )

            try:
                client.create_direct_message(user_id=user.discord.uid, embed=embed)
            except Exception:
                logger.error("An error occured when trying to create a message")

    # If discordproxy app is not active we will check if aa-discordbot is active
    elif allianceauth_discordbot_active():
        import aadiscordbot.tasks

        aadiscordbot.tasks.send_direct_message_by_user_id.delay(user.pk, message)

        logger.debug("Sent discord DM to user %s" % user.pk)
    else:
        logger.debug(
            "No discord notification modules active. Will not send user notifications"
        )


def send_message_to_discord_channel(
    channel_id: int, message: str, embed: bool = False
) -> None:

    if aa_discordproxy_active():

        from discordproxy.client import DiscordClient
        from discordproxy.discord_api_pb2 import Embed

        client = DiscordClient()
        embed = Embed(
            description="A new buyback contract has been created for you.",
            title="New buyback contract created",
        )

        try:
            client.create_channel_message(channel_id=channel_id, embed=embed)
            logger.debug("Sent contract notification to channel %s" % channel_id)
        except Exception:
            logger.error("An error occured when trying to send a channel message")

    elif allianceauth_discordbot_active():
        import aadiscordbot.tasks

        aadiscordbot.tasks.send_channel_message_by_discord_id.delay(
            channel_id, message, embed
        )
    else:
        logger.debug(
            "No discord notification modules active. Will not send user channel notifications"
        )
