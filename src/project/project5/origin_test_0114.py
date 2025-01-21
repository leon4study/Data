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

        password_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_input.send_keys(pw + Keys.RETURN)

    except Exception as e:
        print(f"오류 발생: {e}")



def set_sort_by_most_recent_with_scroll():
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
        

def click_next_item_page(wait):
    wait_time = random.uniform(0.05, 0.15)
    time.sleep(wait_time)
    try:
        # Next page 버튼 기다리기
        next_page_button = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.s-list-item-margin-right-adjustment > span > a.s-pagination-next'))
        )
        
        # execute_script를 사용해 클릭
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", next_page_button)
        time.sleep(0.1)  # 스크롤 후 잠시 대기
        driver.execute_script("arguments[0].click();", next_page_button)

        print("Successfully clicked the Next Item Page button.")
    except Exception as e:
        print(f"Error clicking Next Page button: {e}")


def click_next_review_page():
    try:
        # Next page 버튼 기다리기
        next_page_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-pagination .a-last a"))
        )
        # 버튼 클릭
        next_page_button.click()
        print("Successfully clicked the Next Review Page button.")
    except Exception as e:
        print(f"Error clicking Next Page button: {e}")
        return False
    return True
    

def score_filter():
    star_filter_selector = '.a-icon.a-icon-star-medium.a-star-medium-4'
    try:
        # 요소가 로드될 때까지 기다림
        star_filter_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, star_filter_selector))
        )
        # 요소 클릭
        star_filter_element.click()
        print("Star filter clicked successfully.")
    except Exception as e:
        print(f"Error while waiting for or clicking the star filter: {e}")

def select_best_sellers():
    """
    Selenium을 사용해 드롭다운 메뉴에서 'Best Sellers' 옵션을 선택한 후 페이지 로드를 기다리는 함수.
    
    Args:
        driver (webdriver): Selenium WebDriver 객체.
        wait_time (int): 대기 시간 (초) 기본값은 10초.
    Returns:
        None
    """
    try:
        # WebDriverWait 객체 생성
        # 드롭다운 메뉴 요소 기다림
        dropdown_element = wait.until(EC.presence_of_element_located((By.ID, "s-result-sort-select")))
        # 드롭다운 메뉴 초기화
        select = Select(dropdown_element)
        
        # "Best Sellers" 옵션 선택 (value 사용)
        select.select_by_value("exact-aware-popularity-rank")
        
        # 다음 페이지 로드를 기다림
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))
        print("Successfully selected 'Best Sellers' and waited for the next page to load.")
    except Exception as e:
        print(f"An error occurred: {e}")



