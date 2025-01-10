import tkinter as tk
from tkinter import scrolledtext
import datetime
import pickle

def format_cookies(raw_data):
    formatted_cookies = []
    
    for line in raw_data.split('\n'):
        parts = line.split('\t')
        
        if len(parts) >= 6:
            cookie = {
                'name': parts[0],
                'value': parts[1],
                'domain': parts[2],
                'path': parts[3],
                'expiry': datetime.datetime.strptime(parts[4], "%Y-%m-%dT%H:%M:%S.%fZ") if parts[4] != "Session" else None,
                'secure': parts[5] == "✓",
                'http_only': parts[6] == "✓" if len(parts) > 6 else False,
                'same_site': parts[7] if len(parts) > 7 else None,
                'priority': parts[8] if len(parts) > 8 else None
            }
            formatted_cookies.append(cookie)
    
    return formatted_cookies

def save_cookies():
    raw_data = text_area.get("1.0", tk.END).strip()  # Lấy dữ liệu raw_data từ text_area
    formatted_cookies = format_cookies(raw_data)
    
    with open("cookies.pkl", "wb") as file:
        pickle.dump(formatted_cookies, file)
    
    result_label.config(text="Đã lưu cookies vào file cookies.pkl")
    
    # Tự động tắt cửa sổ sau khi lưu cookies
    root.quit()  # Dừng vòng lặp của tkinter và đóng cửa sổ

# Tạo cửa sổ giao diện người dùng
root = tk.Tk()
root.title("Nhập Dữ Liệu Raw")

# Thêm một vùng nhập liệu (text area) cho raw_data
text_area = scrolledtext.ScrolledText(root, width=80, height=20)
text_area.pack(pady=10)

# Thêm nút lưu dữ liệu vào tệp
save_button = tk.Button(root, text="Lưu Cookies", command=save_cookies)
save_button.pack(pady=10)

# Thêm label để hiển thị thông báo
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

# Chạy giao diện người dùng
root.mainloop()
