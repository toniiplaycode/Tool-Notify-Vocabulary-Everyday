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
import json
import winreg
import win32com.client
import win32event
import win32api
import winerror
from pathlib import Path

# Sửa cách lấy đường dẫn để tương thích với PyInstaller
def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối cho resource files"""
    try:
        # PyInstaller tạo một thư mục temp _MEIPASS
        base_path = sys._MEIPASS
        # Với saved_words.txt, luôn đọc từ thư mục hiện tại
        if relative_path == "saved_words.txt":
            current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            return os.path.join(current_dir, relative_path)
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
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_filename = fp.name
        tts = gTTS(text=text, lang=lang)
        tts.save(temp_filename)
        playsound(temp_filename)
        os.unlink(temp_filename)
    except Exception as e:
        print(f"Lỗi khi đọc từ '{text}': {str(e)}")

def show_notification(title, message, current_num, total):
    """Hiển thị thông báo với số thứ tự từ và tổng số từ"""
    toast = Notification(
        app_id="Vocabulary Everyday",
        title=title,
        msg=f"{message}\n{current_num}/{total}",
        duration="long",
        icon=resource_path("icon.ico")
    )
    toast.show()

def load_settings():
    try:
        if os.path.exists('settings.json'):
            with open('settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if 'interval' in settings:
                    return settings
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
    return {"interval": 180}

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
    return icon

def add_to_startup():
    try:
        exe_path = os.path.abspath(sys.argv[0])
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shortcut_path = os.path.join(startup_folder, 'VocabularyEveryday.lnk')
        
        if not os.path.exists(shortcut_path):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.IconLocation = exe_path
            shortcut.save()
    except Exception as e:
        print(f"Lỗi khi thêm vào startup: {str(e)}")

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
                if data['total_words'] != total_words:
                    print(f"Total words changed from {data['total_words']} to {total_words}, resetting index")
                    return 0
                if data['current_index'] >= total_words:
                    return 0
                return data['current_index']
    except Exception as e:
        print(f"Error loading state: {str(e)}")
    return 0

def check_single_instance():
    """Đảm bảo chỉ có một instance của chương trình chạy"""
    try:
        mutex_name = "Global\\VocabularyEverydayNotifierMutex_v1"
        global mutex
        mutex = win32event.CreateMutex(None, 1, mutex_name)
        last_error = win32api.GetLastError()
        
        print(f"Checking single instance - Last Error: {last_error}")
        
        if last_error == winerror.ERROR_ALREADY_EXISTS:
            print("Another instance is already running! Exiting...")
            win32api.CloseHandle(mutex)
            return False
            
        print("No other instance found, continuing...")
        return True
        
    except Exception as e:
        print(f"Error in check_single_instance: {str(e)}")
        return False

def main():
    try:
        print("Starting application...")
        print("This console will close in 10 seconds if no errors occur")
        
        if not check_single_instance():
            print("Exiting due to another instance running")
            time.sleep(10)  # Đợi 10 giây trước khi thoát
            sys.exit(0)
            
        print("Starting main program...")
        
        # Thêm vào startup khi khởi động
        add_to_startup()
        
        # Tạo và chạy icon trong thread riêng
        icon = create_tray_icon()
        icon_thread = threading.Thread(target=icon.run, daemon=True)
        icon_thread.start()
        
        print("System tray icon created...")
        time.sleep(3)
        
        print("Loading vocabulary file...")
        with open(resource_path("saved_words.txt"), "r", encoding="utf-8") as f:
            all_words = [line.strip() for line in f.readlines()]
            total_words = len(all_words)
            print(f"Loaded {total_words} words from saved_words.txt")

        if not all_words:
            print("Error: saved_words.txt is empty")
            time.sleep(10)
            exit()

        current_word_index = load_current_index(total_words)
        print(f"Starting from word index: {current_word_index}")
        
        settings = load_settings()
        interval = settings.get('interval', 180)
        print(f"Initial interval: {interval} seconds")
        
        # Nếu không có lỗi, đóng console sau 10 giây
        time.sleep(10)
        
        # Vòng lặp chính
        while True:
            try:
                if current_word_index >= total_words:
                    current_word_index = 0
                    print("Reached end of word list, starting over")
                
                line = all_words[current_word_index]
                english_word = line.split('-')[0].strip()
                meaning = line.split('-')[1].strip() if '-' in line else ''
                
                print(f"Showing word {current_word_index + 1}/{total_words}: {english_word}")
                
                show_notification(english_word, meaning, current_word_index + 1, total_words)
                text_to_speech(english_word)
                playsound(custom_sound)
                
                current_word_index = (current_word_index + 1)
                save_current_index(current_word_index, total_words)
                
                settings = load_settings()
                interval = settings.get('interval', 180)
                print(f"Waiting for {interval} seconds before next word...")
                
                # Thay thế vòng lặp for bằng time.sleep() đơn giản
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                time.sleep(10)
                continue

    except Exception as e:
        print(f"Critical error: {str(e)}")
        time.sleep(10)  # Đợi 10 giây khi có lỗi nghiêm trọng
    finally:
        try:
            if 'mutex' in globals():
                win32api.CloseHandle(mutex)
                print("Mutex released")
        except Exception as e:
            print(f"Error releasing mutex: {str(e)}")
            time.sleep(10)

if __name__ == "__main__":
    main()
