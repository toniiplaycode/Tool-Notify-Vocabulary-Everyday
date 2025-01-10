import datetime
import pickle

def format_cookies(raw_data):
    formatted_cookies = []
    
    # Duyệt qua từng dòng dữ liệu
    for line in raw_data.split('\n'):
        parts = line.split('\t')
        
        # Kiểm tra nếu dòng có đủ 6 phần (name, value, domain, path, expiry, và security info)
        if len(parts) >= 6:
            cookie = {
                'name': parts[0],
                'value': parts[1],
                'domain': parts[2],
                'path': parts[3],
                # Sử dụng regex để xử lý fractional seconds
                'expiry': datetime.datetime.strptime(parts[4], "%Y-%m-%dT%H:%M:%S.%fZ") if parts[4] != "Session" else None,
                'secure': parts[5] == "✓",
                'http_only': parts[6] == "✓" if len(parts) > 6 else False,
                'same_site': parts[7] if len(parts) > 7 else None,
                'priority': parts[8] if len(parts) > 8 else None
            }
            formatted_cookies.append(cookie)
    
    return formatted_cookies


# Dữ liệu raw_data ví dụ (nên thay thế bằng dữ liệu thực tế của bạn)
raw_data = """AEC	AZ6Zc-XZXb557axhajboh--GcL1EtmQ9805owoQ1diyH9qUbOjaa1mwZWms	.google.com	/	2025-02-01T01:34:30.062Z	62	✓	✓	Lax			Medium	
APISID	70df0rA9UtP0H6GD/AyP7FYRbgcVur3emZ	.google.com	/	2026-02-09T02:39:32.208Z	40						High	
HSID	At82wVyAWLdDHUBZc	.google.com	/	2026-02-09T02:39:32.208Z	21	✓					High	
NID	520=fwkhpllP7tBphWwAPYgjXY6rPR5uohq2B5ieNJGXQEXqZgpoMT5dGH-zf3skBoXLgZy-ec6EF1IYct4TccnOe-3RQLmqzgTu5Ga04sRjecN_BlivxmQL7Bt9LCbqlGGIr7upE_WP_SwQuEDMvBtHSORIhqfPGDx9mNUzAU4WV1rS7QPu8IFp9l1ZfDOCwFAhTIDVt9knR1npS_7ODknaBoer_23bf_e80bOjw0i5OPXo43Pno3Ug-2WpSHwedT5hHd6UFSJNJqac1KNFqSY8A3DaMCiGHpNj6R-noH2hK9cVAtBY7B88oCLUiSk8iz7px2LINJEai0RQIiEeuT3cc2RUXykbsTo1bvuHuc1OjIm3UWg36Z4z82hGqtwJgO2xug1pzsBcuJKmD53x5CMnOHOypRnWbB-ZAp6nKPtUHLKsLWZ8wtawrMCbSf4rgW0jJ_sor5Mkgxza9rQcniOV15RRAYpVS2VHjmH0hl9sXnDDT4Jj9eusN7Mq7Bk5w19R-KZ3izFAItPnaVg1fBUTwbdA5rJXIPlw6yrai6QqfzS8WKt130VnRmOeMkVsELiPWvAm0_PQtoxWzlJd3EocXp80xI74TJzEbL1axOW-VThc7-rHuM7bKJvhXgjC2dpnamkvRs9LFzp3Rm6CVL1vGh9HaUtzO5BHxIoNBUxFAxiapGYr6V_UXGKkWUS2sewbKCc3HDnLJ-eHVXJY48-JNyY8vIG56F774LdwfTmm_BO8Mc3inyKl9sZOikGxNe-nJgzXCwtIy0-fmpQW_z5bkDHi3icKzIXxxFBSkv163el9XulAn_0MPXMQWZRnWzJAWf9nmtDQ2ArPcCJxPYBcbIWINmJi48_hsjkoBCgmdbbKiBkggVdFJMu7qJZwHxOmpRI	.google.com	/	2025-07-12T02:36:13.969Z	906	✓	✓	None			Medium	
OGPC	19041976-1:	.google.com	/	2025-01-21T08:25:49.000Z	15						Medium	
OSID	g.a000oQg2uvHUdL765u8PWU8PszqbTTbidAKdxpIdVLCJ0vHMYjp3jQt2zJPgvdWjn4D-A5b28gACgYKAZYSARUSFQHGX2Mi5F3qT_HREhD06lGpDYMVwRoVAUF8yKoHBjMLwlLI4vcsKK2VnTTR0076	play.google.com	/	2025-10-26T03:55:29.818Z	157	✓	✓				Medium	
OTZ	7902858_28_28__28_	translate.google.com	/	2025-02-09T02:18:27.000Z	21		✓				Medium	
PLAY_ACTIVE_ACCOUNT	ICrt_XL61NBE_S0rhk8RpG0k65e0XwQVdDlvB6kxiQ8=authuser-0	.play.google.com	/	Session	73		✓				Medium	
S	billing-ui-v3=o3neHxuzj2naelMpVW0X6N7mK7cDUHbl:billing-ui-v3-efe=o3neHxuzj2naelMpVW0X6N7mK7cDUHbl	.google.com	/	Session	98	✓					Low	
SAPISID	cotps0m6Jz9E_dd0/A05aU5Cvhr7zUPU4-	.google.com	/	2026-02-09T02:39:32.208Z	41		✓				High	
SEARCH_SAMESITE	CgQI_JwB	.google.com	/	2025-07-03T08:58:21.561Z	23			Strict			Medium	
SID	g.a000sAg2ughIHJJQGSWOzpTLzAMrBCIn83hu35hw_t5XWZWKSExcqLUwAZxvykiEI1QU_5jQ7wACgYKAfsSARUSFQHGX2MikNL5uEJD5NK0_msKz2GZ1xoVAUF8yKrlR-BFyyucNUDtVKuKRsGD0076	.google.com	/	2026-02-09T02:39:32.209Z	156						High	
SIDCC	AKEyXzUxmfd5rl7JXj8Hi6ug06ejZ_UBscj_v326tX73qd7Tcy2tH2piwp0GoP-rUDhJlSgjuRo	.google.com	/	2026-01-10T02:46:42.221Z	80						High	
SSID	AyOK6DEQ5S-Whhikf	.google.com	/	2026-02-09T02:39:32.208Z	21	✓	✓				High	
__Secure-1PAPISID	cotps0m6Jz9E_dd0/A05aU5Cvhr7zUPU4-	.google.com	/	2026-02-09T02:39:32.208Z	51		✓				High	
__Secure-1PSID	g.a000sAg2ughIHJJQGSWOzpTLzAMrBCIn83hu35hw_t5XWZWKSExcLWIMZDYUtsYIglg64JVAwQACgYKAeYSARUSFQHGX2MiDVm7e1P8d8jZNQIqi95fHRoVAUF8yKpjU1vpecFT7-sm0Y7ihfw_0076	.google.com	/	2026-02-09T02:39:32.209Z	167	✓	✓				High	
__Secure-1PSIDCC	AKEyXzWptZIn4cefw9UlzRi9vnYeaL55-ULeaD0hxKVOBwVjYJ8kNkI2wsAK9FM4_vMFpUmGsSk	.google.com	/	2026-01-10T02:46:42.221Z	91	✓	✓				High	
__Secure-1PSIDTS	sidts-CjEBmiPuTVARu0uNbCBKhyVAr2R5_Zd2--w-sv4wDxE_fXrqxUMioj1C_HOtKk9I2iN9EAA	.google.com	/	2026-01-10T02:38:33.043Z	93	✓	✓				High	
__Secure-3PAPISID	cotps0m6Jz9E_dd0/A05aU5Cvhr7zUPU4-	.google.com	/	2026-02-09T02:39:32.209Z	51		✓	None			High	
__Secure-3PSID	g.a000sAg2ughIHJJQGSWOzpTLzAMrBCIn83hu35hw_t5XWZWKSExc51uLhiinvKHJZGKamMRy0wACgYKAVMSARUSFQHGX2Mi0cNT9QPcUION2MH4SabTcRoVAUF8yKoHtGcdbC0dcoI6ilVW6naI0076	.google.com	/	2026-02-09T02:39:32.209Z	167	✓	✓	None			High	
__Secure-3PSIDCC	AKEyXzWw64Dz0obk1WJzhXXBcjzdTf013eZYMdtGMmkttwFxVN1Dbfkwf1o_ia1zm01bYbkeQxM	.google.com	/	2026-01-10T02:46:42.221Z	91	✓	✓	None			High	
__Secure-3PSIDTS	sidts-CjEBmiPuTVARu0uNbCBKhyVAr2R5_Zd2--w-sv4wDxE_fXrqxUMioj1C_HOtKk9I2iN9EAA	.google.com	/	2026-01-10T02:38:33.043Z	93	✓	✓	None			High	
__Secure-OSID	g.a000oQg2uvHUdL765u8PWU8PszqbTTbidAKdxpIdVLCJ0vHMYjp3DobM903XFyUMYV0RzUFUeAACgYKAeoSARUSFQHGX2MilKADBdFLusPbb88laQDuQxoVAUF8yKoOcgWGPHEsFIFToKbri75P0076	play.google.com	/	2025-10-26T03:55:29.818Z	166	✓	✓	None			Medium"""  # Thay thế với dữ liệu của bạn

formatted_cookies = format_cookies(raw_data)

# Lưu kết quả vào tệp cookies.pkl
with open("cookies.pkl", "wb") as file:
    pickle.dump(formatted_cookies, file)

print("Đã lưu cookies vào file cookies.pkl")
