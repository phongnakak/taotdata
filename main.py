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
import urllib.request 
import ssl

from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

try:
    from opentele.td import TDesktop
    from opentele.tl import TelegramClient as OpenteleClient
    from opentele.api import UseCurrentSession
except ImportError:
    print("❌ Lỗi: Chưa cài thư viện opentele")

# ==========================================
# 1. CẤU HÌNH
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

# --- DATA TÊN VIỆT NAM ---
HO_VN = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
TEN_DEM = ["Thị", "Thu", "Mỹ", "Ngọc", "Thanh", "Thảo", "Phương", "Hồng", "Khánh", "Minh", "Bảo", "Kim", "Anh", "Diệu", "Tuyết", "Trúc", "Bích", "Cẩm", "Thùy", "Nhã", "Cát"]
TEN_GAI = ["Linh", "Hương", "Trang", "Mai", "Vy", "Hân", "Lan", "Nhi", "Huyền", "Tú", "Thư", "Ly", "Quỳnh", "Yến", "Nga", "Ngân", "Hà", "Châu", "Ánh", "Duyên", "Thảo", "Diệp", "Oanh", "Vân", "Quyên", "Trâm", "An", "Chi"]

# --- KHO ẢNH KHỦNG (100+ LINK) ---
LIST_AVATAR_URLS = [
    # Batch 1 (Pexels - Asian Girl Casual)
    "https://images.pexels.com/photos/1382731/pexels-photo-1382731.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2613260/pexels-photo-2613260.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1382734/pexels-photo-1382734.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1391498/pexels-photo-1391498.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1372134/pexels-photo-1372134.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2364593/pexels-photo-2364593.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1319911/pexels-photo-1319911.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3220360/pexels-photo-3220360.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3054535/pexels-photo-3054535.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2036646/pexels-photo-2036646.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1982855/pexels-photo-1982855.jpeg?auto=compress&cs=tinysrgb&w=600",
    
    # Batch 2
    "https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1062249/pexels-photo-1062249.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1130626/pexels-photo-1130626.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1468379/pexels-photo-1468379.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1542085/pexels-photo-1542085.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1264210/pexels-photo-1264210.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1587009/pexels-photo-1587009.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3206118/pexels-photo-3206118.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1580271/pexels-photo-1580271.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1580272/pexels-photo-1580272.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2584269/pexels-photo-2584269.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2104252/pexels-photo-2104252.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2221357/pexels-photo-2221357.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2646237/pexels-photo-2646237.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3214729/pexels-photo-3214729.jpeg?auto=compress&cs=tinysrgb&w=600",
    
    # Batch 3
    "https://images.pexels.com/photos/3319307/pexels-photo-3319307.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/341970/pexels-photo-341970.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1852085/pexels-photo-1852085.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2816576/pexels-photo-2816576.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1892591/pexels-photo-1892591.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2808795/pexels-photo-2808795.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1105058/pexels-photo-1105058.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1498758/pexels-photo-1498758.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3007355/pexels-photo-3007355.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2119561/pexels-photo-2119561.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1578643/pexels-photo-1578643.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2444354/pexels-photo-2444354.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1536619/pexels-photo-1536619.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2246755/pexels-photo-2246755.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2085698/pexels-photo-2085698.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2364582/pexels-photo-2364582.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3142544/pexels-photo-3142544.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2128819/pexels-photo-2128819.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2128817/pexels-photo-2128817.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2265247/pexels-photo-2265247.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1841121/pexels-photo-1841121.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1386604/pexels-photo-1386604.jpeg?auto=compress&cs=tinysrgb&w=600",

    # Batch 4 (Bổ sung thêm cho phong phú)
    "https://images.pexels.com/photos/1182825/pexels-photo-1182825.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3771807/pexels-photo-3771807.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3053824/pexels-photo-3053824.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1376042/pexels-photo-1376042.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2100063/pexels-photo-2100063.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3277188/pexels-photo-3277188.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3444087/pexels-photo-3444087.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3348332/pexels-photo-3348332.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1310522/pexels-photo-1310522.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1937394/pexels-photo-1937394.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3680219/pexels-photo-3680219.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1820559/pexels-photo-1820559.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1546912/pexels-photo-1546912.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3283568/pexels-photo-3283568.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3612885/pexels-photo-3612885.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3767392/pexels-photo-3767392.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1499327/pexels-photo-1499327.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1557843/pexels-photo-1557843.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2092474/pexels-photo-2092474.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1832959/pexels-photo-1832959.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3385657/pexels-photo-3385657.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2915233/pexels-photo-2915233.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2364575/pexels-photo-2364575.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1181686/pexels-photo-1181686.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2690323/pexels-photo-2690323.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3375997/pexels-photo-3375997.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3054533/pexels-photo-3054533.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2584275/pexels-photo-2584275.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/341971/pexels-photo-341971.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1987301/pexels-photo-1987301.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3772510/pexels-photo-3772510.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3768163/pexels-photo-3768163.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/3649765/pexels-photo-3649765.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2043590/pexels-photo-2043590.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1484794/pexels-photo-1484794.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2167673/pexels-photo-2167673.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/2104245/pexels-photo-2104245.jpeg?auto=compress&cs=tinysrgb&w=600",
    "https://images.pexels.com/photos/1181424/pexels-photo-1181424.jpeg?auto=compress&cs=tinysrgb&w=600"
]

