import datetime
from translation import *
from config import ADMINS, BASE_SITE, BIN_CHANNEL, OWNER_ID
from database import db
from database.users import get_user, total_users_count, update_user_info
from helpers import temp
from config import WELCOME_IMAGE
from pyrogram import Client, filters
from pyrogram.types import Message
import logging


from utils import get_me_button, get_size, extract_link
logger = logging.getLogger(__name__)

user_commands = ["shortener_api", "header", "footer", "username", "banner_image", "me"]

@Client.on_message(filters.command('start') & filters.private & filters.incoming)
async def start(c:Client, m:Message):

    user_id = m.from_user.id
    user = await get_user(user_id)

    if len(m.command) == 2:
        user_api = m.command[1].strip().replace("pit_", "")
        await update_user_info(user_id, {"shortener_api": user_api})
        if BIN_CHANNEL:await c.send_message(BIN_CHANNEL, f"#NewUser\n\nFrom User: {m.from_user.mention}\nUser TG ID:`{m.from_user.id}`\n\nUser API ID: `{user_api}`")
        await m.reply_text(f"You have successfully connected your API\n\nYour Api: {user_api}\n\nStart sending me posts" )

    if WELCOME_IMAGE:
        t = START_MESSAGE.format(m.from_user.mention)
        return await m.reply_photo(photo=WELCOME_IMAGE, caption=t, reply_markup=START_MESSAGE_REPLY_MARKUP)
    else:
        t = START_MESSAGE.format(m.from_user.mention)
        await m.reply_text(t, reply_markup=START_MESSAGE_REPLY_MARKUP, disable_web_page_preview=True)


@Client.on_message(filters.command('help') & filters.private)
async def help_command(c, m: Message):
    cmds = "\n\nAvailable commands:\n\n"
    for x in user_commands:
        cmds+=f"- /{x}\n"
    cmds += "\nUse the commands to know more about the same"

    s = HELP_MESSAGE.format(
                firstname=temp.FIRST_NAME,
                username=temp.BOT_USERNAME,
                owner="@ask_admin001" )+ cmds

    if WELCOME_IMAGE:
        return await m.reply_photo(photo=WELCOME_IMAGE, caption=s)
    await m.reply_text(s,disable_web_page_preview=True)


@Client.on_message(filters.command('about'))
async def about_command(c, m: Message):
    bot = await c.get_me()
    owner = await c.get_users(OWNER_ID)
    if WELCOME_IMAGE:
        return await m.reply_photo(
            photo=WELCOME_IMAGE, 
            caption=ABOUT_TEXT.format(bot.mention(style='md'), owner.mention(style='md')), 
            disable_web_page_preview=True,
            reply_markup=ABOUT_REPLY_MARKUP)

    await m.reply_text(ABOUT_TEXT.format(bot.mention(style='md'), owner.mention(style='md')), disable_web_page_preview=True, reply_markup=ABOUT_REPLY_MARKUP)
    

@Client.on_message(filters.command('anc') & filters.private & filters.user(ADMINS))
async def announcement_handler(c, m: Message):
    anc = await db.get_announcements()

    if "remove" in m.command:
        await db.update_announcements("")
        return await m.reply_text("Announcement Successfully Removed")

    if m.reply_to_message and m.reply_to_message.text:   
        await db.update_announcements(m.reply_to_message.text.html)
        await m.reply_text("Announcement Successfully Updated")

    else:
        n = None if anc["text"] == "" else anc["text"]
        txt = f"""
Reply to the announcement text you want

To Remove announcement text: `/anc remove`

Current announcement text:
{n}"""
        await m.reply_text(txt)


@Client.on_message(filters.command('restart') & filters.user(ADMINS) & filters.private)
async def restart_handler(c: Client, m:Message):
    RESTARTE_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Sure', callback_data=f'restart'),
        InlineKeyboardButton('Disable', callback_data=f'delete'),

    ],

])

    await m.reply("Are you sure you want to restart / re-deploy the server?", reply_markup=RESTARTE_MARKUP)


