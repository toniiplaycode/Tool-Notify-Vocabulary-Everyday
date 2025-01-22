from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pickle
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Xử lý encoding an toàn hơn
try:
    if sys.stdout and sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

class VocabularySelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vocabulary Settings")
        self.root.geometry("300x150")
        self.root.resizable(False, False)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Label
        ttk.Label(main_frame, text="Số lượng từ vựng:").grid(row=0, column=0, pady=10)
        
        # Combobox
        self.word_count = ttk.Combobox(main_frame, values=[10, 20, 30, 50, 100, 150, 200, 250, 300], width=10)
        self.word_count.set(30)  # Giá trị mặc định
        self.word_count.grid(row=0, column=1, padx=10)
        
        # Start button
        ttk.Button(main_frame, text="Bắt đầu", command=self.start).grid(row=1, column=0, columnspan=2, pady=20)
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.selected_count = None

    def start(self):
        try:
            self.selected_count = int(self.word_count.get())
            self.root.destroy()
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng chọn số lượng từ vựng")

    def run(self):
        self.root.mainloop()
        return self.selected_count

def get_vocabulary(word_count):
    # Khởi chạy Chrome WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # Truy cập Google Dịch
        driver.get("https://translate.google.com/")
        time.sleep(2)

        # Load cookies
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            if cookie['domain'] == ".google.com":
                driver.add_cookie(cookie)

        # Làm mới trang
        driver.refresh()
        time.sleep(3)

        # Kiểm tra đăng nhập
        try:
            # Đợi thêm thời gian để trang load hoàn toàn
            time.sleep(2)
            
            # Thử tìm nút "Đã lưu" - nút này chỉ xuất hiện khi đã đăng nhập
            saved_button = driver.find_element(By.XPATH, '//div[text()="Đã lưu"]')
            print("Đăng nhập thành công!")
        except:
            print("Đăng nhập không thành công!")
            driver.quit()
            return

        # Nhấn vào nút "Đã lưu"
        saved_button = driver.find_element(By.XPATH, '//div[text()="Đã lưu"]')
        saved_button.click()
        time.sleep(2)

        # Lưu từ vựng
        saved_words = []
        page_count = 0
        while len(saved_words) < word_count:
            saved_tab = driver.find_elements(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[3]/c-wiz/div[2]/ol/li')
            
            for li in saved_tab:
                if len(saved_words) < word_count:
                    word = li.find_element(By.XPATH, './/span[@jsname="diQUje"]')
                    meaning = li.find_element(By.XPATH, './/span[@jsname="WHdkge"]')
                    saved_words.append(f"{word.text} - {meaning.text}")
            
            if len(saved_words) < word_count:
                next_button = driver.find_element(By.XPATH, '//button[@aria-label="10 bản dịch đã lưu tiếp theo"]')
                next_button.click()
                time.sleep(1)

            page_count += 1
            if page_count > (word_count // 10) + 1:
                break

        # Lưu vào file
        with open("saved_words.txt", "w", encoding="utf-8") as f:
            for word in saved_words:
                f.write(word + "\n")

        print(f"Đã lưu {len(saved_words)} từ vựng vào file saved_words.txt")

        # Sau khi lưu từ vựng mới vào saved_words.txt
        
        # Xóa file vocabulary_state.json để reset vị trí từ
        if os.path.exists('vocabulary_state.json'):
            os.remove('vocabulary_state.json')
            print("Đã xóa file vocabulary_state.json để reset vị trí từ")
            
        # Xóa file vocabulary_state.json trong thư mục dist nếu có
        dist_state_file = os.path.join('dist', 'vocabulary_state.json')
        if os.path.exists(dist_state_file):
            os.remove(dist_state_file)
            print("Đã xóa file vocabulary_state.json trong thư mục dist")
            
        print("Đã cập nhật từ vựng mới thành công!")
        messagebox.showinfo("Thành công", "Đã cập nhật từ vựng mới và reset vị trí từ!")

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        messagebox.showerror("Lỗi", f"Không thể lấy từ vựng: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Hiện giao diện chọn số lượng từ
    selector = VocabularySelector()
    word_count = selector.run()
    
    if word_count:
        # Thực hiện lấy từ vựng với số lượng đã chọn
        get_vocabulary(word_count)
