import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def run_matching_game(driver, da_e, da_k):
    print("매칭게임을 시작합니다...")
    try:
        driver.find_element(By.CSS_SELECTOR, "a[href*='Match'], .btn-match").click()
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".btn-opt-start, .btn-blue").click()
        time.sleep(2)
    except Exception as e:
        print("매칭게임 진입 실패:", e)
        return

    while True:
        try:
            html = BeautifulSoup(driver.page_source, "html.parser")
            left_cards = html.select(".match-body [id^='left_card_']")
            
            if not left_cards:
                break

            for left in left_cards:
                card_id = left.get("id")
                word = left.get_text(strip=True)
                
                if word in da_e:
                    ans_k = da_k[da_e.index(word)]
                    right_cards = driver.find_elements(By.CSS_SELECTOR, ".match-body [id^='right_card_']")
                    
                    for right in right_cards:
                        if right.text.strip() == ans_k:
                            left_elem = driver.find_element(By.ID, card_id)
                            
                            ActionChains(driver).click(left_elem).click(right).perform()
                            time.sleep(0.2)
                            break
            time.sleep(0.5)
        except Exception:
            break

    print("매칭게임이 완료되었습니다.")