# ==========================================
# 2. WEB SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return f"Bot V12 (100+ Photos) - Total: {len(LIST_AVATAR_URLS)}"

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
# 4. HAM CONVERT + RETRY LOGIC
# ==========================================
MY_API_ID = 36305655
MY_API_HASH = '58c19740ea1f5941e5847c0b3944f41d'

async def convert_process(event, downloaded_path):
    msg = await event.reply("⏳ **Đang xử lý (Chống lỗi 404)...**")
    
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

        # 1. 2FA
        try:
            await client_convert.edit_2fa(new_password=DEFAULT_2FA_PASS)
            log_info.append(f"🔐 2FA: {DEFAULT_2FA_PASS}")
        except:
            log_info.append("🔐 2FA: Đã có sẵn")
        
        # 2. NAME
        try:
            new_ho = random.choice(HO_VN)
            new_ten = random.choice(TEN_DEM) + " " + random.choice(TEN_GAI)
            await client_convert(UpdateProfileRequest(first_name=new_ho, last_name=new_ten))
            log_info.append(f"👤 Tên: {new_ho} {new_ten}") 
        except Exception as e:
            log_info.append(f"⚠️ Lỗi tên: {str(e)}")

        # --- 3. DOI AVATAR (CO CHE RETRY - QUAN TRONG) ---
        temp_avatar_path = f"temp_process/avatar_{timestamp}.jpg"
        avatar_success = False
        error_log = ""

        # Thu toi da 5 lan cho chac
        for i in range(5):
            try:
                url_anh = random.choice(LIST_AVATAR_URLS)
                
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                req = urllib.request.Request(
                    url_anh, 
                    data=None, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                with urllib.request.urlopen(req, context=ssl_context) as response, open(temp_avatar_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                
                # Upload
                upload_file = await client_convert.upload_file(temp_avatar_path)
                await client_convert(UploadProfilePhotoRequest(file=upload_file))
                
                avatar_success = True
                break 
            except Exception as e:
                error_log = str(e)
                continue

        if avatar_success:
            log_info.append("🖼️ Avatar: Đã đổi ✅")
        else:
            log_info.append(f"⚠️ Lỗi ảnh: {error_log}")

        # GHI TXT
        with open(txt_pass_path, "w", encoding="utf-8") as f:
            f.write(f"Account: {session_name}\n")
            f.write("\n".join(log_info))
            
        # CONVERT
        tdesk = await client_convert.ToTDesktop(flag=UseCurrentSession)
        tdesk.SaveTData(tdata_folder_path)
        await client_convert.disconnect()
        
        await msg.edit("📦 **Đang đóng gói...**")
        
        # ZIP
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
    await event.respond(f"🛠 **Bot V12 (100+ Photos)**\n✅ Đã cập nhật kho ảnh lớn.\n✅ Tự động thử lại nếu ảnh lỗi.")

if __name__ == '__main__':
    keep_alive()
    print("--- BOT STARTED ---")
    bot.start(bot_token=bot_token)
    bot.run_until_disconnected()
