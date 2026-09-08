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


def _visible_text(element):
    """Selenium의 text/innerText/textContent를 순서대로 사용해 표시 문자열을 얻는다."""
    if element is None:
        return ""

    for attr in (None, "innerText", "textContent"):
        try:
            if attr is None:
                value = element.text
            else:
                value = element.get_attribute(attr)
            if value:
                value = " ".join(value.split())
                if value:
                    return value
        except Exception:
            continue
    return ""


def _extract_class_list(driver, wait):
    """로그인 후 현재 페이지에서 실제 클래스 목록을 찾아 반환한다."""
    selectors = [
        (By.CSS_SELECTOR, ".left-class-list a[href*='/ClassMain/']"),
        (By.CSS_SELECTOR, "a[href*='/ClassMain/']"),
        (By.XPATH, "//a[contains(@href, '/ClassMain/')]")
    ]

    elements = []
    for by, selector in selectors:
        try:
            wait.until(EC.presence_of_all_elements_located((by, selector)))
            elements = driver.find_elements(by, selector)
            if elements:
                break
        except Exception:
            continue

    class_dict = {}
    seen_ids = set()

    for item in elements:
        try:
            href = (item.get_attribute("href") or "").strip()
            if "/ClassMain/" not in href:
                continue

            class_id = href.split("/ClassMain/", 1)[1].split("?", 1)[0].split("/", 1)[0].strip()
            if not class_id or class_id == "joinClass" or class_id in seen_ids:
                continue

            class_name = _visible_text(item)

            if not class_name:
                for child_selector in (".class-name", ".class-title", ".name", "span", "div"):
                    try:
                        child = item.find_element(By.CSS_SELECTOR, child_selector)
                        class_name = _visible_text(child)
                        if class_name:
                            break
                    except Exception:
                        continue

            if not class_name:
                class_name = (
                    item.get_attribute("aria-label")
                    or item.get_attribute("title")
                    or ""
                ).strip()

            if not class_name:
                class_name = f"클래스 ({class_id})"

            seen_ids.add(class_id)
            class_dict[len(class_dict)] = {
                "class_name": class_name,
                "class_id": class_id,
            }
        except Exception:
            continue

    return class_dict


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
    wait = WebDriverWait(driver, 12)

    try:
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

        time.sleep(1)
        class_dict = _extract_class_list(driver, wait)

        if not class_dict:
            print("\n[오류] 가입된 클래스 목록을 찾을 수 없습니다. 로그인 상태와 클래스 목록을 확인해 주세요.")
            return

        print(f"[확인] 클래스 {len(class_dict)}개를 찾았습니다.")

        choice_class_val = choice_class(class_dict)
        target_class_id = class_dict[choice_class_val]["class_id"]

        driver.get(f"https://www.classcard.net/ClassMain/{target_class_id}")
        time.sleep(2)

        set_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/set/') or @data-idx]")
        sets_dict = {}
        idx = 0
        seen_sets = set()

        for set_item in set_elements:
            try:
                set_id = set_item.get_attribute("data-idx")
                href = set_item.get_attribute("href") or ""
                if not set_id and "/set/" in href:
                    set_id = href.split("/set/", 1)[1].split("/", 1)[0].split("?", 1)[0]
                if not set_id or set_id in seen_sets:
                    continue
                seen_sets.add(set_id)

                try:
                    card_num = set_item.find_element(By.TAG_NAME, "span").text.strip()
                except Exception:
                    card_num = ""

                title = _visible_text(set_item)
                if card_num and card_num in title:
                    title = title.replace(card_num, "", 1).strip()
                title = title or f"세트 {set_id}"

                sets_dict[idx] = {"card_num": card_num, "title": title, "set_id": set_id}
                idx += 1
            except Exception:
                continue

        if not sets_dict:
            print("\n[오류] 클래스 내 세트 목록을 찾을 수 없습니다.")
            return

        choice_set_val = choice_set(sets_dict)
        current_set_id = sets_dict[choice_set_val]["set_id"]

        driver.get(f"https://www.classcard.net/set/{current_set_id}/{target_class_id}")

        word_d = word_get(driver)
        da_e, da_k, da_kn, da_kyn, da_ked, da_sd = word_d
        num_d = len(da_e)

        if num_d == 0:
            print("[오류] 단어 데이터를 인식하지 못했습니다. 프로그램이 종료됩니다.")
            return

        ch_d = chd_wh()

        if ch_d == 1:
            result = memorization.run_memorization(driver, num_d)
        elif ch_d == 2:
            result = recall.run_recall(driver, num_d, da_e, da_k)
        elif ch_d == 3:
            result = spelling.run_spelling(driver, num_d, da_e, da_k)
        elif ch_d == 4:
            result = test.run_test(driver, num_d, da_e, da_k)
        else:
            result = False

        if result is False:
            print("\n[중단] 학습 화면 진입 또는 카드 처리가 완료되지 않았습니다.")
            print("[진단] 브라우저의 현재 화면을 확인한 뒤 위의 오류 내용을 확인해 주세요.")
            input("Enter 키를 누르면 브라우저를 종료합니다...")
            return

        print("\n[완료] 학습 작업이 마무리되었습니다.")
        input("Enter 키를 누르면 브라우저를 종료합니다...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
