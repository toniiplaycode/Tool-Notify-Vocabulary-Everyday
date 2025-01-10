from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # Import webdriver-manager
import time
import pickle

# Khởi chạy Chrome WebDriver sử dụng webdriver-manager để tự động tải và quản lý chromedriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))  # Không cần chỉ định đường dẫn tĩnh nữa

# Truy cập Google Dịch trước khi thêm cookie
driver.get("https://translate.google.com/")
time.sleep(2)  # Đợi trang tải

# Load cookies đã lưu vào Selenium
cookies = pickle.load(open("cookies.pkl", "rb"))  # Đọc cookies từ file
for cookie in cookies:
    # Đảm bảo cookie có domain đúng
    if 'expiry' in cookie:
        del cookie['expiry']  # Xóa expiry vì Selenium không cần
    if cookie['domain'] == ".google.com":  # Kiểm tra domain của cookie
        driver.add_cookie(cookie)

# Làm mới trang để áp dụng cookies
driver.refresh()
time.sleep(2)  # Đợi trang tải lại

# Kiểm tra xem đã đăng nhập thành công chưa (kiểm tra một phần tử đặc trưng chỉ xuất hiện khi đã đăng nhập)
try:
    # Ví dụ: Kiểm tra phần tử của người dùng đã đăng nhập (thay bằng một phần tử thực tế bạn muốn kiểm tra)
    user_element = driver.find_element(By.XPATH, '//div[@aria-label="Tài khoản của bạn"]')  # Thay thế bằng XPath đúng
    print("Đăng nhập thành công!")
except:
    print("Đăng nhập không thành công!")

# Nhấn vào nút "Đã lưu"
saved_button = driver.find_element(By.XPATH, '//div[text()="Đã lưu"]')  # XPath của nút "Đã lưu"
saved_button.click()
time.sleep(2)  # Đợi một chút để đảm bảo nút đã được nhấn

# Lưu từ vựng vào danh sách
saved_words = []
page_count = 0  # Đếm số trang đã duyệt
while len(saved_words) < 30:  # Lặp lại cho đến khi có ít nhất 30 từ vựng
    saved_tab = driver.find_elements(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[3]/c-wiz/div[2]/ol/li')  # Đảm bảo XPath chính xác
    
    for li in saved_tab:
        if len(saved_words) < 30:  # Nếu số lượng từ vựng chưa đủ 30
            word = li.find_element(By.XPATH, './/span[@jsname="diQUje"]')  # XPath đến phần tử chứa từ vựng
            meaning = li.find_element(By.XPATH, './/span[@jsname="WHdkge"]')  # XPath đến phần tử chứa nghĩa
            saved_words.append(f"{word.text} - {meaning.text}")
    
    # Nếu chưa có đủ 30 từ, nhấn nút chuyển trang
    if len(saved_words) < 30:
        next_button = driver.find_element(By.XPATH, '//button[@aria-label="10 bản dịch đã lưu tiếp theo"]')  # XPath nút chuyển trang
        next_button.click()
        time.sleep(1)  # Đợi trang mới tải

    page_count += 1
    if page_count > 3:  # Nếu lặp quá nhiều lần mà không có đủ từ vựng, dừng lại
        break

# In danh sách từ vựng
print(saved_words)

# Đóng trình duyệt
driver.quit()

# Lưu từ vựng vào file
with open("saved_words.txt", "w", encoding="utf-8") as f:
    for word in saved_words:
        f.write(word + "\n")

print("Từ vựng đã được lưu vào file saved_words.txt.")
