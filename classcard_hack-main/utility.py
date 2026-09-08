import re
import time
from getpass import getpass

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
        card_info = f" | {info['card_num']}" if info.get("card_num") else ""
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


def _element_text(element):
    """표시 여부와 관계없이 DOM 요소의 텍스트를 안전하게 읽는다."""
    if element is None:
        return ""

    text = (element.text or "").strip()
    if text:
        return text

    try:
        return (element.get_attribute("textContent") or "").strip()
    except Exception:
        return ""


def _find_first(root, selectors):
    for by, selector in selectors:
        try:
            element = root.find_element(by, selector)
            if _element_text(element):
                return element
        except Exception:
            continue
    return None


def _normalize_meaning(value):
    value = (value or "").strip()
    value = re.sub(r"\[.*?\]\s*", "", value)
    return value.strip()


def _meaning_variants(value):
    lines = [_normalize_meaning(line) for line in (value or "").splitlines()]
    lines = [line for line in lines if line]

    if not lines:
        return "", "", "", ""

    original = "\n".join(lines)
    comma = ", ".join(lines)
    spaced = " ".join(lines)

    pos_pattern = r"\b(?:명|동|형|부)\.\s*"
    edited = [re.sub(pos_pattern, "", line).strip() for line in lines]
    edited = ", ".join(line for line in edited if line)

    return original, comma, spaced, edited


def _extract_from_rendered_dom(driver):
    """현재 렌더링된 카드 목록 DOM에서 앞면/뜻을 직접 읽는다."""
    wait = WebDriverWait(driver, 12)

    try:
        wait.until(EC.presence_of_element_located((By.ID, "tab_set_all")))
    except Exception:
        return []

    # 기존 공개 구현에서 사용하던 #tab_set_all 카드 구조를 우선 사용한다.
    row_selectors = [
        (By.XPATH, "//*[@id='tab_set_all']/div[2]/div"),
        (By.CSS_SELECTOR, "#tab_set_all .flip-card"),
        (By.CSS_SELECTOR, "#tab_set_all .card-item"),
        (By.CSS_SELECTOR, "#tab_set_all .set-detail-card"),
    ]

    rows = []
    for by, selector in row_selectors:
        try:
            found = driver.find_elements(by, selector)
            if found:
                rows = found
                break
        except Exception:
            continue

    pairs = []
    seen = set()

    front_selectors = [
        (By.XPATH, ".//div[4]/div[1]/div[1]/div/div"),
        (By.CSS_SELECTOR, ".front-word"),
        (By.CSS_SELECTOR, ".cc-table-word"),
        (By.CSS_SELECTOR, ".text-en"),
        (By.CSS_SELECTOR, ".front"),
        (By.CSS_SELECTOR, ".word"),
    ]
    back_selectors = [
        (By.XPATH, ".//div[4]/div[2]/div[1]/div/div"),
        (By.CSS_SELECTOR, ".back-word"),
        (By.CSS_SELECTOR, ".cc-table-mean"),
        (By.CSS_SELECTOR, ".text-ko"),
        (By.CSS_SELECTOR, ".back"),
        (By.CSS_SELECTOR, ".mean"),
    ]

    for row in rows:
        front = _find_first(row, front_selectors)
        back = _find_first(row, back_selectors)

        eng = _element_text(front)
        kor = _element_text(back)

        if not eng or not kor:
            continue

        key = (eng, kor)
        if key in seen:
            continue
        seen.add(key)

        audio = ""
        try:
            audio_elements = row.find_elements(By.CSS_SELECTOR, "[data-src]")
            for audio_element in audio_elements:
                src = (audio_element.get_attribute("data-src") or "").strip()
                if src:
                    audio = src
                    break
        except Exception:
            pass

        pairs.append((eng, kor, audio))

    return pairs


def _extract_from_html(page_source):
    """렌더링 DOM 추출이 실패할 때 사용하는 보조 HTML 파서."""
    pairs = []
    seen = set()
    soup = BeautifulSoup(page_source, "html.parser")

    items = soup.select(
        "#tab_set_all > div:nth-of-type(2) > div, "
        ".card-item, .wb-card, .cc-table-row, tr[data-idx], "
        ".card-box, .set-detail-card, .flip-card"
    )

    front_selectors = [
        ".front-word", ".cc-table-word", ".text-en", ".card-txt",
        ".text-normal", ".front", ".word"
    ]
    back_selectors = [
        ".back-word", ".cc-table-mean", ".text-ko", ".card-mean",
        ".back", ".mean"
    ]

    for item in items:
        front = next((item.select_one(sel) for sel in front_selectors if item.select_one(sel)), None)
        back = next((item.select_one(sel) for sel in back_selectors if item.select_one(sel)), None)

        eng = front.get_text("\n", strip=True) if front else ""
        kor = back.get_text("\n", strip=True) if back else ""

        if eng and kor and (eng, kor) not in seen:
            seen.add((eng, kor))
            pairs.append((eng, kor, ""))

    return pairs


def word_get(driver, num_d=None):
    print("\n[단어 추출 진행 중...] 카드 목록을 확인합니다...")

    try:
        modals = driver.find_elements(
            By.CSS_SELECTOR,
            ".modal .btn-close, .modal .close, #alertModal .btn, .modal-footer .btn",
        )
        for modal in modals:
            if modal.is_displayed():
                modal.click()
                time.sleep(0.2)
    except Exception:
        pass

    pairs = _extract_from_rendered_dom(driver)
    source = "렌더링된 카드 DOM"

    if not pairs:
        pairs = _extract_from_html(driver.page_source)
        source = "HTML 파서"

    # 최후의 보조 수단: 페이지에 직렬화된 일반 front/mean 쌍이 있을 경우만 읽는다.
    if not pairs:
        page_source = driver.page_source
        front_matches = re.findall(
            r'["\']?(?:front_word|front)["\']?\s*:\s*["\']([^"\']+)["\']',
            page_source,
        )
        mean_matches = re.findall(
            r'["\']?(?:mean_word|mean)["\']?\s*:\s*["\']([^"\']+)["\']',
            page_source,
        )
        if front_matches and len(front_matches) == len(mean_matches):
            pairs = list(zip(front_matches, mean_matches, [""] * len(front_matches)))
            source = "페이지 직렬화 데이터"

    if num_d is not None and num_d > 0 and len(pairs) > num_d:
        pairs = pairs[:num_d]

    da_e = []
    da_k = []
    da_kn = []
    da_kyn = []
    da_ked = []
    da_sd = []

    for eng, kor, audio in pairs:
        eng = (eng or "").strip()
        original, comma, spaced, edited = _meaning_variants(kor)

        if not eng or not original:
            continue

        da_e.append(eng)
        da_k.append(original)
        da_kn.append(comma)
        da_kyn.append(spaced)
        da_ked.append(edited)
        da_sd.append(audio)

    if da_e:
        print(f"-> [성공] {source}에서 총 {len(da_e)}개 단어를 읽었습니다.\n")
    else:
        print("[오류] 카드 단어를 찾지 못했습니다.")
        print(f"[진단 정보] 현재 URL: {driver.current_url}")
        print(f"[진단 정보] 페이지 제목: {driver.title}")
        try:
            tab_count = len(driver.find_elements(By.ID, "tab_set_all"))
            row_count = len(driver.find_elements(By.XPATH, "//*[@id='tab_set_all']/div[2]/div"))
            print(f"[진단 정보] tab_set_all={tab_count}, 후보 카드 행={row_count}")
        except Exception:
            pass

    return da_e, da_k, da_kn, da_kyn, da_ked, da_sd
