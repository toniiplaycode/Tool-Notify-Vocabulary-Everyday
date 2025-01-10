import time
from winotify import Notification
from playsound import playsound
import os
from gtts import gTTS
import tempfile
from sys import exit
import sys
import pystray
from PIL import Image
import threading
import random
import json
import winreg
import win32com.client

# Sửa cách lấy đường dẫn để tương thích với PyInstaller
def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối cho resource files"""
    try:
        # PyInstaller tạo một thư mục temp _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    
    return os.path.join(base_path, relative_path)

# Sử dụng resource_path để lấy đường dẫn file âm thanh
custom_sound = resource_path("ting.wav")

# Kiểm tra file âm thanh có tồn tại không
if not os.path.exists(custom_sound):
    print(f"Lỗi: Không tìm thấy file âm thanh tại {custom_sound}")
    exit()

def text_to_speech(text, lang='en'):
    """Chuyển đổi văn bản thành giọng nói và phát"""
    try:
        # Tạo file tạm để lưu âm thanh
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_filename = fp.name
            
        # Tạo file âm thanh
        tts = gTTS(text=text, lang=lang)
        tts.save(temp_filename)
        
        # Phát âm thanh
        playsound(temp_filename)
        
        # Xóa file tạm sau khi phát
        os.unlink(temp_filename)
    except Exception as e:
        print(f"Lỗi khi đọc từ '{text}': {str(e)}")

def show_notification(title, message):
    toast = Notification(
        app_id="Vocabulary Everyday",
        title=title,
        msg=message,
        duration="long",
        icon=resource_path("icon.ico")
    )
    toast.show()

def load_settings():
    try:
        with open(resource_path('settings.json'), 'r') as f:
            return json.load(f)
    except:
        return {"interval": 180}  # Mặc định 180 giây

def create_tray_icon():
    image = Image.open(resource_path("icon.ico"))
    
    def on_quit(icon):
        icon.stop()
        os._exit(0)
    
    def open_settings(icon):
        os.system('settings.exe')
    
    # Tạo menu cho icon với thêm tùy chọn Settings
    menu = pystray.Menu(
        pystray.MenuItem("Settings", open_settings),
        pystray.MenuItem("Quit", on_quit)
    )
    
    icon = pystray.Icon(
        "Vocabulary",
        image,
        "Vocabulary Notifier",
        menu
    )
    
    icon.run()

# Chạy tray icon trong thread riêng
threading.Thread(target=create_tray_icon, daemon=True).start()

def add_to_startup():
    try:
        # Lấy đường dẫn đến file thực thi
        exe_path = os.path.abspath(sys.argv[0])
        
        # Tạo shortcut trong thư mục Startup
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_folder, 'VocabularyEveryday.lnk')
        
        # Tạo shortcut nếu chưa tồn tại
        if not os.path.exists(shortcut_path):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.IconLocation = exe_path
            shortcut.save()
    except Exception as e:
        print(f"Lỗi khi thêm vào startup: {str(e)}")

# Thêm vào startup khi khởi động
add_to_startup()

try:
    # Đọc danh sách từ vựng từ file
    with open(resource_path("saved_words.txt"), "r", encoding="utf-8") as f:
        all_words = [line.strip() for line in f.readlines()]

    if not all_words:
        print("Lỗi: File saved_words.txt trống")
        exit()

    # Vòng lặp vô hạn để xoay vòng các từ
    while True:
        # Tạo một bản sao của danh sách từ để random
        current_words = all_words.copy()
        
        # Tiếp tục cho đến khi hết từ trong chu kỳ hiện tại
        while current_words:
            # Chọn ngẫu nhiên một từ từ danh sách hiện tại
            line = random.choice(current_words)
            # Xóa từ đã chọn khỏi danh sách hiện tại
            current_words.remove(line)
            
            try:
                english_word = line.split('-')[0].strip()
                meaning = line.split('-')[1].strip() if '-' in line else ''
                
                show_notification(english_word, meaning)
                text_to_speech(english_word)
                playsound(custom_sound)
                settings = load_settings()
                time.sleep(settings["interval"])
            except Exception as e:
                print(f"Lỗi khi hiển thị từ '{line}': {str(e)}")
                continue

except FileNotFoundError:
    print("Lỗi: Không tìm thấy file saved_words.txt")
except Exception as e:
    print(f"Lỗi không xác định: {str(e)}")
