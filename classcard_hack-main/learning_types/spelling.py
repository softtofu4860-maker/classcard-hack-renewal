import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_spelling(driver, num_d, da_e, da_k):
    print("스펠학습을 시작합니다.")
    wait = WebDriverWait(driver, 10)
    time.sleep(1)

    # 1. 학습 세션 진입 버튼 클릭
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='spell'], .btn-spell, div.study-btn:nth-child(3)"))).click()
        time.sleep(1)
    except Exception:
        pass

    # 2. 시작 팝업 레이어 처리
    start_selectors = [
        "a.btn-start", 
        "#wrapper-learn .start-opt-body a",
        "#wrapper-learn a.btn-primary",
        "//a[contains(text(), '학습 시작')]",
        "//a[contains(text(), '이닝')]"
    ]
    
    for selector in start_selectors:
        try:
            if selector.startswith("//"):
                btn = driver.find_element(By.XPATH, selector)
            else:
                btn = driver.find_element(By.CSS_SELECTOR, selector)
            if btn.is_displayed():
                btn.click()
                break
        except Exception:
            pass

    time.sleep(1.5)
    print(f"전체구간 {num_d}개 카드 학습 진행 중...")

    pos_pattern = re.compile(r'\[.*?\]\s*')

    # 3. 문제 풀이 루프
    for i in range(num_d):
        try:
            question_elem = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, ".card-item.active .question-text, #wrapper-learn .question-text, .cq-text, .text-normal, div.card-body"
            )))
            
            raw_text = question_elem.text.strip().split("\n")[0]
            clean_text = pos_pattern.sub('', raw_text).strip()

            target_answer = ""
            for idx, k_val in enumerate(da_k):
                if clean_text in k_val or k_val in clean_text:
                    target_answer = da_e[idx]
                    break
            
            if not target_answer:
                for idx, e_val in enumerate(da_e):
                    if clean_text.lower() == e_val.lower():
                        target_answer = da_k[idx]
                        break

            if not target_answer and da_e:
                target_answer = da_e[i % len(da_e)]

            input_box = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "input[type='text']:not([style*='display: none'])"
            )))
            
            input_box.click()
            input_box.clear()
            input_box.send_keys(target_answer)
            time.sleep(0.1)
            input_box.send_keys(Keys.ENTER)

            time.sleep(0.7)

        except Exception:
            time.sleep(0.3)
            continue

    print("스펠학습이 완료되었습니다.")