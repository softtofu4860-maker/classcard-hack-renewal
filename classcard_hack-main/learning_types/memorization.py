import time
from selenium.webdriver.common.by import By
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


def run_memorization(driver, num_d):
    print("암기학습을 시작합니다.")
    wait = WebDriverWait(driver, 12)

    study_selectors = [
        (By.CSS_SELECTOR, "a[href*='memorize']"),
        (By.CSS_SELECTOR, ".btn-memorize"),
        (By.CSS_SELECTOR, "div.study-btn:nth-child(1)"),
        (By.XPATH, "//*[contains(normalize-space(.), '암기학습')]")
    ]
    if not _click_first(driver, wait, study_selectors, "암기학습"):
        print(f"[진단] 현재 URL: {driver.current_url}")
        return False

    time.sleep(1)

    start_selectors = [
        (By.CSS_SELECTOR, "#wrapper-learn .start-opt-body a"),
        (By.CSS_SELECTOR, ".btn-opt-start"),
        (By.CSS_SELECTOR, "a.btn-start"),
        (By.CSS_SELECTOR, "#wrapper-learn a.btn-primary"),
        (By.XPATH, "//a[contains(normalize-space(.), '학습 시작')]")
    ]
    _click_first(driver, wait, start_selectors, "학습 시작")
    time.sleep(1.5)

    learn_selectors = [
        (By.ID, "wrapper-learn"),
        (By.CSS_SELECTOR, ".btn-down-cover-box"),
        (By.CSS_SELECTOR, ".btn-turn"),
        (By.CSS_SELECTOR, ".btn-short-change-card")
    ]
    learn_ready = False
    for by, selector in learn_selectors:
        try:
            wait.until(EC.presence_of_element_located((by, selector)))
            learn_ready = True
            break
        except Exception:
            continue

    if not learn_ready:
        print("[오류] 암기학습 화면이 열리지 않았습니다.")
        print(f"[진단] 현재 URL: {driver.current_url}")
        print(f"[진단] 페이지 제목: {driver.title}")
        return False

    print(f"[진행] 암기학습 {num_d}개 카드 처리 중...")
    completed = 0

    for _ in range(num_d):
        cover_selectors = [
            (By.CSS_SELECTOR, ".btn-down-cover-box"),
            (By.CSS_SELECTOR, ".btn-turn"),
            (By.CSS_SELECTOR, "a.btn-short-change-card")
        ]
        if not _click_first(driver, wait, cover_selectors, "카드 넘김"):
            break
        time.sleep(0.5)

        know_selectors = [
            (By.CSS_SELECTOR, ".btn-know-box"),
            (By.CSS_SELECTOR, ".btn-know")
        ]
        if not _click_first(driver, wait, know_selectors, "알고 있음"):
            completed += 1
            continue

        completed += 1
        time.sleep(0.8)

    if completed == num_d:
        print(f"[완료] 암기학습 {completed}/{num_d}개 카드 처리 완료")
        return True

    print(f"[중단] 암기학습이 {completed}/{num_d}개에서 멈췄습니다.")
    print(f"[진단] 현재 URL: {driver.current_url}")
    return False
