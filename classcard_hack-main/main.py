import time
import warnings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from utility import chd_wh, get_id, word_get, choice_class, choice_set
from learning_types import (
    memorization,
    recall,
    spelling,
    test
)

warnings.filterwarnings("ignore", category=DeprecationWarning)

def main():
    account = get_id()

    chrome_options = Options()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("--start-maximized")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception:
        driver = webdriver.Chrome(options=chrome_options)

    driver.implicitly_wait(3)
    wait = WebDriverWait(driver, 10)

    try:
        # 1. 로그인
        print("\n[진행] 클래스카드 로그인 페이지 접속...")
        driver.get("https://www.classcard.net/Login")

        tag_id = wait.until(EC.element_to_be_clickable((By.NAME, "login_id")))
        tag_pw = driver.find_element(By.NAME, "login_pwd")

        tag_id.clear()
        tag_id.send_keys(account["id"])
        tag_pw.send_keys(account["pw"])

        try:
            driver.find_element(By.CSS_SELECTOR, "#loginForm a.btn, form .btn, button[type='submit']").click()
        except Exception:
            tag_pw.submit()

        time.sleep(2)

        # 2. 클래스 선택
        class_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/ClassMain/')]")
        class_dict = {}
        valid_idx = 0
        seen_ids = set()

        for item in class_elements:
            try:
                href = item.get_attribute("href") or ""
                if "/ClassMain/" not in href:
                    continue
                class_id = href.split("/ClassMain/")[1].split("?")[0].split("/")[0]
                class_name = item.text.strip() or item.get_attribute("innerText").strip()
                if class_id and class_id not in seen_ids and class_id != "joinClass":
                    seen_ids.add(class_id)
                    class_dict[valid_idx] = {"class_name": class_name, "class_id": class_id}
                    valid_idx += 1
            except Exception:
                continue

        if not class_dict:
            print("\n[오류] 가입된 클래스 목록을 찾을 수 없습니다. 아이디/비밀번호를 확인해 주세요.")
            return

        choice_class_val = choice_class(class_dict)
        target_class_id = class_dict[choice_class_val]["class_id"]

        driver.get(f"https://www.classcard.net/ClassMain/{target_class_id}")
        time.sleep(2)

        # 3. 세트 선택
        set_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/set/') or @data-idx]")
        sets_dict = {}
        idx = 0
        seen_sets = set()

        for set_item in set_elements:
            try:
                set_id = set_item.get_attribute("data-idx")
                href = set_item.get_attribute("href") or ""
                if not set_id and "/set/" in href:
                    set_id = href.split("/set/")[1].split("/")[0].split("?")[0]
                if not set_id or set_id in seen_sets:
                    continue
                seen_sets.add(set_id)

                try:
                    card_num = set_item.find_element(By.TAG_NAME, "span").text.strip()
                except Exception:
                    card_num = ""

                title = set_item.text.replace(card_num, "").strip() or f"세트 {set_id}"
                sets_dict[idx] = {"card_num": card_num, "title": title, "set_id": set_id}
                idx += 1
            except Exception:
                continue

        if not sets_dict:
            print("\n[오류] 클래스 내 세트 목록을 찾을 수 없습니다.")
            return

        choice_set_val = choice_set(sets_dict)
        current_set_id = sets_dict[choice_set_val]["set_id"]

        # 세트 페이지 진입
        driver.get(f"https://www.classcard.net/set/{current_set_id}/{target_class_id}")

        # 4. 단어 추출
        word_d = word_get(driver)
        da_e, da_k, da_kn, da_kyn, da_ked, da_sd = word_d
        num_d = len(da_e)

        if num_d == 0:
            print("[오류] 단어 데이터를 인식하지 못했습니다. 프로그램이 종료됩니다.")
            return

        # 5. 학습 진행
        ch_d = chd_wh()

        if ch_d == 1:
            memorization.run_memorization(driver, num_d)
        elif ch_d == 2:
            recall.run_recall(driver, num_d, da_e, da_k)
        elif ch_d == 3:
            spelling.run_spelling(driver, num_d, da_e, da_k)
        elif ch_d == 4:
            test.run_test(driver, num_d, da_e, da_k)

        print("\n[완료] 학습 작업이 마무리되었습니다.")
        input("Enter 키를 누르면 브라우저를 종료합니다...")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()