import os
import threading
from flask import Flask
import time
import asyncio
import logging
import shutil
import socks
import sys

# Import Telethon
from telethon import TelegramClient, events
from telethon.errors import PasswordHashInvalidError

# Import Opentele
try:
    from opentele.td import TDesktop
    from opentele.tl import TelegramClient as OpenteleClient
    from opentele.api import UseCurrentSession
except ImportError:
    print("❌ Lỗi: Chưa cài thư viện opentele")

# ==========================================
# 1. CẤU HÌNH (PROXY & PASS 2FA)
# ==========================================
PROXY_CONF = (
    socks.HTTP,
    'Snvt9.tunproxy.com',
    25425,
    True,
    'nJmiIM',
    'vBNpmtH8'
)

DEFAULT_2FA_PASS = "12341234" # Mat khau 2FA ban muon cai

# ==========================================
# 2. WEB SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Convert TData V5 (Auto 2FA)"

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
# 4. HAM CONVERT + SET 2FA
# ==========================================
MY_API_ID = 36305655
MY_API_HASH = '58c19740ea1f5941e5847c0b3944f41d'

async def convert_process(event, downloaded_path):
    msg = await event.reply("⏳ **Đang xử lý & Cài 2FA...**")
    
    filename_w_ext = os.path.basename(downloaded_path) 
    session_name = filename_w_ext.replace('.session', '') 
    
    # Tao thu muc lam viec
    timestamp = int(time.time())
    work_dir = f"temp_process/work_{session_name}_{timestamp}"
    os.makedirs(work_dir, exist_ok=True)
    
    # Tao thu muc CHINH (Ket qua)
    container_folder = os.path.join(work_dir, session_name)
    os.makedirs(container_folder, exist_ok=True)

    # Copy session vao
    shutil.copy2(downloaded_path, os.path.join(container_folder, filename_w_ext))
    
    # Tao folder tdata
    tdata_folder_path = os.path.join(container_folder, "tdata")
    path_to_load = os.path.join(container_folder, session_name)
    
    # Tao file TXT ghi pass
    txt_pass_path = os.path.join(container_folder, "pass_2fa.txt")

    client_convert = None
    log_2fa = ""
    
    try:
        # KET NOI
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

        # --- BAT DAU DOAN CODE CAI 2FA ---
        try:
            # Thu cai mat khau moi
            await client_convert.edit_2fa(new_password=DEFAULT_2FA_PASS)
            log_2fa = f"✅ Đã bật 2FA: {DEFAULT_2FA_PASS}"
            
            # Ghi file txt neu cai thanh cong
            with open(txt_pass_path, "w", encoding="utf-8") as f:
                f.write(f"Account: {session_name}\nPass 2FA: {DEFAULT_2FA_PASS}\nStatus: Active")
                
        except Exception as e_2fa:
            # Neu da co pass hoac loi thi bo qua
            if "Password" in str(e_2fa):
                log_2fa = "⚠️ Nick đã có 2FA từ trước (Không đổi)."
                with open(txt_pass_path, "w", encoding="utf-8") as f:
                    f.write(f"Account: {session_name}\nPass 2FA: Đã có sẵn (Không phải {DEFAULT_2FA_PASS})")
            else:
                log_2fa = f"⚠️ Lỗi set 2FA: {str(e_2fa)}"
        # ---------------------------------

        # CONVERT TDATA
        tdesk = await client_convert.ToTDesktop(flag=UseCurrentSession)
        tdesk.SaveTData(tdata_folder_path)
        await client_convert.disconnect()
        
        await msg.edit(f"📦 **Đang đóng gói...**\n({log_2fa})")
        
        # NEN ZIP
        zip_output_path = f"temp_process/{session_name}"
        shutil.make_archive(zip_output_path, 'zip', root_dir=work_dir)
        final_zip_file = zip_output_path + ".zip"
        
        await msg.edit("⬆️ **Đang tải lên...**")
        
        await bot.send_file(
            event.chat_id,
            final_zip_file,
            caption=f"✅ **Xong!**\n📂 Folder: `{session_name}`\n🔐 {log_2fa}",
            force_document=True
        )
        
        await msg.delete()

    except Exception as e:
        if "SOCKS" in str(e) or "Connection" in str(e):
             await msg.edit(f"❌ **Lỗi Proxy:** Mạng chậm.")
        else:
             await msg.edit(f"❌ **Lỗi:** `{str(e)}`")
    
    finally:
        try:
            if os.path.exists(work_dir): shutil.rmtree(work_dir)
            if os.path.exists(final_zip_file): os.remove(final_zip_file)
            if os.path.exists(downloaded_path): os.remove(downloaded_path)
        except: pass

@bot.on(events.NewMessage)
async def handler(event):
    if event.file and event.file.name.endswith('.session'):
        temp_path = f"sessions/{event.file.name}"
        msg_wait = await event.reply("⬇️ **Đang tải...**")
        try:
            await bot.download_media(event.message, temp_path)
            await msg_wait.delete()
            await convert_process(event, temp_path)
        except Exception as e:
            print(e)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(f"🛠 **Bot Convert TData V5**\n✅ Auto Set 2FA: `{DEFAULT_2FA_PASS}`\n✅ Auto Create Note .txt")

if __name__ == '__main__':
    keep_alive()
    print("--- BOT STARTED ---")
    bot.start(bot_token=bot_token)
    bot.run_until_disconnected()
