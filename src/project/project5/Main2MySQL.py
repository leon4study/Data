from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from mysql1 import MySqlClient
from reviews import load_reviews
from items import load_items
import os, json, time
import pandas as pd
import random
from dotenv import load_dotenv
from bs4 import BeautifulSoup
load_dotenv()

# 아마존 크롤링 함수

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 3)


ID = os.environ.get('ID') 
PW = os.environ.get('PW')
DB_SERVER_HOST = os.environ.get("DB_SERVER_HOST")
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_DATABASE = os.environ.get("DB_DATABASE")
DB_PORT = os.environ.get("DB_PORT")


my_sql_client = MySqlClient(
            server_name=DB_SERVER_HOST,
            database_name=DB_DATABASE,
            username=DB_USERNAME,
            password=DB_PASSWORD,
            port=DB_PORT
        )


def amazon_login(id : str ,pw : str):
    try:
        # 'Sign in' 버튼에 마우스를 올려 드롭다운 메뉴를 표시
        account_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "nav-link-accountList"))
        )
        ActionChains(driver).move_to_element(account_element).perform()

        # 'Sign in' 버튼 클릭
        sign_in_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#nav-flyout-ya-signin a.nav-action-signin-button"))
        )
        sign_in_button.click()

        """
        # 확인: 현재 URL이 로그인 페이지인지 확인
        WebDriverWait(driver, 20).until(
            EC.url_contains("https://www.amazon.com/ap/signin")
        )
        print("로그인 페이지로 이동 완료.")
        """
        # 이메일 입력 필드 대기
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_input.send_keys(id + Keys.RETURN)
        print("email end")

        # QR 코드 팝업 확인 및 닫기 처리
        try:
            qr_popup_close_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close']"))  # 팝업 닫기 버튼의 Xpath
            )
            qr_popup_close_button.click()  # 팝업 닫기
        except Exception:
            print("QR 코드 팝업이 없습니다. 진행합니다.")
        
        #wait_time = random.uniform(0.5, 1)
        #time.sleep(wait_time)

        password_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_input.send_keys(pw + Keys.RETURN)

    except Exception as e:
        print(f"오류 발생: {e}")


def set_sort_by_most_recent_with_scroll(driver, wait):
    """
    스크롤을 내려 'Sort by' 드롭다운에서 'Most recent' 옵션을 선택하는 함수.
    
    Args:
        driver: Selenium WebDriver 객체.
        wait: WebDriverWait 객체.
    """
    try:
        # 'Sort by' 드롭다운 버튼 대기
        dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "sort-order-dropdown"))
        )
        
        # 드롭다운이 화면에 보이도록 스크롤
        driver.execute_script("arguments[0].scrollIntoView();", dropdown)
        
        # Select 객체를 사용해 드롭다운 조작
        select = Select(dropdown)
        
        # 'Most recent' 옵션 선택
        select.select_by_value("recent")

    except Exception as e:
        print(f"Error setting sort by with scroll: {e}")
    #finally  :
        #wait_time = random.uniform(0.1, 0.4)
        #time.sleep(wait_time)



def click_next_page(driver, wait):
    try:
        # Next page 버튼 기다리기
        next_page_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-pagination .a-last a"))
        )
        # 버튼 클릭
        next_page_button.click()
        print("Successfully clicked the Next Page button.")
    except Exception as e:
        print(f"Error clicking Next Page button: {e}")


def region_setting(driver, zip_code="30301"):
    """
    지역 설정을 수행하는 함수. zip code를 입력한 후 Apply 및 Done 버튼을 클릭합니다.
    
    Args:
        driver: Selenium WebDriver 객체.
        zip_code (str): 설정할 우편번호 (기본값: "30301").
    
    Returns:
        str: 작업 성공 메시지 또는 오류 메시지.
    """
    try:
        # 1. 'Deliver to' 버튼 클릭
        deliver_to_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a#nav-global-location-popover-link"))
        )
        deliver_to_button.click()

        # 2. 새로운 화면에서 Zip Code 입력 필드 찾기
        zip_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#GLUXZipUpdateInput"))
        )
        zip_input.clear()  # 기존 값을 지우고
        zip_input.send_keys(zip_code)  # 새 우편번호 입력
        time.sleep(0.04)
        # 3. 'Apply' 버튼 클릭
        apply_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.a-button-input[aria-labelledby='GLUXZipUpdate-announce']"))
        )
        apply_button.click()
        time.sleep(0.05)

        # 4. 'Done' 버튼 클릭
        done_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button#a-autoid-1-announce"))
        )

        done_button.click()
        time.sleep(0.1)
        try:
            # "Continue" 버튼 요소 찾기
            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "GLUXConfirmClose"))
            )
            continue_button.click()  # "Continue" 버튼 클릭
            print("팝업 확인 버튼 클릭 완료.")
        except Exception as e:
            print(f"확인 버튼 클릭 실패: {e}")



    except Exception as e:
        return f"오류 발생: {e}"





