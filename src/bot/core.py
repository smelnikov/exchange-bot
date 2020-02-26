import os

import telebot


from bot.views import ExchangeView, HistoryView, ListView


API_TOKEN = os.environ.get('API_TOKEN')

PROXY_BACKEND = os.environ.get('PROXY_BACKEND')


if PROXY_BACKEND:
    from telebot import apihelper

    apihelper.proxy = {'https': PROXY_BACKEND}


bot = telebot.TeleBot(API_TOKEN)


commands = {
    "list <base>":
        "returns list of all available rates for `base`",

    "exchange {amount} {base} to {currency}":
        "converts `amount` of `base` to `currency`\n"
        "ex.: /exchange 10 USD to CAD",

    "history {base} {currency} for {N} days":
        "return an image graph chart with the exchange rate of "
        "the selected `base`/`currency` for the last `N` days\n"
        "ex.: /history USD CAD for 7 days"
}


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    cid = message.chat.id
    help_text = "The following commands are available: \n\n"
    for key in commands:
        help_text += "/" + key + "\n"
        help_text += commands[key] + "\n\n"
    help_text += "Notes: 'USD' used by default if `base` not set."
    bot.send_message(cid, help_text)


@bot.message_handler(commands=['list'])
def send_list(message):
    """"""
    bot.reply_to(
        message,
        ListView(message.text).render()
    )


@bot.message_handler(commands=['exchange'])
def send_exchange(message):
    bot.reply_to(
        message,
        ExchangeView(message.text).render()
    )


@bot.message_handler(commands=['history'])
def send_history(message):
    cid = message.chat.id
    msgid = message.message_id
    response = HistoryView(message.text).render()
    is_text = isinstance(response, str)

    if is_text:
        bot.reply_to(
            message,
            response
        )
    else:
        bot.send_photo(
            cid,
            response,
            reply_to_message_id=msgid
        )
