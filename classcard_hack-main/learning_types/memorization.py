import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_memorization(driver, num_d):
    print("암기학습을 시작합니다.")
    wait = WebDriverWait(driver, 10)
    
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='memorize'], .btn-memorize, div.study-btn:nth-child(1)"))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#wrapper-learn .start-opt-body a, .btn-opt-start"))).click()
        time.sleep(1.5)
    except Exception as e:
        print("암기학습 진입 실패:", e)
        return

    for _ in range(num_d):
        try:
            cover_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-down-cover-box, .btn-turn")))
            cover_btn.click()
            time.sleep(0.3)
            
            know_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-know-box, .btn-know")))
            know_btn.click()
            time.sleep(0.8)
        except Exception:
            break

    print("암기학습이 완료되었습니다.")