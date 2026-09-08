import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _click_first(driver, wait, selectors, label):
    last_error = None
    for by, selector in selectors:
        try:
            element = wait.until(EC.element_to_be_clickable((by, selector)))
            element.click()
            print(f"[확인] {label} 버튼을 찾았습니다.")
            return True
        except Exception as exc:
            last_error = exc
    print(f"[오류] {label} 버튼을 찾지 못했습니다.")
    if last_error:
        print(f"[진단] {type(last_error).__name__}: {last_error}")
    return False


def run_spelling(driver, num_d, da_e, da_k):
    print("스펠학습을 시작합니다.")

    # 기존 코드는 버튼을 못 찾아도 예외를 삼킨 채 문제 풀이 루프로 들어가
    # 세트 페이지에서 계속 대기하는 문제가 있었습니다.
    wait = WebDriverWait(driver, 4)
    time.sleep(0.8)

    study_selectors = [
        (By.CSS_SELECTOR, "a[href*='spell']"),
        (By.CSS_SELECTOR, ".btn-spell"),
        (By.CSS_SELECTOR, ".study-btn.spell"),
        (By.XPATH, "//a[contains(normalize-space(.), '스펠학습') or contains(normalize-space(.), '스펠 학습') ]"),
        (By.XPATH, "//button[contains(normalize-space(.), '스펠학습') or contains(normalize-space(.), '스펠 학습') ]")
    ]

    if not _click_first(driver, wait, study_selectors, "스펠학습"):
        print(f"[진단] 현재 URL: {driver.current_url}")
        print(f"[진단] 페이지 제목: {driver.title}")
        return False

    time.sleep(0.8)

    start_selectors = [
        (By.CSS_SELECTOR, "a.btn-start"),
        (By.CSS_SELECTOR, ".btn-opt-start"),
        (By.CSS_SELECTOR, "#wrapper-learn .start-opt-body a"),
        (By.XPATH, "//a[contains(normalize-space(.), '학습 시작') or contains(normalize-space(.), '시작하기') ]"),
        (By.XPATH, "//button[contains(normalize-space(.), '학습 시작') or contains(normalize-space(.), '시작하기') ]")
    ]

    # 시작 버튼이 없는 버전도 있으므로, 발견됐을 때만 클릭한다.
    _click_first(driver, wait, start_selectors, "학습 시작")
    time.sleep(1.2)

    input_selectors = [
        (By.CSS_SELECTOR, "input.input-answer"),
        (By.CSS_SELECTOR, "input[type='text']:not([style*='display: none'])"),
        (By.CSS_SELECTOR, "input[type='text']")
    ]

    try:
        input_box = None
        for by, selector in input_selectors:
            try:
                input_box = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((by, selector))
                )
                if input_box.is_enabled():
                    break
            except Exception:
                input_box = None

        if input_box is None:
            print("[오류] 스펠학습 입력창을 찾지 못했습니다.")
            print(f"[진단] 현재 URL: {driver.current_url}")
            print(f"[진단] 페이지 제목: {driver.title}")
            return False
    except Exception as exc:
        print(f"[오류] 스펠학습 화면 확인 실패: {type(exc).__name__}: {exc}")
        return False

    print(f"전체구간 {num_d}개 카드 학습 진행 중...")

    pos_pattern = re.compile(r'\[.*?\]\s*')
    completed = 0

    for i in range(num_d):
        try:
            question_elem = None
            question_selectors = [
                (By.CSS_SELECTOR, ".card-item.active .question-text"),
                (By.CSS_SELECTOR, "#wrapper-learn .question-text"),
                (By.CSS_SELECTOR, ".cq-text"),
                (By.CSS_SELECTOR, ".text-normal")
            ]

            for by, selector in question_selectors:
                try:
                    question_elem = WebDriverWait(driver, 2).until(
                        EC.visibility_of_element_located((by, selector))
                    )
                    if question_elem.text.strip():
                        break
                except Exception:
                    question_elem = None

            if question_elem is None:
                print(f"[중단] {i + 1}/{num_d}번 카드의 문제를 찾지 못했습니다.")
                break

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

            input_box = None
            for by, selector in input_selectors:
                try:
                    input_box = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    break
                except Exception:
                    input_box = None

            if input_box is None:
                print(f"[중단] {i + 1}/{num_d}번 카드의 입력창을 찾지 못했습니다.")
                break

            input_box.click()
            input_box.clear()
            input_box.send_keys(target_answer)
            input_box.send_keys(Keys.ENTER)
            completed += 1
            print(f"[진행] {completed}/{num_d}")
            time.sleep(0.7)

        except Exception as exc:
            print(f"[중단] {i + 1}/{num_d}번 카드 처리 중 오류: {type(exc).__name__}: {exc}")
            break

    if completed == num_d:
        print(f"[완료] 스펠학습 {completed}/{num_d}개 카드 처리 완료")
        return True

    print(f"[중단] 스펠학습이 {completed}/{num_d}개에서 멈췄습니다.")
    print(f"[진단] 현재 URL: {driver.current_url}")
    return False
