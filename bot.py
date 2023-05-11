import datetime
import asyncio
import aiohttp
from aiohttp import web
from pyrogram import Client
from config import *
from database import db
from helpers import temp, ping_server
from utils import broadcast_admins

import logging
import logging.config


logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)




class Bot(Client):

    def __init__(self):
        super().__init__(
        "shortener",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins")
        )

    async def start(self): 

        temp.START_TIME = datetime.datetime.now()
        await super().start()
        me = await self.get_me()
        self.username = '@' + me.username
        temp.BOT_USERNAME = me.username
        temp.FIRST_NAME = me.first_name

        if not await db.get_bot_stats():
            await db.create_stats()
        await db.get_announcements()  
        await broadcast_admins(self, f'** {self.username} Bot started successfully **')

        await self.send_message(int(BIN_CHANNEL), f'{self.username} Bot started')

        logging.info(f'{self.username} Bot started')

        if REPLIT:

            routes = web.RouteTableDef()
            @routes.get("/", allow_head=True)
            
            async def root_route_handler(request):
                res = {
                    "status": "running",
                }
                return web.json_response(res)

            async def web_server():
                web_app = web.Application(client_max_size=30000000)
                web_app.add_routes(routes)
                return web_app

            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", 8000).start()
            
    async def stop(self, *args):
        await broadcast_admins(self, '** Bot Stopped Bye **')
        await super().stop()
        logging.info('Bot Stopped Bye')

