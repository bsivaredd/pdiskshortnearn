import re
import json
from pyrogram import Client
from database import db
from shortzy import Shortzy
from config import *
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from pyrogram.enums import ParseMode
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def main_convertor_handler(message:Message, user=None):

    header_text = user["header_text"] if user["is_header_text"] else ""
    footer_text = user["footer_text"] if user["is_footer_text"] else ""
    username = user["username"] if user["is_username"] else None
    banner_image = user["banner_image"] if user["is_banner_image"] else None

    caption = None

    if message.text:
        caption = message.text.html
    elif message.caption:
        caption = message.caption.html

    # caption = caption.replace("--", "")

    # Checking if the message has any link or not. If it doesn't have any link, it will return.
    if len(await extract_link(caption)) <=0 and not message.reply_markup:
        return

    # Replacing the username with your username.
    caption = await replace_username(caption, username)

    # Getting the function for the user's method
    method_func = replace_link

    # converting urls
    shortenedText = await method_func(user, caption)

    # converting reply_markup urls
    reply_markup = await reply_markup_handler(message, method_func, user)

    # Adding header and footer
    # shortenedText = f"{header_text}\n{shortenedText}\n{footer_text}"

    shortenedText = f"{header_text}\n{shortenedText}\n{footer_text}"

    # Used to get the file_id of the media. If the media is a photo and BANNER_IMAGE is set, it will
    # replace the file_id with the BANNER_IMAGE.
    if message.media:
        medias = getattr(message, message.media.value)
        fileid = medias.file_id
        if message.photo and banner_image:
            fileid = banner_image

    if message.text:
        return await message.reply(shortenedText, disable_web_page_preview=True, reply_markup=reply_markup, quote=True, parse_mode=ParseMode.HTML)

    elif message.media:

        if message.document:
            return await message.reply_document(fileid, caption=shortenedText, reply_markup=reply_markup, quote=True, parse_mode=ParseMode.HTML)

        
        elif message.photo:
            return await message.reply_photo(fileid, caption=shortenedText, reply_markup=reply_markup, quote=True, parse_mode=ParseMode.HTML)


# Reply markup 
async def reply_markup_handler(message:Message, method_func, user):
    if message.reply_markup:
        reply_markup = json.loads(str(message.reply_markup))
        buttsons = []
        for markup in reply_markup["inline_keyboard"]:
            buttons = []
            for j in markup:
                text = j["text"]
                url = j["url"]
                url = await method_func(user, url)
                button = InlineKeyboardButton(text, url=url)
                buttons.append(button)
            buttsons.append(buttons)
        reply_markup = InlineKeyboardMarkup(buttsons)
        return reply_markup


#  ----- droplink ----
async def replace_link(user, text, x=""):

    api_key = user["shortener_api"]
    base_site = BASE_SITE

    shortzy = Shortzy(api_key, base_site)
    
    links = await extract_link(text)

    for link in links:

        long_url = link
        # Include domain validation 
        try:
            short_link = await shortzy.convert(link, x)
            text = text.replace(long_url, short_link)
        except Exception as e:
            logging.exception("Error converting link to short link: %s" % e)

    return text

####################  Replace Username  ####################
async def replace_username(text, username):
    if username:
        replace_text = f"@{username}" if username != "none" else ""
        usernames = re.findall("([@#][A-Za-z0-9_]+)", text)
        for i in usernames:
            text = text.replace(i, replace_text)
    return text
    

#####################  Extract all urls in a string ####################
async def extract_link(string):
    regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    urls = re.findall(regex, string)
    return ["".join(x) for x in urls]

async def broadcast_admins(c: Client, Message, sender=False):

    admins = ADMINS[:]
    
    if sender:
        admins.remove(sender)

    for i in admins:
        try:
            await c.send_message(i, Message)
        except PeerIdInvalid:
            logging.info(f"{i} have not yet started the bot")
    return

async def get_size(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

async def update_stats(m:Message):
    reply_markup = str(m.reply_markup) if m.reply_markup else ''
    message = m.caption.html if m.caption else m.text.html

    short_links = await extract_link(message + reply_markup)
    total_links = len(short_links)

    await db.update_posts(1)

    await db.update_links(total_links, len(short_links))

async def get_me_button(user):
    user_id = user["user_id"]
    buttons = []
    try:
        buttons =  [
                [
                    InlineKeyboardButton('Header Text',
                                        callback_data=f'ident'),
                    InlineKeyboardButton('✅ Enable' if not user["is_header_text"] else '❌ Disable',
                                        callback_data=f'setgs#is_header_text#{not user["is_header_text"]}#{str(user_id)}')
                ],
                [
                    InlineKeyboardButton('Footer Text', callback_data='ident'),
                    InlineKeyboardButton('✅ Enable' if not user["is_footer_text"] else '❌ Disable',
                                        callback_data=f'setgs#is_footer_text#{not user["is_footer_text"]}#{str(user_id)}')
                ],
                [
                    InlineKeyboardButton('Username',
                                        callback_data=f'ident'),
                    InlineKeyboardButton('✅ Enable' if not user["is_username"] else '❌ Disable',
                                        callback_data=f'setgs#is_username#{not user["is_username"]}#{str(user_id)}')
                ],
                [
                    InlineKeyboardButton('Banner Image', callback_data=f'ident'),
                    InlineKeyboardButton('✅ Enable' if not user["is_banner_image"] else '❌ Disable',
                                        callback_data=f'setgs#is_banner_image#{not user["is_banner_image"]}#{str(user_id)}')
                ],
            ]
    except Exception as e:
        print(e)
    return buttons