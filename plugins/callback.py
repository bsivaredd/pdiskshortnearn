import asyncio
import re
from config import OWNER_ID
from database import update_user_info
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, CallbackQuery
from database.users import get_user
from helpers import temp
from translation import BACK_REPLY_MARKUP, HELP_MESSAGE, HELP_REPLY_MARKUP, ABOUT_TEXT, ABOUT_REPLY_MARKUP, START_MESSAGE, START_MESSAGE_REPLY_MARKUP
from utils import get_me_button
import os
import sys
import logging
from database import db
logger = logging.getLogger(__name__)

user_commands = ["shortener_api", "header", "footer", "username", "banner_image", "me"]

cmds = "\n\nAvailable commands:\n\n"
for x in user_commands:
    cmds+=f"- /{x}\n"
cmds += "\nUse the commands to know more about the same"

@Client.on_callback_query(filters.regex(r"^setgs"))
async def user_setting_cb(c,query: CallbackQuery):
    _, setting, toggle, user_id = query.data.split('#')
    myvalues = {setting:True if toggle == "True" else False}

    await update_user_info(user_id, myvalues)
    user = await get_user(user_id)
    buttons = await get_me_button(user)
    reply_markup = InlineKeyboardMarkup(buttons)
    try:
        await query.message.edit_reply_markup(reply_markup)

        setting = (re.sub(r"is|_", " ", setting)).title()
        toggle = "Enabled" if toggle == "True" else "Disabled"

        await query.answer(f"{setting} {toggle} Successfully", show_alert=True)

    except Exception as e:
        logging.error("Errors occurred while updating user information", exc_info=True)

@Client.on_callback_query()
async def on_callback_query(bot:Client, query:CallbackQuery):

    if query.data == 'delete':
        await query.message.delete()

    elif query.data == 'help_command':
        try:
            await query.message.edit(HELP_MESSAGE.format(
                firstname=temp.FIRST_NAME,
                username=temp.BOT_USERNAME,
                owner="@ask_admin001" ) + cmds, reply_markup=HELP_REPLY_MARKUP, disable_web_page_preview=True)
        except Exception as e:
            logging.exception(e)

    elif query.data == 'about_command':
        try:
            me = await bot.get_me()
            owner = await bot.get_users(OWNER_ID)
            await query.message.edit(ABOUT_TEXT.format(
                me.mention(style='md'),
                owner.mention(style='md'),), reply_markup=ABOUT_REPLY_MARKUP, disable_web_page_preview=True)
        except Exception as e:
            logging.exception(e)

    elif query.data == 'start_command':
        await query.message.edit(START_MESSAGE.format(
            query.message.from_user.mention,
            ), reply_markup=START_MESSAGE_REPLY_MARKUP, disable_web_page_preview=True)

    elif query.data == 'restart':
        await query.message.edit('**Restarting.....**')
        await asyncio.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif query.data == 'anc_command':
        try:
            anc = await db.get_announcements()
            n = "No copyrighted links available right now" if anc["text"] == "" else anc["text"]
            await query.message.edit(n, reply_markup=BACK_REPLY_MARKUP)
        except Exception as e:
            print(e)

    await query.answer()
