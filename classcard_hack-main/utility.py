import re
import time
from getpass import getpass

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By


def get_id():
    print("========================================")
    print("         CLASS CARD AUTO BOT            ")
    print("========================================")
    user_id = input("아이디를 입력하세요: ").strip()
    user_pw = getpass("비밀번호를 입력하세요: ")
    return {"id": user_id, "pw": user_pw}


def choice_class(class_dict):
    print("\n학습할 클래스를 선택해주세요.")
    for idx, info in class_dict.items():
        print(f"[{idx + 1}] {info['class_name']}")

    while True:
        try:
            sel = int(input(">>> ").strip()) - 1
            if sel in class_dict:
                print(f"[{class_dict[sel]['class_name']}]를 선택하셨습니다.\n")
                return sel
            print("목록에 있는 번호를 입력해 주세요.")
        except ValueError:
            print("숫자만 입력해 주세요.")


def choice_set(sets_dict):
    print("\n학습할 세트를 선택해주세요.")
    for idx, info in sets_dict.items():
        card_info = f" | {info['card_num']}" if info.get('card_num') else ""
        print(f"[{idx + 1}] {info['title']}{card_info}")

    while True:
        try:
            sel = int(input(">>> ").strip()) - 1
            if sel in sets_dict:
                print(f"[{sets_dict[sel]['title']}] 를 선택하셨습니다.\n")
                return sel
            print("목록에 있는 번호를 입력해 주세요.")
        except ValueError:
            print("숫자만 입력해 주세요.")


def chd_wh():
    print("\n학습 유형을 선택해주세요.")
    modes = {1: "암기학습", 2: "리콜학습", 3: "스펠학습", 4: "테스트학습"}
    for number, name in modes.items():
        print(f"[{number}] {name}")

    while True:
        try:
            sel = int(input(">>> ").strip())
            if sel in modes:
                print(f"{sel}번 {modes[sel]}을 선택하셨습니다.\n")
                return sel
            print("1~4 번호 중 하나를 입력해 주세요.")
        except ValueError:
            print("숫자만 입력해 주세요.")


def word_get(driver, num_d=None):
    print("\n[단어 추출 진행 중...] 페이지 로딩 대기...")
    time.sleep(2.5)

    try:
        modals = driver.find_elements(
            By.CSS_SELECTOR,
            ".modal .btn-close, .modal .close, #alertModal .btn, .modal-footer .btn",
        )
        for modal in modals:
            if modal.is_displayed():
                driver.execute_script("arguments[0].click();", modal)
                time.sleep(0.5)
    except Exception:
        pass

    da_e, da_k = [], []
    page_source = driver.page_source

    try:
        front_matches = re.findall(
            r'["\']?(?:front_word|front|word)["\']?\s*:\s*["\']([^"\']+)["\']',
            page_source,
        )
        mean_matches = re.findall(
            r'["\']?(?:mean_word|mean|kor)["\']?\s*:\s*["\']([^"\']+)["\']',
            page_source,
        )
        if front_matches and len(front_matches) == len(mean_matches):
            da_e, da_k = front_matches, mean_matches
            print("-> [성공] 페이지 데이터에서 단어 추출 완료")
    except Exception:
        pass

    if not da_e:
        soup = BeautifulSoup(page_source, "html.parser")
        items = soup.select(
            ".card-item, .wb-card, .cc-table-row, tr[data-idx], .card-box, .set-detail-card"
        )
        for item in items:
            f_elem = item.select_one(
                ".front-word, .card-header, .cc-table-word, .text-en, .card-txt, .text-normal, .front, .word"
            )
            b_elem = item.select_one(
                ".back-word, .card-body, .cc-table-mean, .text-ko, .card-mean, .back, .mean"
            )
            eng = f_elem.get_text(strip=True) if f_elem else ""
            kor = b_elem.get_text(strip=True) if b_elem else ""
            if eng and kor:
                da_e.append(eng)
                da_k.append(kor)

        if da_e:
            print("-> [성공] DOM 파싱으로 단어 추출 완료")

    da_k = [re.sub(r'\[.*?\]\s*', '', value).strip() for value in da_k]
    num_total = len(da_e)
    da_kn = [str(i + 1) for i in range(num_total)]

    if num_total > 0:
        print(f"-> 총 {num_total}개 단어 데이터 로드 완료!\n")
    else:
        print(f"[진단 정보] 현재 URL: {driver.current_url}")
        print(f"[진단 정보] 페이지 제목: {driver.title}")

    return da_e, da_k, da_kn, da_k, da_k, da_e
