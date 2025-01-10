from selenium import webdriver 
from selenium.webdriver.common.by import By

keyword = "스마트폰"
drvier = webdriver.Chrome()
drvier.get(f"https://www.coupang.com/np/search?q={keyword}")

drvier. implicitly_wait (5)

results = drvier. find_elements(By.CLASS_NAME, "descriptions-inner")
for rank, r in enumerate(results,1) :
    if rank > 10 :
        break
    try :
        name = r.find_element (By.CLASS_NAME, "name")
        price = r.find_element (By.CLASS_NAME, "price")
        print(f" {rank}위 {name.text} {price.text}")
    except :
        print("skip")
drvier.quit()