import os
import threading
from flask import Flask
import time
import random
import asyncio
import logging
import shutil
import socks
import sys

from telethon import TelegramClient, events
try:
    from opentele.td import TDesktop
    from opentele.tl import TelegramClient as OpenteleClient
    from opentele.api import UseCurrentSession
except ImportError:
    print("❌ Lỗi: Chưa cài thư viện opentele")

# ==========================================
# 1. CẤU HÌNH PROXY
# ==========================================
PROXY_CONF = (
    socks.HTTP,
    'Snvt9.tunproxy.com',
    25425,
    True,
    'nJmiIM',
    'vBNpmtH8'
)

# ==========================================
# 2. WEB SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Convert TData Online"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

# ==========================================
# 3. KHOI TAO BOT (CHỐNG NHẦM LẪN 100%)
# ==========================================
# Dung cach nay (api_id=..., api_hash=...) thi khong bao gio bi loi nua
bot = TelegramClient(
    'bot_main_cloud', 
    api_id=36305655,                       # SO
    api_hash='58c19740ea1f5941e5847c0b3944f41d' # CHU (Bat buoc phai co dau nhay)
)

bot_token = '8010513010:AAG8t1uExxFmc-ZiCrxILI0BwXMZ6iPUUFU'

if not os.path.exists('sessions'): os.makedirs('sessions')
if not os.path.exists('temp_process'): os.makedirs('temp_process')

logging.basicConfig(level=logging.INFO)

# ==========================================
# 4. HAM CONVERT
# ==========================================
# Khai bao lai de dung cho ham convert
MY_API_ID = 36305655
MY_API_HASH = '58c19740ea1f5941e5847c0b3944f41d'

async def convert_process(event, downloaded_path):
    msg = await event.reply("⏳ **Đang xử lý theo thuật toán Opentele...**")
    
    filename_w_ext = os.path.basename(downloaded_path)
    session_name = filename_w_ext.replace('.session', '')
    
    timestamp = int(time.time())
    root_folder = f"temp_process/{session_name}_{timestamp}"
    os.makedirs(root_folder, exist_ok=True)
    
    session_path_in_folder = os.path.join(root_folder, filename_w_ext)
    shutil.copy2(downloaded_path, session_path_in_folder)
    
    path_to_load = os.path.join(root_folder, session_name)
    tdata_folder_path = os.path.join(root_folder, "tdata")

    client_convert = None
    try:
        # Gan the ten cho Opentele luon
        client_convert = OpenteleClient(
            path_to_load, 
            api_id=MY_API_ID, 
            api_hash=MY_API_HASH, 
            proxy=PROXY_CONF
        )
        await client_convert.connect()
        
        if not await client_convert.is_user_authorized():
            await msg.edit(f"☠️ **SESSION DIE:** File `{session_name}` không đăng nhập được.")
            await client_convert.disconnect()
            return

        tdesk = await client_convert.ToTDesktop(flag=UseCurrentSession)
        tdesk.SaveTData(tdata_folder_path)
        await client_convert.disconnect()
        
        await msg.edit("📦 **Đang nén TData...**")
        zip_output_path = f"temp_process/{session_name}_{timestamp}"
        shutil.make_archive(zip_output_path, 'zip', tdata_folder_path)
        final_zip_file = zip_output_path + ".zip"
        
        await msg.edit("⬆️ **Đang tải lên...**")
        await event.respond(
            file=final_zip_file,
            caption=f"✅ **Convert thành công!**\n📂 File: `{session_name}.zip`\n(Opentele Core)"
        )
        await msg.delete()

    except Exception as e:
        if "SOCKS" in str(e) or "Connection" in str(e):
             await msg.edit(f"❌ **Lỗi Proxy:** Kết nối thất bại.\nTunproxy có thể đang chậm.")
        else:
             await msg.edit(f"❌ **Lỗi Convert:**\n`{str(e)}`")
    
    finally:
        try:
            if os.path.exists(root_folder): shutil.rmtree(root_folder)
            if os.path.exists(final_zip_file): os.remove(final_zip_file)
            if os.path.exists(downloaded_path): os.remove(downloaded_path)
        except: pass

@bot.on(events.NewMessage)
async def handler(event):
    if event.file and event.file.name.endswith('.session'):
        temp_path = f"sessions/{event.file.name}"
        msg_wait = await event.reply("⬇️ **Đang tải file về Server...**")
        try:
            await bot.download_media(event.message, temp_path)
            await msg_wait.delete()
            await convert_process(event, temp_path)
        except Exception as e:
            print(e)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("🛠 **Bot Convert TData Ready**")

if __name__ == '__main__':
    keep_alive()
    print("--- BOT STARTED ---")
    bot.start(bot_token=bot_token)
    bot.run_until_disconnected()
