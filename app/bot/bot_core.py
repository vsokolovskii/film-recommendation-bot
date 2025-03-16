import logging

import telebot

from app.agent.agent import agent
from app.clients.sqlite import sqlite_client
from app.settings import settings

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(settings.telegram_bot_token, parse_mode=None)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    user_info = f"User ID: {message.from_user.id}, First Name: {message.from_user.first_name}, Last Name: {message.from_user.last_name}, Username: {message.from_user.username}"
    logger.info(f"New user interaction: {user_info}")
    print(f"New user interaction: {user_info}")
    sqlite_client.add_new_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
    bot.reply_to(message, f"Hello {message.from_user.first_name}! I can help you find a movie to watch based on your preferences. Tell me your favorite movie and I'll suggest something you might like.")


@bot.message_handler(func=lambda message: True)
def respond_to_message(message):
    user_info = f"User ID: {message.from_user.id}, Message: {message.text}"
    logger.info(f"Processing message: {user_info}")
    response = agent.run(message.text, reset=False, additional_args={"user_id": message.from_user.id})
    bot.reply_to(message, response)
    agent.write_memory_to_messages()
