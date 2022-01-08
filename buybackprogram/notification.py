"""
notifications helper
"""
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import intcomma

from allianceauth.notifications import notify
from allianceauth.services.hooks import get_extension_logger

from buybackprogram.app_settings import allianceauth_discordbot_active
from buybackprogram.utils import get_site_url

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
    try:

        from discordproxy.client import DiscordClient
        from discordproxy.discord_api_pb2 import Embed

        # If user has the discord service activated
        if hasattr(user, "discord"):

            client = DiscordClient()

            disable_hit = "*You can disable these notifications from [My Settings]({0}/buybackprogram/user_settings_edit)*".format(
                get_site_url()
            )

            # Check if the contract was accepted or rejected
            if contract["status"] == "finished":
                status = "accepted"
            elif contract["status"] == "rejected":
                status = "rejected"
            else:
                status = contract["status"]

            footer = Embed.Footer(
                text="AA Buyback Program",
            )

            embed = Embed(
                description="Your buyback contract {0} for {1} has been processed. Your contract has been {2}.\n\n{3}".format(
                    tracking.tracking_number,
                    intcomma(int(contract["price"])),
                    status,
                    disable_hit,
                ),
                title="Contract {0}".format(status),
                footer=footer,
            )

            try:
                client.create_direct_message(user_id=user.discord.uid, embed=embed)
            except Exception:
                logger.error("An error occured when trying to create a message")
        else:
            logger.debug(
                "%s has no active discord services, skipping notification" % user
            )

    except ModuleNotFoundError:
        # If discordproxy app is not active we will check if aa-discordbot is active
        if allianceauth_discordbot_active():
            import aadiscordbot.tasks

            aadiscordbot.tasks.send_direct_message_by_user_id.delay(user.pk, message)

            logger.debug("Sent discord DM to user %s" % user.pk)
        else:
            logger.debug(
                "No discord notification modules active. Will not send user notifications"
            )


def send_message_to_discord_channel(
    tracking: str, contract: str, channel_id: int, message: str, embed: bool = False
) -> None:

    # Check if the discordproxy module is active. We will use it as our priority app for notifications
    try:

        from discordproxy.client import DiscordClient
        from discordproxy.discord_api_pb2 import Embed

        client = DiscordClient()

        disable_hit = (
            "*You can disable these notifications from your program settings.*"
        )

        footer = Embed.Footer(
            text="AA Buyback Program",
        )

        embed = Embed(
            description="A new buyback contract {0} with a vlue of {1} has been assigned for you.\n\n{2}".format(
                tracking.tracking_number, intcomma(int(contract["price"])), disable_hit
            ),
            title="New buyback contract assigned",
            footer=footer,
        )

        try:
            client.create_channel_message(channel_id=channel_id, embed=embed)
            logger.debug("Sent contract notification to channel %s" % channel_id)
        except Exception:
            logger.error("An error occured when trying to send a channel message")

    except ModuleNotFoundError:
        if allianceauth_discordbot_active():
            import aadiscordbot.tasks

            aadiscordbot.tasks.send_channel_message_by_discord_id.delay(
                channel_id, message, embed
            )
        else:
            logger.debug(
                "No discord notification modules active. Will not send user channel notifications"
            )
