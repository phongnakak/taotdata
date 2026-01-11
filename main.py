import os
import threading
from flask import Flask
import time
import random
import asyncio
import logging
import shutil
import builtins
import getpass
import sys
import socks  # Bat buoc phai co pysocks
from telethon import TelegramClient, events

try:
    from opentele.td import TDesktop
except ImportError:
    print("❌ Lỗi: Chưa cài thư viện opentele")

# ==========================================
# 1. CẤU HÌNH PROXY (HTTP - Tunproxy)
# ==========================================
PROXY_CONF = (
    socks.HTTP,              # Chay HTTP
    'Snvt9.tunproxy.com',    # Host
    25425,                   # Port
    True,                    # rdns
    'nJmiIM',                # Username
    'vBNpmtH8'               # Password
)

# ==========================================
# 2. WEB SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Convert TData Online (Proxy Enabled)"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

# ==========================================
# 3. CẤU HÌNH BOT
# ==========================================
api_id = 36305655
api_hash = '58c19740ea1f5941e5847c0b3944f41d'

# Token ban da dien san:
bot_token = '8010513010:AAG8t1uExxFmc-ZiCrxILI0BwXMZ6iPUUFU' 

if not os.path.exists('sessions'): os.makedirs('sessions')
if not os.path.exists('temp_tdata'): os.makedirs('temp_tdata')

logging.basicConfig(level=logging.ERROR)

# Bot chinh chay mang Render
bot = TelegramClient('bot_convert_cloud', api_id, api_hash)

# ==========================================
# 4. HÀM XỬ LÝ CONVERT (CÓ PROXY)
# ==========================================
async def process_convert(event, session_path):
    msg = await event.reply("⏳ **Đang kết nối Proxy & Convert...**")
    
    original_name = event.file.name.replace('.session', '')
    tdata_folder = f"temp_tdata/{original_name}"
    zip_output_path = f"temp_tdata/{original_name}" 
    final_zip_file = f"temp_tdata/{original_name}.zip"

    client_convert = None
    try:
        # --- KET NOI QUA PROXY ---
        client_convert = TelegramClient(session_path, api_id, api_hash, proxy=PROXY_CONF)
        
        # Khoi tao TData
        tdesk = TDesktop(tdata_folder)
        
        async with client_convert:
            # Login vao session qua Proxy
            await tdesk.LoadFromClient(client_convert)
            # Luu ra TData
            tdesk.SaveTData(tdata_folder)
        
        # Nen file
        await msg.edit("📦 **Đang nén file Zip...**")
        shutil.make_archive(zip_output_path, 'zip', tdata_folder)

        # Gui file
        await msg.edit("⬆️ **Đang tải lên...**")
        await event.respond(
            file=final_zip_file,
            caption=f"✅ **Convert thành công!**\n(Đã fake IP Việt Nam an toàn)\n📂 File: `{original_name}.zip`"
        )
        await msg.delete()

    except Exception as e:
        if "SOCKS" in str(e) or "Connection" in str(e):
             await msg.edit(f"❌ **Lỗi Proxy:** Kết nối thất bại.\nCheck lại Tunproxy.")
        else:
             await msg.edit(f"❌ **Lỗi Convert:**\n`{str(e)}`")
    
    finally:
        # Don rac
        try:
            if os.path.exists(tdata_folder): shutil.rmtree(tdata_folder)
            if os.path.exists(final_zip_file): os.remove(final_zip_file)
            if client_convert: await client_convert.disconnect()
        except: pass

# ==========================================
# 5. SỰ KIỆN NHẬN FILE
# ==========================================
@bot.on(events.NewMessage)
async def handler(event):
    if event.file and event.file.name.endswith('.session'):
        random_id = int(time.time()) + random.randint(1, 99999)
        temp_path = f"sessions/convert_{random_id}.session"
        try:
            await bot.download_media(event.message, temp_path)
            await process_convert(event, temp_path)
        finally:
            if os.path.exists(temp_path): os.remove(temp_path)
            if os.path.exists(temp_path + '-journal'): os.remove(temp_path + '-journal')

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("🛠 **Bot Convert TData (VN Proxy)**\n\nGửi file `.session` vào đây, tôi sẽ dùng Proxy Việt Nam để convert an toàn.")

if __name__ == '__main__':
    keep_alive()
    print("--- BOT CONVERT STARTED ---")
    bot.start(bot_token=bot_token)
    bot.run_until_disconnected()