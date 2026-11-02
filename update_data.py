import json, re, datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0"}
LAT, LON = 37.008, 127.280  # 안성

WCODE = {0: "맑음 ☀️", 1: "대체로 맑음 🌤", 2: "구름 조금 ⛅", 3: "흐림 ☁️",
         45: "안개 🌫", 48: "안개 🌫", 51: "이슬비 🌦", 53: "이슬비 🌦", 55: "이슬비 🌦",
         61: "비 🌧", 63: "비 🌧", 65: "강한 비 🌧", 71: "눈 ❄️", 73: "눈 ❄️", 75: "강한 눈 ❄️",
         80: "소나기 🌦", 81: "소나기 🌦", 82: "강한 소나기 ⛈", 95: "뇌우 ⛈"}

def get_weather():
    try:
        u = ("https://api.open-meteo.com/v1/forecast"
             f"?latitude={LAT}&longitude={LON}"
             "&current=temperature_2m,weather_code"
             "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
             "&timezone=Asia%2FSeoul&forecast_days=1")
        j = requests.get(u, headers=UA, timeout=15).json()
        c, d = j["current"], j["daily"]
        return {"temp": f'{round(c["temperature_2m"])}°C',
                "desc": WCODE.get(c["weather_code"], "날씨 정보"),
                "note": f'최저 {round(d["temperature_2m_min"][0])}° / 최고 {round(d["temperature_2m_max"][0])}° · 강수확률 {d["precipitation_probability_max"][0]}%'}
    except Exception as e:
        print("날씨 에러:", e)
        return None

def get_market():
    try:
        res = requests.get("https://finance.naver.com/sise/", headers=UA, timeout=15)
        res.encoding = "euc-kr"
        soup = BeautifulSoup(res.text, "html.parser")
        out = []
        for name, key in (("코스피", "KOSPI"), ("코스닥", "KOSDAQ")):
            val = soup.select_one(f"#{key}_now").text.strip()
            raw = soup.select_one(f"#{key}_change").text
            m = re.search(r"[+-]?\d+(?:\.\d+)?\s*%", raw)
            chg = m.group(0).replace(" ", "") if m else raw.strip()
            if m and chg[0] not in "+-":
                chg = ("-" if ("하락" in raw or "▼" in raw) else "+") + chg
            out.append({"name": name, "value": val, "chg": chg})
        return out
    except Exception as e:
        print("증시 에러:", e)
        return [{"name": "증시 정보", "value": "네이버 증권 참고", "chg": ""}]

def news(query, n=5, fallback="헤드라인을 가져오지 못했어요. 아래 링크를 확인해 주세요."):
    try:
        u = f"https://news.google.com/rss/search?q={quote(query)}+when:1d&hl=ko&gl=KR&ceid=KR:ko"
        root = ET.fromstring(requests.get(u, headers=UA, timeout=15).content)
        titles, seen = [], set()
        for it in root.iter("item"):
            t = (it.findtext("title") or "").strip()
            if t and t not in seen:
                seen.add(t); titles.append(t)
            if len(titles) >= n:
                break
        return titles or [fallback]
    except Exception as e:
        print("뉴스 에러:", query, e)
        return [fallback]

def main():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    data = {
        "asOf": now.strftime("%Y.%m.%d %H:%M 기준"),
        "weather": get_weather(),
        "market": get_market(),
        "ent": news("연예"),
        "lol": news("LCK OR 롤드컵 OR 리그오브레전드"),
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
