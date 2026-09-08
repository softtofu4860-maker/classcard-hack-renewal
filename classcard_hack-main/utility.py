import re
import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_id():
    print("========================================")
    print("         CLASS CARD AUTO BOT            ")
    print("========================================")
    user_id = input("아이디를 입력하세요: ").strip()
    user_pw = input("비밀번호를 입력하세요: ").strip()
    return {"id": user_id, "pw": user_pw}

def choice_class(class_dict):
    print("\n학습할 클래스를 선택해주세요.")
    print("Ctrl + C 로 중지 등록")
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
    print("Ctrl + C 로 중지 등록")
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
    print("Ctrl + C 로 중지 등록")
    print("[1] 암기학습(매크로)")
    print("[2] 리콜학습(매크로)")
    print("[3] 스펠학습(매크로)")
    print("[4] 테스트학습(매크로)")
    
    modes = {1: "암기학습", 2: "리콜학습", 3: "스펠학습", 4: "테스트학습"}
    
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
    print(f"\n[단어 추출 진행 중...] 페이지 로딩 대기...")
    time.sleep(2.5)

    # 0단계: 팝업 / 모달창 차단 처리
    try:
        modals = driver.find_elements(By.CSS_SELECTOR, ".modal .btn-close, .modal .close, #alertModal .btn, .modal-footer .btn")
        for m in modals:
            if m.is_displayed():
                driver.execute_script("arguments[0].click();", m)
                time.sleep(0.5)
    except Exception:
        pass

    da_e, da_k = [], []

    # 1단계: HTML 스크립트 소스코드 내 JS 객체 Direct Regex 파싱 (가장 완벽함)
    page_source = driver.page_source
    try:
        # 클래스카드 데이터 전송용 패턴 탐색
        front_matches = re.findall(r'["\']?(?:front_word|front|word)["\']?\s*:\s*["\']([^"\']+)["\']', page_source)
        mean_matches = re.findall(r'["\']?(?:mean_word|mean|kor)["\']?\s*:\s*["\']([^"\']+)["\']', page_source)

        if len(front_matches) > 0 and len(front_matches) == len(mean_matches):
            da_e = front_matches
            da_k = mean_matches
            print("-> [성공 1단계] 스크립트 정규식 파싱으로 단어 추출 완료")
    except Exception:
        pass

    # 2단계: 브라우저 JS Runtime 변수 수집
    if not da_e:
        try:
            js_data = driver.execute_script("""
                var e = [], k = [];
                // 1) 전역 변수 탐색
                if (typeof card_data !== 'undefined' && Array.isArray(card_data)) {
                    card_data.forEach(function(c) {
                        if (c.front || c.front_word) e.push(c.front || c.front_word);
                        if (c.mean || c.mean_word) k.push(c.mean || c.mean_word);
                    });
                }
                // 2) DOM 기반 광범위 수집
                if (e.length === 0) {
                    var items = document.querySelectorAll('.card-item, .wb-card, .cc-table-row, tr[data-idx], .card-box, .set-detail-card, div[class*="card"]');
                    items.forEach(function(item) {
                        var eng = item.querySelector('.front-word, .card-header, .cc-table-word, .text-en, .card-txt, .front, .word, .text-normal')?.innerText.strip() || '';
                        var kor = item.querySelector('.back-word, .card-body, .cc-table-mean, .text-ko, .card-mean, .back, .mean')?.innerText.strip() || '';
                        if (eng && kor) { e.push(eng); k.push(kor); }
                    });
                }
                return [e, k];
            """)
            if js_data and len(js_data[0]) > 0:
                da_e, da_k = js_data[0], js_data[1]
                print("-> [성공 2단계] JS Runtime 객체 탐색으로 단어 추출 완료")
        except Exception:
            pass

    # 3단계: BeautifulSoup DOM 셀렉터 파싱
    if not da_e:
        soup = BeautifulSoup(page_source, "html.parser")
        items = soup.select(".card-item, .wb-card, .cc-table-row, tr[data-idx], .card-box, .set-detail-card")
        for item in items:
            f_elem = item.select_one(".front-word, .card-header, .cc-table-word, .text-en, .card-txt, .text-normal, .front, .word")
            b_elem = item.select_one(".back-word, .card-body, .cc-table-mean, .text-ko, .card-mean, .back, .mean")

            eng = f_elem.get_text(strip=True) if f_elem else ""
            kor = b_elem.get_text(strip=True) if b_elem else ""

            if eng and kor:
                da_e.append(eng)
                da_k.append(kor)

        if da_e:
            print("-> [성공 3단계] DOM 파싱으로 단어 추출 완료")

    # 특수문자 및 품사 정리
    da_k = [re.sub(r'\[.*?\]\s*', '', k).strip() for k in da_k]
    num_total = len(da_e)
    da_kn = [str(i + 1) for i in range(num_total)]

    if num_total > 0:
        print(f"-> 총 {num_total}개 단어 데이터 로드 완료!\n")
    else:
        print(f"[진단 정보] 현재 URL: {driver.current_url}")
        print(f"[진단 정보] 페이지 제목: {driver.title}")

    return da_e, da_k, da_kn, da_k, da_k, da_e