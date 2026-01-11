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
# 1. CẤU HÌNH PROXY (QUAN TRỌNG)
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
    return "Bot Convert TData (Structure Fixed)"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

# ==========================================
# 3. KHOI TAO BOT
# ==========================================
bot = TelegramClient(
    'bot_main_cloud', 
    api_id=36305655,                       
    api_hash='58c19740ea1f5941e5847c0b3944f41d' 
)

bot_token = '8010513010:AAG8t1uExxFmc-ZiCrxILI0BwXMZ6iPUUFU'

if not os.path.exists('sessions'): os.makedirs('sessions')
if not os.path.exists('temp_process'): os.makedirs('temp_process')

logging.basicConfig(level=logging.INFO)

# ==========================================
# 4. HAM CONVERT (CẤU TRÚC Y HỆT FILE RAR)
# ==========================================
MY_API_ID = 36305655
MY_API_HASH = '58c19740ea1f5941e5847c0b3944f41d'

async def convert_process(event, downloaded_path):
    msg = await event.reply("⏳ **Đang xử lý cấu trúc chuẩn...**")
    
    filename_w_ext = os.path.basename(downloaded_path) # VD: +84123.session
    session_name = filename_w_ext.replace('.session', '') # VD: +84123
    
    # 1. Tao thu muc lam viec tam thoi (Work Dir)
    timestamp = int(time.time())
    work_dir = f"temp_process/work_{session_name}_{timestamp}"
    os.makedirs(work_dir, exist_ok=True)
    
    # 2. Tao thu muc cha (Container) ben trong Work Dir -> Day la thu muc ban se thay khi giai nen
    # VD: work_dir/+84123/
    container_folder = os.path.join(work_dir, session_name)
    os.makedirs(container_folder, exist_ok=True)

    # 3. Copy file .session vao trong container (Giong file RAR cua ban)
    # VD: work_dir/+84123/+84123.session
    session_path_in_container = os.path.join(container_folder, filename_w_ext)
    shutil.copy2(downloaded_path, session_path_in_container)
    
    # 4. Tao thu muc tdata ben trong container
    # VD: work_dir/+84123/tdata
    tdata_folder_path = os.path.join(container_folder, "tdata")
    
    # Duong dan de Opentele load (Load file session vua copy vao)
    path_to_load = os.path.join(container_folder, session_name)

    client_convert = None
    try:
        # KET NOI PROXY
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

        # CONVERT & LUU VAO FOLDER TDATA
        tdesk = await client_convert.ToTDesktop(flag=UseCurrentSession)
        tdesk.SaveTData(tdata_folder_path)
        await client_convert.disconnect()
        
        await msg.edit("📦 **Đang đóng gói...**")
        
        # 5. NEN FILE ZIP
        # Nen toan bo noi dung cua work_dir
        # Khi giai nen Zip se thay folder: +84123 -> ben trong co tdata
        zip_output_path = f"temp_process/{session_name}_{timestamp}"
        
        shutil.make_archive(
            zip_output_path, 
            'zip', 
            root_dir=work_dir 
        )
        
        final_zip_file = zip_output_path + ".zip"
        
        await msg.edit("⬆️ **Đang tải lên...**")
        
        # Gui file
        await bot.send_file(
            event.chat_id,
            final_zip_file,
            caption=f"✅ **Convert thành công!**\n📂 Folder: `{session_name}`\n(Cấu trúc chuẩn Telegram Portable)"
        )
        
        await msg.delete()

    except Exception as e:
        if "SOCKS" in str(e) or "Connection" in str(e):
             await msg.edit(f"❌ **Lỗi Proxy:** Kết nối thất bại.\nTunproxy có thể đang chậm.")
        else:
             await msg.edit(f"❌ **Lỗi Convert:**\n`{str(e)}`")
    
    finally:
        # Don rac
        try:
            if os.path.exists(work_dir): shutil.rmtree(work_dir)
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
    await event.respond("🛠 **Bot Convert TData (Full Structure)**\nGửi file .session vào đây, tôi sẽ trả về đúng cấu trúc thư mục bạn cần!")

if __name__ == '__main__':
    keep_alive()
    print("--- BOT STARTED ---")
    bot.start(bot_token=bot_token)
    bot.run_until_disconnected()
