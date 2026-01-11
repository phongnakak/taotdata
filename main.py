import os
import threading
from flask import Flask
import time
import asyncio
import logging
import shutil
import socks
import sys
import random
import urllib.request # Dung de tai anh avatar

# Import Telethon
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

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

DEFAULT_2FA_PASS = "12341234" 

# --- DATA RANDOM ---
HO_VN = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
TEN_DEM = ["Thị", "Thu", "Mỹ", "Ngọc", "Thanh", "Thảo", "Phương", "Hồng", "Khánh", "Minh", "Bảo"]
TEN_GAI = ["Linh", "Hương", "Trang", "Mai", "Vy", "Hân", "Lan", "Nhi", "Huyền", "Tú", "Thư", "Ly", "Quỳnh", "Yến", "Nga", "Ngân", "Hà", "Châu"]

# Danh sach link anh Gai Xinh (Anh AI hoac Stock de tranh ban quyen)
LIST_AVATAR_URLS = [
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400",
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400",
    "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400",
    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400",
    "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=400",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400",
    "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=400",
    "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=400",
    "https://images.unsplash.com/photo-1514315384763-ba401779410f?w=400"
]

# ==========================================
# 2. WEB SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Convert V6 (Auto Name + Avatar)"

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
# 4. HAM CONVERT + CHANGE INFO
# ==========================================
MY_API_ID = 36305655
MY_API_HASH = '58c19740ea1f5941e5847c0b3944f41d'

async def convert_process(event, downloaded_path):
    msg = await event.reply("⏳ **Đang xử lý (Đổi tên & Avatar)...**")
    
    filename_w_ext = os.path.basename(downloaded_path) 
    session_name = filename_w_ext.replace('.session', '') 
    
    timestamp = int(time.time())
    work_dir = f"temp_process/work_{session_name}_{timestamp}"
    os.makedirs(work_dir, exist_ok=True)
    
    container_folder = os.path.join(work_dir, session_name)
    os.makedirs(container_folder, exist_ok=True)

    shutil.copy2(downloaded_path, os.path.join(container_folder, filename_w_ext))
    
    tdata_folder_path = os.path.join(container_folder, "tdata")
    path_to_load = os.path.join(container_folder, session_name)
    txt_pass_path = os.path.join(container_folder, "pass_2fa.txt")

    client_convert = None
    log_info = []
    
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

        # --- 1. SET 2FA ---
        try:
            await client_convert.edit_2fa(new_password=DEFAULT_2FA_PASS)
            log_info.append(f"🔐 2FA: {DEFAULT_2FA_PASS}")
        except:
            log_info.append("🔐 2FA: Đã có sẵn")
        
        # --- 2. DOI TEN RANDOM ---
        try:
            new_ho = random.choice(HO_VN)
            new_ten = random.choice(TEN_DEM) + " " + random.choice(TEN_GAI)
            await client_convert(UpdateProfileRequest(first_name=new_ten, last_name=new_ho))
            log_info.append(f"👤 Tên: {new_ho} {new_ten}")
        except Exception as e:
            log_info.append(f"⚠️ Lỗi tên: {str(e)}")

        # --- 3. DOI AVATAR RANDOM ---
        temp_avatar_path = f"temp_process/avatar_{timestamp}.jpg"
        try:
            # Tai anh tu URL ve
            url_anh = random.choice(LIST_AVATAR_URLS)
            urllib.request.urlretrieve(url_anh, temp_avatar_path)
            
            # Upload anh len Tele
            upload_file = await client_convert.upload_file(temp_avatar_path)
            await client_convert(UploadProfilePhotoRequest(file=upload_file))
            log_info.append("🖼️ Avatar: Đã đổi")
        except Exception as e:
            log_info.append(f"⚠️ Lỗi ảnh: {str(e)}")

        # --- GHI FILE TXT ---
        with open(txt_pass_path, "w", encoding="utf-8") as f:
            f.write(f"Account: {session_name}\n")
            f.write("\n".join(log_info))
            
        # --- CONVERT ---
        tdesk = await client_convert.ToTDesktop(flag=UseCurrentSession)
        tdesk.SaveTData(tdata_folder_path)
        await client_convert.disconnect()
        
        await msg.edit("📦 **Đang đóng gói...**")
        
        # --- NEN ZIP ---
        zip_output_path = f"temp_process/{session_name}"
        shutil.make_archive(zip_output_path, 'zip', root_dir=work_dir)
        final_zip_file = zip_output_path + ".zip"
        
        await msg.edit("⬆️ **Đang tải lên...**")
        
        caption_text = f"✅ **Xong!**\n📂 Folder: `{session_name}`\n" + "\n".join(log_info)
        
        await bot.send_file(
            event.chat_id,
            final_zip_file,
            caption=caption_text,
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
            # Xoa anh avatar tam
            if 'temp_avatar_path' in locals() and os.path.exists(temp_avatar_path): 
                os.remove(temp_avatar_path)
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
    await event.respond(f"🛠 **Bot Full Option V6**\n✅ Auto 2FA\n✅ Auto Name (Gái VN)\n✅ Auto Avatar")

if __name__ == '__main__':
    keep_alive()
    print("--- BOT STARTED ---")
    bot.start(bot_token=bot_token)
    bot.run_until_disconnected()
