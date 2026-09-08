import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_recall(driver, num_d, da_e, da_k):
    print("리콜학습을 시작합니다.")
    wait = WebDriverWait(driver, 10)
    
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='recall'], .btn-recall, div.study-btn:nth-child(2)"))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#wrapper-learn .start-opt-body a, .btn-opt-start"))).click()
        time.sleep(1.5)
    except Exception as e:
        print("리콜학습 진입 실패:", e)
        return

    for i in range(1, num_d + 1):
        try:
            cash_elem = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, f"#wrapper-learn .study-body div:nth-child({i}) .text-normal, #wrapper-learn .question-text"
            )))
            cash_d = cash_elem.text.strip().split("\n")[0]

            try:
                if cash_d.upper() != cash_d.lower():
                    text = da_k[da_e.index(cash_d)] if cash_d in da_e else da_e[da_k.index(cash_d)]
                else:
                    text = da_e[da_k.index(cash_d)] if cash_d in da_k else da_k[da_e.index(cash_d)]
            except (ValueError, IndexError):
                text = "모름"

            options = driver.find_elements(By.CSS_SELECTOR, "#wrapper-learn .answer-btn, #wrapper-learn .option-item")

            clicked = False
            for opt in options:
                if opt.text.strip() == text or text in opt.text:
                    opt.click()
                    clicked = True
                    break

            if not clicked and options:
                random.choice(options).click()

            time.sleep(1.0)

        except Exception:
            break

    print("리콜학습이 완료되었습니다.")