def crawl_amazon(keyword="skin+care"):
    try:
        # 아마존 검색 페이지 열기
        driver.get(f"https://www.amazon.com")
        driver.implicitly_wait(5)  # 페이지 로딩 대기
        wait_time = random.uniform(0.05, 0.15)
        time.sleep(wait_time)

        wait_time = random.uniform(0.05, 0.15)
        time.sleep(wait_time)
        
        search_box = driver.find_element(By.ID, 'twotabsearchtextbox')

        # 검색어 입력
        search_box.clear()  # 혹시 검색창에 이전 텍스트가 있다면 삭제
        search_box.send_keys(keyword)  # "skin care" 입력

        # 검색 실행 (Enter 키 사용 또는 검색 버튼 클릭)
        search_box.send_keys(Keys.RETURN)
        
        amazon_login(ID,PW)
        

        # id="n/3760911"을 가진 요소 찾기
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#n\\/3760911')))

        # 요소를 클릭하거나 원하는 작업 수행
        element.click()



        
        select_best_sellers()

        time.sleep(1)
        # 크롤링할 요소 선택 (CSS Selector 사용)
        categories = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.a-spacing-micro.s-navigation-indent-2')))

        
        # 각 카테고리 페이지 방문 및 크롤링
        for category in categories[1:]:
            try:
                # 링크 클릭
                link = category.find_element(By.TAG_NAME, 'a')  # 내부 'a' 태그 찾기
                category_name = link.text  # 카테고리 이름 저장
                
                # 새 창 열기
                driver.execute_script("window.open(arguments[0], '_blank');", link.get_attribute("href"))
                time.sleep(2)  # 페이지 로딩 대기

                # 새 창으로 전환
                driver.switch_to.window(driver.window_handles[-1])
                #===================================================
                cnt = 0
                while cnt < 100:
                    time.sleep(0.5)
                    time.sleep(wait_time)

                    try :
                        query = "SELECT ASIN FROM items"  # items 테이블에서 모든 데이터를 조회
                        df = my_sql_client.fetch_as_dataframe(query)
                        ASIN_list = df['ASIN'].to_list()
                        print(ASIN_list[:4])
                    except Exception as e:
                        print(f"error occurred from get_asin_from_sql {e}")
                    

                    # 모든 리스트 아이템 가져오기
                    items = driver.find_elements(By.CSS_SELECTOR, '[role="listitem"]')
                    print("\n", len(items), "\n")
                    item_list = []
                    
                    # 각 아이템 클릭 및 상세 정보 크롤링
                    for idx, item in enumerate(items):
                        try:
                            ASIN = item.get_attribute("data-asin")
                            if ASIN in ASIN_list:
                                print("ASIN PASSED")
                                continue  # 이미 처리된 ASIN은 건너뜀
                            else:
                                try:
                                    if item.find_elements(By.CLASS_NAME, "puis-sponsored-label-text"):  # Sponsored 라벨 존재 확인
                                        continue  # Sponsored 항목은 건너뜀
                                except Exception as e:
                                    print(f"Sponsored 라벨 확인 중 에러 발생: {e}")
                                    # 에러가 발생하면 Sponsored 여부를 무시하고 다음 로직 실행


                                cnt += 1
                                ASIN_list.append(ASIN)

                                # 새 탭에서 열기 위해 Shift + Click
                                item_link = item.find_element(By.CSS_SELECTOR, 'a.a-link-normal')
                                item_url = item_link.get_attribute("href")

                                time.sleep(0.4)
                                # 새 탭에서 상세 정보 열기
                                driver.execute_script("window.open(arguments[0], '_blank');", item_url)
                                driver.switch_to.window(driver.window_handles[-1])  # 새 탭으로 전환

                                # 상세 정보 크롤링


                                # 추가 제품 세부 정보
                                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "productTitle"))) 

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

                                # 상품 제목
                                title = driver.find_element(By.ID, "productTitle").text
                                reviews = driver.find_element(By.ID, "acrCustomerReviewText").text if len(driver.find_elements(By.ID, "acrCustomerReviewText")) > 0 else "No ratings"
                                brand = driver.find_element(By.CSS_SELECTOR, "tr.po-brand .po-break-word").text  if len(driver.find_elements(By.CSS_SELECTOR, "tr.po-brand .po-break-word")) > 0 else "No brand"
                                special_feature = driver.find_element(By.CSS_SELECTOR, "tr.po-special_feature .po-break-word").text if len(driver.find_elements(By.CSS_SELECTOR, "tr.po-special_feature .po-break-word")) > 0 else "No special feature"
                                price = driver.find_element(By.CLASS_NAME, "a-price-whole").text + "." + driver.find_element(By.CLASS_NAME, "a-price-fraction").text
                                total_star = driver.find_element(By.CSS_SELECTOR, ".a-popover-trigger .a-size-small.a-color-base").text if len(driver.find_elements(By.CSS_SELECTOR, ".a-popover-trigger .a-size-small.a-color-base")) > 0 else "No star"
                                

                                # total_rating counts
                                totaL_rating_counts = driver.find_element(By.CSS_SELECTOR, "#acrCustomerReviewText").text
                                global_rating_count = int(totaL_rating_counts.strip("()").replace(",", ""))
                                
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
                                print(f"index: {idx}")
                                print(f"ASIN: {ASIN}")
                                print(f"Title: {title}")
                                print(f"global_rating_count: {global_rating_count}")
                                print(f"price: {price}")
                                print()

                                item_list.append({
                                                    "ASIN" : ASIN, "title" : title,
                                                    "brand" : brand, "price" : price,
                                                    "global_rating_count" : global_rating_count,
                                                    "Special_Feature" : special_feature,
                                                    "total_star_mean" : total_star,
                                                    "detail_dict" : detail_dict,
                                                    "best_sellers_rank_Feature" : best_sellers_rank_text
                                                    })

                                # rating 이력 있으면 리뷰 정보 가져오기
                                if reviews =="No ratings":
                                    print("No ratings")
                                    continue
                                else:
                                    print(f"{category_name} 리뷰 크롤링")
                                    see_more_reviews_link = wait.until( EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-hook='see-all-reviews-link-foot']")))
                                    actions = ActionChains(driver)                    
                                    actions.move_to_element(see_more_reviews_link).perform()  # 링크로 스크롤 이동
                                    print("스크롤 이동")

                                    # 약간의 추가 대기 후 클릭 (화면이 스크롤될 시간이 필요할 수 있음)
                                    time.sleep(0.5)
                                    see_more_reviews_link.click()
                                    print("링크 클릭")
                                    
                                    set_sort_by_most_recent_with_scroll()
                                    print("스크롤 실행 완료")

                                    try:
                                        # 리뷰 데이터를 저장할 리스트
                                        reviews_list = []
                                        # 리뷰 요소를 모두 가져옵니다
                                        review_count = 0  # 수집한 리뷰 개수를 관리하는 변수
                                        max_reviews = 50  # 최대 수집 리뷰 수

                                        while review_count < max_reviews:
                                            wait_time = random.uniform(0.4, 0.6)
                                            time.sleep(wait_time)
                                            driver.implicitly_wait(7)

                                            detail_reviews = driver.find_elements(By.CSS_SELECTOR, 'div[class="a-section celwidget"]')

                                            # 리뷰가 없는 경우 처리
                                            if len(detail_reviews) == 0:
                                                print("No reviews found on the current page.")
                                                reviews_list.append({
                                                    "review_num": ASIN + "__" + str(review_count),
                                                    "ASIN": ASIN,
                                                    "title": title,
                                                    "date": "No date",
                                                    "review_rating": "No review",
                                                    "content": "No content"
                                                })
                                                break  # 리뷰가 없으므로 더 이상 시도하지 않고 루프 종료

                                            for detail_review in detail_reviews:  # 현재 페이지에서 모든 리뷰를 처리
                                                
                                                if review_count >= max_reviews:  # 최대 리뷰 수에 도달하면 종료
                                                    break
                                                try:
                                                    #time.sleep(wait_time)
                                                    date = detail_review.find_element(By.CSS_SELECTOR, "span[data-hook='review-date']").text if len(detail_review.find_elements(By.CSS_SELECTOR, "span[data-hook='review-date']")) > 0 else "No date"
                                                    review_title = detail_review.find_element(By.CLASS_NAME, "review-title").text if len(detail_review.find_elements(By.CLASS_NAME, "review-title")) > 0 else "No title"
                                                    # 리뷰 평점 처리
                                                    review_rating_element = detail_review.find_elements(By.CSS_SELECTOR, "span.a-icon-alt")
                                                    review_rating = (
                                                        driver.execute_script("return arguments[0].innerText;", review_rating_element[0]) 
                                                        if len(review_rating_element) > 0 
                                                        else "No review"
                                                    )
                                                    content = detail_review.find_element(By.CSS_SELECTOR, "span[data-hook='review-body']").text if len(detail_review.find_elements(By.CSS_SELECTOR, "span[data-hook='review-body']")) > 0 else "No content"
                                                    print(f"  Review {review_count + 1}")
                                                    print(f"  Title: {review_title}")
                                                    print("-" * 50)

                                                    reviews_list.append({
                                                                            "review_num" : ASIN+"__"+str(review_count),
                                                                            "ASIN" : ASIN,"title" : title,
                                                                            "date" : date, "review_rating" : review_rating,
                                                                            "content" : content
                                                    })
                                                    review_count += 1  # 수집한 리뷰 개수 증가
                                                except Exception as e:
                                                    print(f"Error extracting review {review_count + 1}: {e}")
                                                    continue
                                            
                                            if review_count >= max_reviews:  # 최대 리뷰 수에 도달하면 종료
                                                break
                                            if not click_next_review_page():
                                                break
                                        # 리뷰가 없는 경우를 대비한 기본 값 처리
                                        if len(detail_reviews) == 0:
                                            print("Returning to the previous page due to no reviews.")
                                            driver.back()
                                            reviews_list.append({
                                                "review_num": ASIN + "__" + str(review_count),
                                                "ASIN": ASIN,
                                                "title": title,
                                                "date": "No date",
                                                "review_rating": "No review",
                                                "content": "No content"
                                            })

                                    except Exception as e:
                                        print(f"Error retrieving reviews: {e}")
                                    
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
                                print("=" * 50)
                                    # 새 탭 닫기
                                driver.close()
                                driver.switch_to.window(driver.window_handles[1])  # 원래 탭으로 돌아가기

                        except Exception as e:
                            print(f"Error processing item {idx + 1}: {e}")
                            continue
                    
                    click_next_item_page(wait)

                #===================================================
                # 새 창을 닫고 원래 창으로 돌아가기
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(2)  # 페이지 로딩 대기

            except Exception as e:
                print(f"Error processing category {category_name}: {e}")

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

# 함수 실행
crawl_amazon("K-beauty")
