import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối cho resource files"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

def create_default_settings():
    """Tạo file settings.json với giá trị mặc định nếu chưa tồn tại"""
    if not os.path.exists('settings.json'):
        default_settings = {"interval": 180}
        with open('settings.json', 'w') as f:
            json.dump(default_settings, f)
        return default_settings
    return None

def load_settings():
    # Tạo settings mặc định nếu chưa có
    default_settings = create_default_settings()
    if default_settings:
        return default_settings
        
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            # Đảm bảo có key interval
            if 'interval' not in settings:
                settings['interval'] = 180
            return settings
    except:
        return {"interval": 180}

def save_settings(settings):
    try:
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu cài đặt: {str(e)}")

class SettingsWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vocabulary Settings")
        self.root.geometry("300x150")
        self.root.resizable(False, False)
        
        # Load settings
        self.settings = load_settings()
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Interval setting
        ttk.Label(main_frame, text="Interval between words (seconds):").grid(row=0, column=0, pady=10)
        self.interval_var = tk.StringVar(value=str(self.settings["interval"]))
        interval_entry = ttk.Entry(main_frame, textvariable=self.interval_var, width=10)
        interval_entry.grid(row=0, column=1, padx=10)
        
        # Save button
        ttk.Button(main_frame, text="Lưu", command=self.save).grid(row=1, column=0, columnspan=2, pady=20)
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def save(self):
        try:
            interval = int(self.interval_var.get())
            if interval < 1:
                raise ValueError("Thời gian phải lớn hơn 0")
            
            self.settings["interval"] = interval
            save_settings(self.settings)
            self.root.destroy()
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên dương")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SettingsWindow()
    app.run() 