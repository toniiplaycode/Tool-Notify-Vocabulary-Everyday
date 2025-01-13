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

def show_notification(title, message, current_num, total):
    """Hiển thị thông báo với số thứ tự từ và tổng số từ"""
    toast = Notification(
        app_id="Vocabulary Everyday",
        title=title,
        msg=f"{message}\n{current_num}/{total}",  # Thêm số thứ tự/tổng số từ
        duration="long",
        icon=resource_path("icon.ico")
    )
    toast.show()

def load_settings():
    try:
        # Thử đọc từ thư mục hiện tại trước
        if os.path.exists('settings.json'):
            with open('settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if 'interval' in settings:
                    return settings
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
    return {"interval": 180}  # Default value

def create_tray_icon():
    image = Image.open(resource_path("icon.ico"))
    
    def on_quit(icon):
        icon.stop()
        os._exit(0)
    
    def open_settings(icon):
        os.system('settings.exe')
        
    def open_format_cookies(icon):
        os.system('formatCookies.exe')
        
    def open_get_vocabulary(icon):
        os.system('getVocabulary.exe')
    
    # Tạo menu cho icon với thêm các tùy chọn mới
    menu = pystray.Menu(
        pystray.MenuItem("Get Vocabulary", open_get_vocabulary),
        pystray.MenuItem("Format Cookies", open_format_cookies),
        pystray.MenuItem("Settings", open_settings),
        pystray.MenuItem("Quit", on_quit),
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

def save_current_index(index, total_words):
    """Lưu vị trí từ vựng hiện tại và tổng số từ"""
    try:
        data = {
            'current_index': index,
            'total_words': total_words,
            'last_updated': time.time()
        }
        with open('vocabulary_state.json', 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving state: {str(e)}")

def load_current_index(total_words):
    """Đọc vị trí từ vựng đã lưu"""
    try:
        if os.path.exists('vocabulary_state.json'):
            with open('vocabulary_state.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Chỉ reset về 0 khi số từ vựng thay đổi
                if data['total_words'] != total_words:
                    print(f"Total words changed from {data['total_words']} to {total_words}, resetting index")
                    return 0
                # Nếu index vượt quá số từ hiện tại, reset về 0
                if data['current_index'] >= total_words:
                    return 0
                return data['current_index']
    except Exception as e:
        print(f"Error loading state: {str(e)}")
    return 0

try:
    # Đọc danh sách từ vựng từ file
    with open(resource_path("saved_words.txt"), "r", encoding="utf-8") as f:
        all_words = [line.strip() for line in f.readlines()]
        total_words = len(all_words)
        print(f"Loaded {total_words} words from saved_words.txt")

    if not all_words:
        print("Error: saved_words.txt is empty")
        exit()

    # Đọc vị trí từ vựng đã lưu
    current_word_index = load_current_index(total_words)
    print(f"Starting from word index: {current_word_index}")
    
    # Vòng lặp vô hạn để xoay vòng các từ
    while True:
        settings = load_settings()
        interval = settings.get('interval', 180)
        
        # Kiểm tra và đảm bảo index hợp lệ
        if current_word_index >= total_words:
            current_word_index = 0
            print("Reached end of word list, starting over")
            
        # Lấy từ hiện tại và hiển thị ngay lập tức
        line = all_words[current_word_index]
        try:
            english_word = line.split('-')[0].strip()
            meaning = line.split('-')[1].strip() if '-' in line else ''
            
            print(f"Showing word {current_word_index + 1}/{total_words}: {english_word}")
            
            show_notification(english_word, meaning, current_word_index + 1, total_words)
            text_to_speech(english_word)
            playsound(custom_sound)
            
            # Đợi interval trước khi hiển thị từ tiếp theo
            time.sleep(interval)
            
            # Tăng chỉ số từ sau khi đã đợi
            current_word_index = (current_word_index + 1)
            save_current_index(current_word_index, total_words)
            
        except Exception as e:
            print(f"Error displaying word '{line}': {str(e)}")
            current_word_index = (current_word_index + 1)
            save_current_index(current_word_index, total_words)
            continue

except FileNotFoundError:
    print("Error: saved_words.txt not found")
except Exception as e:
    print(f"Unknown error: {str(e)}")
