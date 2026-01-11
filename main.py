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

# --- IMPORT THU VIEN CUA BAN ---
from telethon import TelegramClient, events
try:
    from opentele.td import TDesktop
    from opentele.tl import TelegramClient as OpenteleClient
    from opentele.api import UseCurrentSession
except ImportError:
    print("❌ Lỗi: Chưa cài thư viện opentele")

# ==========================================
# 1. CẤU HÌNH PROXY (HTTP - Tunproxy)
# ==========================================
# Bat buoc phai co Proxy de khong chet Session
PROXY_CONF = (
    socks.HTTP,
    'Snvt9.tunproxy.com',
    25425,
    True,
    'nJmiIM',
    'vBNpmtH8'
)

# ==========================================
# 2. WEB SERVER (Giu Bot Online)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Convert TData (Opentele Integration)"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

# ==========================================
# 3. KHOI TAO BOT
# ==========================================
# 3. KHOI TAO BOT
# ==========================================
api_id = 36305655   # Day la so
api_hash = '58c19740ea1f5941e5847c0b3944f41d'  # Day la chu (co dau nhay)
bot_token = '8010513010:AAG8t1uExxFmc-ZiCrxILI0BwXMZ6iPUUFU' # Token cua ban

# Tao thu muc tam
if not os.path.exists('sessions'): os.makedirs('sessions')
if not os.path.exists('temp_process'): os.makedirs('temp_process')

logging.basicConfig(level=logging.INFO)

# QUAN TRONG: Phai dung thu tu (api_id truoc, api_hash sau)
bot = TelegramClient('bot_main_cloud', api_id, api_hash)
# 4. HAM CONVERT (LOGIC TU CODE CUA BAN)
# ==========================================
async def convert_process(event, downloaded_path):
    msg = await event.reply("⏳ **Đang xử lý theo thuật toán Opentele...**")
    
    # Lay ten file (VD: 849xxx)
    filename_w_ext = os.path.basename(downloaded_path)
    session_name = filename_w_ext.replace('.session', '')
    
    # 1. Tao cau truc thu muc rieng biet (Giong code ban gui)
    # root_folder: temp_process/849xxx_timestamp
    timestamp = int(time.time())
    root_folder = f"temp_process/{session_name}_{timestamp}"
    os.makedirs(root_folder, exist_ok=True)
    
    # 2. Copy file session vao trong root_folder (Bat buoc theo logic cua opentele)
    session_path_in_folder = os.path.join(root_folder, filename_w_ext)
    shutil.copy2(downloaded_path, session_path_in_folder)
    
    # Duong dan cho Opentele load (khong can duoi .session)
    path_to_load = os.path.join(root_folder, session_name)
    
    # Duong dan dich cho TData (Ben trong root_folder)
    tdata_folder_path = os.path.join(root_folder, "tdata")

    client_convert = None
    try:
        # --- KHOI TAO OPENTELE CLIENT ---
        # QUAN TRONG: Minh them PROXY vao day de bao ve session
        client_convert = OpenteleClient(path_to_load, api_id, api_hash, proxy=PROXY_CONF)
        
        await client_convert.connect()
        
        if not await client_convert.is_user_authorized():
            await msg.edit(f"☠️ **SESSION DIE:** File `{session_name}` không đăng nhập được.")
            await client_convert.disconnect()
            return

        # --- CHUYEN DOI SANG TDESKTOP ---
        # Logic: Load session -> ToTDesktop -> SaveTData
        tdesk = await client_convert.ToTDesktop(flag=UseCurrentSession)
        
        # Luu TData vao thu muc con "tdata"
        tdesk.SaveTData(tdata_folder_path)
        
        await client_convert.disconnect() # Ngat ket noi sau khi convert xong
        
        # --- NEN FILE ZIP ---
        await msg.edit("📦 **Đang nén TData...**")
        
        # Zip toan bo thu muc tdata
        # Output: temp_process/849xxx.zip
        zip_output_path = f"temp_process/{session_name}_{timestamp}"
        shutil.make_archive(zip_output_path, 'zip', tdata_folder_path)
        final_zip_file = zip_output_path + ".zip"
        
        # --- GUI FILE ---
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
        # --- DON DEP RAC ---
        try:
            if os.path.exists(root_folder): shutil.rmtree(root_folder) # Xoa folder tdata tam
            if os.path.exists(final_zip_file): os.remove(final_zip_file) # Xoa file zip
            if os.path.exists(downloaded_path): os.remove(downloaded_path) # Xoa file session tai ve
        except: pass

# ==========================================
# 5. SU KIEN NHAN FILE
# ==========================================
@bot.on(events.NewMessage)
async def handler(event):
    if event.file and event.file.name.endswith('.session'):
        # Luu file tam ra ngoai
        temp_path = f"sessions/{event.file.name}"
        
        msg_wait = await event.reply("⬇️ **Đang tải file về Server...**")
        try:
            await bot.download_media(event.message, temp_path)
            await msg_wait.delete()
            # Goi ham convert
            await convert_process(event, temp_path)
        except Exception as e:
            print(e)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("🛠 **Bot Convert TData (Opentele Core)**\n\nGửi file `.session` vào đây, tôi sẽ dùng thuật toán Opentele + Proxy để convert an toàn.")

if __name__ == '__main__':
    keep_alive()
    print("--- BOT STARTED ---")
    bot.start(bot_token=bot_token)
    bot.run_until_disconnected()

