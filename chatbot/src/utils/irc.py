import irc.bot
import irc.strings

from config.settings import settings

DEFAULT_RESPONSE = "Divano Divino automated support. " + "State your issue via PRIVMSG."


class IrcBot(irc.bot.SingleServerIRCBot):
    def __init__(self, message_handler):
        irc.bot.SingleServerIRCBot.__init__(
            self,
            [(settings.irc_server, settings.irc_port, settings.irc_password)],
            settings.irc_nick,
            settings.irc_nick,
        )
        self.channel = settings.irc_channel
        self.message_handler = message_handler

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        nick = e.source.nick
        c = self.connection

        response = self.message_handler("".join(e.arguments))
        for line in response.splitlines():
            c.notice(nick, line)

    def on_pubmsg(self, c, e):
        c = self.connection

        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(
            self.connection.get_nickname()
        ):
            c.notice(self.channel, DEFAULT_RESPONSE)
