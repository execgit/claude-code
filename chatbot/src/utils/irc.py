import irc.bot
import irc.strings
import time
import uuid
import textwrap

from config.settings import settings
from src.utils.logging import setup_logger  # noqa: E402

DEFAULT_RESPONSE = "Divano Divino automated support. State your issue via PRIVMSG."

# Fixes lifted from
# https://opendev.org/openstack/ptgbot/src/commit/287f8d5/ptgbot/bot.py#L114-L115
irc.client.ServerConnection.buffer_class.errors = 'replace'
# If a long message is split, how long to sleep between sending parts
# of a message.  This is lower than the general recommended interval,
# but in practice IRC networks allows short bursts at a higher rate.
MESSAGE_CONTINUATION_SLEEP = 0.5
# The amount of time to sleep between messages.
ANTI_FLOOD_SLEEP = 2

logger = setup_logger(__name__)

class IrcBot(irc.bot.SingleServerIRCBot):
    def __init__(self, message_handler):
        nick = uuid.uuid1().hex[:8]
        logger.info(f"Joining server {settings.irc_server}")
        irc.bot.SingleServerIRCBot.__init__(
            self,
            [(settings.irc_server, settings.irc_port, settings.irc_password)],
            nick,
            nick,
        )
        self.channel = settings.irc_channel
        self.message_handler = message_handler

    def send(self, channel, msg):
        # 400 chars is an estimate of a safe line length (which can vary)
        chunks = textwrap.wrap(msg, 400)
        for count, chunk in enumerate(chunks):
            self.connection.privmsg(channel, chunk)
            if count:
                time.sleep(MESSAGE_CONTINUATION_SLEEP)
        time.sleep(ANTI_FLOOD_SLEEP)

    def on_nicknameinuse(self, c, e):
        logger.info("IRC: Nick in use")
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        logger.info("IRC: Got welcome")
        time.sleep(5)
        logger.info(f"Sending IDENTIFY")
        self.send("NickServ", f"IDENTIFY {settings.irc_nick} {settings.irc_nickserv_pass}")
        time.sleep(2)
        logger.info(f"Joining channel {self.channel}")
        self.connection.join(self.channel)

    def on_privmsg(self, c, e):
        nick = e.source.nick
        c = self.connection

        response = self.message_handler("".join(e.arguments))
        self.send(nick, response)

    def on_pubmsg(self, c, e):
        c = self.connection

        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(
            self.connection.get_nickname()
        ):
            c.notice(self.channel, DEFAULT_RESPONSE)

