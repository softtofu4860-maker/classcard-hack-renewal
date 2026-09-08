import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def run_test(driver, num_d, da_e, da_k):
    print("테스트학습을 시작합니다.")
    wait = WebDriverWait(driver, 10)
    
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='test'], .btn-test"))).click()
        time.sleep(1)
        
        start_btns = driver.find_elements(By.CSS_SELECTOR, "#wrapper-test .retry-layer a, #wrapper-test .prepare-layer a, .quiz-start-div a")
        for btn in start_btns:
            if btn.is_displayed():
                btn.click()
                time.sleep(0.5)

        try:
            alert_btn = driver.find_element(By.CSS_SELECTOR, "#alertModal a.btn, #alertModal .modal-footer a")
            if alert_btn.is_displayed():
                alert_btn.click()
        except Exception:
            pass

        time.sleep(1.5)
    except Exception as e:
        print("테스트학습 진입 실패:", e)
        return

    for i in range(1, num_d + 1):
        try:
            item_selector = f"#testForm .quiz-item:nth-child({i}), #testForm div.quiz-item-{i}"
            
            cash_elem = driver.find_element(By.CSS_SELECTOR, f"{item_selector} .card-text, {item_selector} .question-text")
            cash_d = cash_elem.text.strip().split("\n")[0]
            
            try:
                cash_elem.click()
            except Exception:
                pass

            time.sleep(0.3)

            try:
                if cash_d.upper() != cash_d.lower():
                    text = da_k[da_e.index(cash_d)] if cash_d in da_e else da_e[da_k.index(cash_d)]
                else:
                    text = da_e[da_k.index(cash_d)] if cash_d in da_k else da_k[da_e.index(cash_d)]
            except (ValueError, IndexError):
                text = "모름"

            try:
                input_tag = driver.find_element(By.CSS_SELECTOR, f"{item_selector} input[type='text']")
                submit_tag = driver.find_element(By.CSS_SELECTOR, f"{item_selector} a.btn-submit, {item_selector} a.btn-blue")
                
                input_tag.click()
                input_tag.send_keys(text)
                submit_tag.click()
            except NoSuchElementException:
                box_items = driver.find_elements(By.CSS_SELECTOR, f"{item_selector} .option-item, {item_selector} label, {item_selector} .answer-btn")
                
                selected = False
                for box in box_items:
                    if box.text.strip() == text or text in box.text:
                        driver.execute_script("arguments[0].click();", box)
                        selected = True
                        break
                
                if not selected and box_items:
                    driver.execute_script("arguments[0].click();", box_items[0])

            time.sleep(0.8)

        except Exception:
            continue

    print("테스트학습이 완료되었습니다.")