def crawl_amazon(keyword="skin+care"):
    try:
        # 아마존 검색 페이지 열기
        driver.get(f"https://www.amazon.com")
        driver.implicitly_wait(5)  # 페이지 로딩 대기
        wait_time = random.uniform(0.05, 0.1)
        time.sleep(wait_time)

        region_setting(driver,"30301")
        wait_time = random.uniform(0.05, 0.1)
        time.sleep(wait_time)
        
        search_box = driver.find_element(By.ID, 'twotabsearchtextbox')

        # 검색어 입력
        search_box.clear()  # 혹시 검색창에 이전 텍스트가 있다면 삭제
        search_box.send_keys(keyword)  # "skin care" 입력

        # 검색 실행 (Enter 키 사용 또는 검색 버튼 클릭)
        search_box.send_keys(Keys.RETURN)
        
        amazon_login(ID,PW)
        print()

        # 모든 리스트 아이템 가져오기
        items = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
        item_list = []
        # 각 아이템 클릭 및 상세 정보 크롤링
        for idx, item in enumerate(items):

            try:
                #wait_time = random.uniform(0.01, 0.05)
                #time.sleep(wait_time)

                # 새 탭에서 열기 위해 Shift + Click
                item_link = item.find_element(By.CSS_SELECTOR, 'a.a-link-normal')
                item_url = item_link.get_attribute("href")

                # 새 탭에서 상세 정보 열기
                driver.execute_script("window.open(arguments[0], '_blank');", item_url)
                driver.switch_to.window(driver.window_handles[-1])  # 새 탭으로 전환

                # 상세 정보 크롤링
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "productTitle")))  # 상품 제목 대기
                title = driver.find_element(By.ID, "productTitle").text

                reviews = driver.find_element(By.ID, "acrCustomerReviewText").text if len(driver.find_elements(By.ID, "acrCustomerReviewText")) > 0 else "No reviews"
                brand = driver.find_element(By.CSS_SELECTOR, "tr.po-brand .po-break-word").text  if len(driver.find_elements(By.CSS_SELECTOR, "tr.po-brand .po-break-word")) > 0 else "No brand"
                special_feature = driver.find_element(By.CSS_SELECTOR, "tr.po-special_feature .po-break-word").text if len(driver.find_elements(By.CSS_SELECTOR, "tr.po-special_feature .po-break-word")) > 0 else "No special feature"
                price = driver.find_element(By.CLASS_NAME, "a-price-whole").text + "." + driver.find_element(By.CLASS_NAME, "a-price-fraction").text
                total_star = driver.find_element(By.CSS_SELECTOR, ".a-popover-trigger .a-size-small.a-color-base").text if len(driver.find_elements(By.CSS_SELECTOR, ".a-popover-trigger .a-size-small.a-color-base")) > 0 else "No rating"
                
                # 추가 제품 세부 정보
                detail_bullets = driver.find_element(By.ID, "detailBullets_feature_div")
                product_details = detail_bullets.find_elements(By.CSS_SELECTOR, "li span.a-list-item")
                detail_dict = {}

                for detail in product_details:
                    try:
                        # ':' 기준으로 나누어 key와 value 추출
                        key = detail.find_element(By.TAG_NAME, "span").text.split(":")[0].strip()
                        value = detail.text.split(":")[1].strip()
                        detail_dict[key] = value
                    except Exception:
                        continue

                ASIN  = detail_dict['ASIN']
                # Best Sellers Rank 정보 가져오기
                best_sellers_elements = driver.find_elements(By.CSS_SELECTOR, "ul.detail-bullet-list > li > span.a-list-item")

                best_sellers_rank_text = "No result"  # 기본값 설정
                for element in best_sellers_elements:
                    if "Best Sellers Rank" in element.text:
                        try:
                            # Best Sellers Rank가 포함된 텍스트에서 순위 추출
                            best_sellers_rank_text = element.text.split(":")[1].strip()
                            break  # 원하는 값을 찾으면 루프 종료
                        except Exception:
                            best_sellers_rank_text = "No result"
                            break

                print()
                print(f"ASIN: {ASIN}")
                print(f"Title: {title}")
                print(f"brand: {brand}")
                print(f"price: {price}")
                print()

                item_list.append({
                                    "ASIN" : ASIN,
                                    "title": title,
                                    "brand": brand,
                                    "price": price,
                                    "Special_Feature": special_feature,
                                    "total_star_mean": total_star,
                                    "detail_dict" : detail_dict,
                                    "best_sellers_rank_Feature" : best_sellers_rank_text
                                    })

                # 리뷰 있으면 리뷰 정보 가져오기
                if reviews != "No reviews":
                    print('리뷰 크롤링')
                    see_more_reviews_link = wait.until( EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-hook='see-all-reviews-link-foot']")))
                    actions = ActionChains(driver)                    
                    actions.move_to_element(see_more_reviews_link).perform()  # 링크로 스크롤 이동
                    print("스크롤 이동")

                    # 약간의 추가 대기 후 클릭 (화면이 스크롤될 시간이 필요할 수 있음)
                    see_more_reviews_link.click()
                    print("링크 클릭")
                    
                    set_sort_by_most_recent_with_scroll(driver, wait)
                    print("스크롤 실행 완료")

                    try:
                        # 리뷰 데이터를 저장할 리스트
                        reviews_list = []
                        # 리뷰 요소를 모두 가져옵니다
                        review_count = 0  # 수집한 리뷰 개수를 관리하는 변수
                        max_reviews = 30  # 최대 수집 리뷰 수

                        while review_count < max_reviews:
                            #wait_time = random.uniform(0.02, 0.08)
                            driver.implicitly_wait(7)
                            detail_reviews = driver.find_elements(By.CSS_SELECTOR, 'div[class="a-section celwidget"]')

                            for detail_review in detail_reviews:  # 현재 페이지에서 모든 리뷰를 처리
                                if review_count >= max_reviews:  # 최대 리뷰 수에 도달하면 종료
                                    break
                                try:
                                    
                                    #time.sleep(wait_time)
                                    date = detail_review.find_element(By.CSS_SELECTOR, "span[data-hook='review-date']").text if len(detail_review.find_elements(By.CSS_SELECTOR, "span[data-hook='review-date']")) > 0 else "No date"
                                    review_title = detail_review.find_element(By.CLASS_NAME, "review-title").text if len(detail_review.find_elements(By.CLASS_NAME, "review-title")) > 0 else "No title"
                                    review_rating_element =  detail_review.find_element(By.CSS_SELECTOR, "span.a-icon-alt")
                                    review_rating = driver.execute_script("return arguments[0].innerText;", review_rating_element)
                                    content = detail_review.find_element(By.CSS_SELECTOR, "span[data-hook='review-body']").text if len(detail_review.find_elements(By.CSS_SELECTOR, "span[data-hook='review-body']")) > 0 else "No content"

                                    print(f"  Review {review_count + 1}")
                                    print(f"  Title: {review_title}")
                                    print("-" * 50)

                                    reviews_list.append({
                                                            "review_num" : ASIN+"__"+str(review_count),
                                                            "ASIN" : ASIN,
                                                            "title": title,
                                                            "date": date,
                                                            "review_rating": review_rating,
                                                            "content": content
                                    })

                                    review_count += 1  # 수집한 리뷰 개수 증가
                                except Exception as e:
                                    print(f"Error extracting review {review_count + 1}: {e}")
                                    continue

                            try:
                                if review_count >= max_reviews:  # 최대 리뷰 수에 도달하면 종료
                                    break
                                click_next_page(driver, wait)
                            except Exception as e:
                                print(f"No more pages or error: {e}")
                                break  # 더 이상 페이지가 없거나 오류가 발생하면 종료

                    except Exception as e:
                        print(f"Error retrieving reviews: {e}")
                
                print("=" * 50)
                # 새 탭 닫기
                driver.close()
                driver.switch_to.window(driver.window_handles[0])  # 원래 탭으로 돌아가기
            except Exception as e:
                print(f"Error processing item {idx + 1}: {e}")
                continue
            print()            
            print(item_list)

            # DataFrame 변환
            item_df = pd.json_normalize(item_list)

            # `detail_dict` 관련 컬럼 병합
            detail_cols = [col for col in item_df.columns if col.startswith("detail_dict.")]
            if detail_cols:
                # `detail_dict` 관련 데이터를 다시 병합
                item_df["detail_dict"] = item_df[detail_cols].apply(
                    lambda row: {col.split(".")[1]: row[col] for col in detail_cols if pd.notnull(row[col])},
                    axis=1,
                )
                # 변환 완료 후 detail_dict 관련 컬럼 제거
                item_df.drop(columns=detail_cols, inplace=True)

            # DataFrame 변환

            # detail_dict 열을 JSON 문자열로 변환
            item_df["detail_dict"] = item_df["detail_dict"].apply(json.dumps)

            # price 및 total_star_mean을 숫자형으로 변환
            item_df["price"] = pd.to_numeric(item_df["price"], errors="coerce")
            item_df["total_star_mean"] = pd.to_numeric(item_df["total_star_mean"], errors="coerce")

            # MySQL에 item_df 로드
            load_items(df=item_df, my_sql_client=my_sql_client)
            
            review_df = pd.json_normalize(reviews_list)
            print()
            print(review_df.columns)

            load_reviews(df = review_df, my_sql_client = my_sql_client)

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

# 함수 실행
crawl_amazon("K-beauty")
