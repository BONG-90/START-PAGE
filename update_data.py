import json
import datetime
import requests
from bs4 import BeautifulSoup

def get_market_data():
    url = "https://finance.naver.com/sise/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        kospi = soup.select_one("#KOSPI_now").text.strip()
        kospi_chg = soup.select_one("#KOSPI_change").text.strip()
        
        kosdaq = soup.select_one("#KOSDAQ_now").text.strip()
        kosdaq_chg = soup.select_one("#KOSDAQ_change").text.strip()
        
        return [
            {"name": "코스피", "value": kospi, "chg": kospi_chg},
            {"name": "코스닥", "value": kosdaq, "chg": kosdaq_chg}
        ]
    except Exception as e:
        print("증시 크롤링 에러:", e)
        return [{"name": "증시 정보", "value": "네이버 증권 참고", "chg": ""}]

def main():
    # 한국 시간 기준 (UTC+9)
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    now_str = now.strftime("%Y.%m.%d %H:%M 기준")
    
    data = {
        "asOf": now_str,
        "market": get_market_data(),
        "ent": [
            "최신 연예 주요 뉴스는 아래 네이버/다음 연예 링크에서 실시간으로 확인해 주세요."
        ],
        "lol": [
            "최신 LCK 및 롤드컵 일정/경기 결과는 아래 LoL Esports 사이트를 참고하세요."
        ]
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