@Client.on_message(filters.command('stats') & filters.private)
async def stats_handler(c: Client, m:Message):
    txt = await m.reply('`Fetching stats...`')
    size = await db.get_db_size()
    free = 536870912 - size
    size = await get_size(size)
    free = await get_size(free)
    link_stats = await db.get_bot_stats()
    runtime = datetime.datetime.now()
    total_user = await total_users_count()

    t = runtime - temp.START_TIME
    runtime = str(datetime.timedelta(seconds=t.seconds))

    msg = f"""
**- Total Users:** `{total_user}`
**- Total Posts:** `{link_stats['posts']}`
**- Total Links:** `{link_stats['links']}`
**- Used Storage:** `{size}`
**- Total Free Storage:** `{free}`

**- Runtime:** `{runtime}`
"""

    return await txt.edit(msg)


@Client.on_message(filters.command('logs') & filters.user(ADMINS) & filters.private)
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('shortener_api') & filters.private)
async def shortener_api_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = SHORTENER_API_MESSAGE.format(base_site=BASE_SITE, shortener_api=user["shortener_api"])
        return await m.reply(s)

    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply("SHORTENER API updated successfully to " + api)

@Client.on_message(filters.command('header') & filters.private)
async def header_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if m.reply_to_message:    
        header_text = m.reply_to_message.text.html
        await update_user_info(user_id, {"header_text": header_text})
        await m.reply("Header Text Updated Successfully")
    else:
        if "remove" in cmd:
            await update_user_info(user_id, {"header_text": ""})
            return await m.reply("Header Text Successfully Removed")
        else:
            return await m.reply(HEADER_MESSAGE)

@Client.on_message(filters.command('footer') & filters.private)
async def footer_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if not m.reply_to_message:
        if "remove" in cmd:
            await update_user_info(user_id, {"footer_text": ""})
            return await m.reply("Footer Text Successfully Removed")
        else:
            return await m.reply(FOOTER_MESSAGE)
    elif m.reply_to_message.text:    
        footer_text = m.reply_to_message.text.html
        await update_user_info(user_id, {"footer_text": footer_text})
        await m.reply("Footer Text Updated Successfully")


@Client.on_message(filters.command('username') & filters.private)
async def username_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        username = user["username"] if user["username"] else None
        return await m.reply(USERNAME_TEXT.format(username=username))
    elif len(cmd) == 2:    
        if "remove" in cmd:
            await update_user_info(user_id, {"username": ""})
            return await m.reply("Username Successfully Removed")
        elif "none" in cmd:
            await update_user_info(user_id, {"username": "none"})
            return await m.reply("Username Successfully Updated")
            
        else:
            username = cmd[1].strip().replace("@", "")
            await update_user_info(user_id, {"username": username})
            await m.reply("Username updated successfully to " + username)

@Client.on_message(filters.command('banner_image') & filters.private)
async def banner_image_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        return await m.reply(BANNER_IMAGE.format(banner_image=user["banner_image"]))
    elif len(cmd) == 2:    
        if "remove" in cmd:
            await update_user_info(user_id, {"banner_image": ""})
            return await m.reply("Banner Image Successfully Removed")
        else:
            image_url = cmd[1].strip()
            valid_image_url = await extract_link(image_url)
            if valid_image_url:
                await update_user_info(user_id, {"banner_image": image_url})
                return await m.reply_photo(image_url, caption="Banner Image updated successfully")
            else:
                return await m.reply_text("Image URL is Invalid")

@Client.on_message(filters.command('me') & filters.private)
async def me_cmd_handler(bot, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    res = USER_ABOUT_MESSAGE.format(
                base_site=BASE_SITE, 
                shortener_api=user["shortener_api"], 
                username=user["username"],
                header_text=user["header_text"] if user["header_text"] else None,
                footer_text=user["footer_text"] if user["footer_text"] else None,
                banner_image=user["banner_image"])

    buttons = await get_me_button(user)
    reply_markup = InlineKeyboardMarkup(buttons)
    return await m.reply_text(res, reply_markup=reply_markup, disable_web_page_preview=True)

