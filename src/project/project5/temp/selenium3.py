from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

def test(keyword="컴퓨터"):
    # 크롬 옵션 설정
    options = Options()

    # User-Agent 설정 (일반적인 크롬 브라우저의 User-Agent로 설정)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")

    # 헤드리스 모드 비활성화 (헤드리스 모드에서는 일부 사이트가 차단될 수 있음)
    options.headless = False

    # 크롬 드라이버 설정
    driver = webdriver.Chrome(options=options)
    
    # 검색 페이지 열기
    driver.get(f"https://www.coupang.com/np/search?q={keyword}")
    
    # 기다리는 시간을 늘려서 페이지 로딩을 보장
    driver.implicitly_wait(50)
    
    try:
        # 드롭다운을 보여주기 위해 마우스를 올리기
        search_sorting = driver.find_element(By.CLASS_NAME, "search-customized-selectbox")
        actions = ActionChains(driver)
        actions.move_to_element(search_sorting).perform()  # 마우스를 해당 요소로 이동

        # 드롭다운 메뉴의 '72개씩 보기' 라벨을 클릭
        wait = WebDriverWait(driver, 50)  # 대기 시간을 50초로 늘림
        label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@for='listSize-72']")))
        label.click()

        # 새 페이지가 로드될 때까지 기다리기
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-customized-selectbox")))  # 예시로 기존 페이지 요소 대기

        # 데이터 로딩 후 크롤링 시작
        results = driver.find_elements(By.CLASS_NAME, "descriptions-inner")
        for rank, r in enumerate(results, 1):
            if rank > 10:
                break
            try:
                name = r.find_element(By.CLASS_NAME, "name")
                price = r.find_element(By.CLASS_NAME, "price")
                print(f"{rank}위 {name.text} {price.text}")
            except Exception as e:
                print("skip", e)
    except Exception as e:
        print("Error occurred:", e)
    finally:
        driver.quit()

# 테스트 실행
test()
