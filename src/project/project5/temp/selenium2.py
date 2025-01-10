from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import random
import csv


def change_agents():
    user_agents_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        # 추가 User-Agent 문자열
    ]

    headers = {"User-Agent": random.choice(user_agents_list)}
    response = requests.get(url, headers=headers, verify=False)

def change_proxy():
    proxies_list = [
    {"http": "http://ip:port", "https": "https://ip:port"},
    # 추가 프록시
]

    proxies = random.choice(proxies_list)
    response = requests.get(url, proxies=proxies, verify=False)




# 셀레니움 설정
def init_driver():
    chrome_options = Options()
    # User-Agent 설정
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.1 Safari/537.36")
    # 헤드리스 모드 비활성화 (헤드리스 모드는 차단 가능성 높음)
    chrome_options.add_argument("--headless")  # 필요한 경우 헤드리스 모드 활성화
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver_service = Service("chromedriver")  # 크롬 드라이버 경로 설정
    return webdriver.Chrome(service=driver_service, options=chrome_options)

# 검색 키워드 입력
keyword = input("검색할 제품 입력 : ")

# 데이터 저장용 리스트
link_list = []

# 드라이버 초기화
driver = init_driver()

# CSV 파일 생성
with open(f"coupang_{keyword}.csv", "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["제품명", "가격", "링크"])

    # 페이지 반복
    for page_num in range(1, 3):
        print(f"<<<<<{page_num}페이지>>>>>")
        
        # URL 설정
        url = f"https://www.coupang.com/np/search?q={keyword}&page={page_num}&listSize=36"
        driver.get(url)
        
        # 랜덤 대기 시간
        time.sleep(random.uniform(3, 5))
        
        # 페이지 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("[class=search-product]")
        print(f"아이템 수: {len(items)}")
        
        for item in items:
            name = item.select_one(".name").text.strip()
            price = item.select_one(".price-value")
            if not price:
                continue
            else:
                price = price.text.strip()
            link = f"https://coupang.com{item.a['href']}"
            
            link_list.append(link)
            writer.writerow([name, price, link])
            print(f"{name}: {price}")
            print(link)
        
        # 페이지 간 대기 시간
        time.sleep(random.uniform(5, 10))

print(link_list)
print(len(link_list))

# 드라이버 종료
driver.quit()