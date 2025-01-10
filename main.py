import time
from win10toast import ToastNotifier
from playsound import playsound

# Đường dẫn tới file âm thanh
custom_sound = "./ting.wav"

# Đọc danh sách từ vựng từ file
with open("saved_words.txt", "r", encoding="utf-8") as f:
    saved_words = [line.strip() for line in f.readlines()]

# Khởi tạo ToastNotifier
toaster = ToastNotifier()

# Hiển thị từ vựng với âm thanh tùy chỉnh
for word in saved_words:
    toaster.show_toast(
        "Học từ vựng",
        word,
        duration=10,
        threaded=True,
    )
    playsound(custom_sound)
    time.sleep(10)
