"""Fortune calculation logic for 星詠みChronicle."""
from datetime import date, datetime
from fortune_data import ZODIAC_SIGNS, CHINESE_ZODIAC, LIFE_PATH, BLOOD_TYPE, TYPES


def get_zodiac(month: int, day: int) -> dict:
    boundaries = [
        (3, 21), (4, 20), (5, 21), (6, 21),
        (7, 23), (8, 23), (9, 23), (10, 23),
        (11, 22), (12, 22), (1, 20), (2, 19),
    ]
    for i, (m, d) in enumerate(boundaries):
        if (month == m and day >= d) or (month == m % 12 + 1 and day < boundaries[(i + 1) % 12][1]):
            # Aries starts at index 0 (3/21)
            pass

    # Simpler lookup
    sign_index = None
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        sign_index = 0   # 牡羊
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        sign_index = 1   # 牡牛
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        sign_index = 2   # 双子
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        sign_index = 3   # 蟹
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        sign_index = 4   # 獅子
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        sign_index = 5   # 乙女
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        sign_index = 6   # 天秤
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        sign_index = 7   # 蠍
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        sign_index = 8   # 射手
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        sign_index = 9   # 山羊
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        sign_index = 10  # 水瓶
    else:
        sign_index = 11  # 魚

    return {"index": sign_index, **ZODIAC_SIGNS[sign_index]}


def get_chinese_zodiac(year: int) -> dict:
    # 2020 is the year of the Rat (子)
    idx = (year - 2020) % 12
    if idx < 0:
        idx += 12
    return {"index": idx, **CHINESE_ZODIAC[idx]}


def get_life_path(year: int, month: int, day: int) -> dict:
    digits = [int(c) for c in f"{year}{month:02d}{day:02d}"]
    total = sum(digits)
    while total > 9 and total not in (11, 22):
        total = sum(int(c) for c in str(total))
    return {"number": total, **LIFE_PATH.get(total, LIFE_PATH[9])}


def determine_type(zodiac_idx: int, chinese_idx: int, life_path_num: int, blood: str) -> int:
    scores = {i: 0 for i in range(1, 13)}

    for type_id, tdata in TYPES.items():
        # Zodiac affinity: +3 for primary match
        if zodiac_idx in tdata["zodiac_affinity"]:
            pos = tdata["zodiac_affinity"].index(zodiac_idx)
            scores[type_id] += 3 - pos   # +3, +2, +1

        # Chinese zodiac affinity
        if chinese_idx in tdata["chinese_affinity"]:
            pos = tdata["chinese_affinity"].index(chinese_idx)
            scores[type_id] += 3 - pos

        # Life path affinity
        if life_path_num in tdata["lifepath_affinity"]:
            pos = tdata["lifepath_affinity"].index(life_path_num)
            scores[type_id] += 3 - pos

        # Blood type affinity
        if blood in tdata["blood_affinity"]:
            pos = tdata["blood_affinity"].index(blood)
            scores[type_id] += 2 - pos

    best = max(scores, key=lambda k: (scores[k], k))
    return best


def calculate_fortune_scores(type_id: int, year: int, month: int, day: int) -> dict:
    base = TYPES[type_id]["fortune_base"].copy()
    # Add deterministic variation based on birth date
    seed = (year * 31 + month * 7 + day * 13) % 20 - 10
    result = {}
    adjustments = {"総合": seed % 8, "恋愛": (seed * 3) % 10, "金運": (seed * 7) % 9, "仕事": (seed * 5) % 8}
    for cat, base_score in base.items():
        score = min(100, max(40, base_score + adjustments[cat]))
        result[cat] = score
    return result


def calculate_all(year: int, month: int, day: int, blood: str, navigator: str, name: str) -> dict:
    zodiac   = get_zodiac(month, day)
    chinese  = get_chinese_zodiac(year)
    lp       = get_life_path(year, month, day)
    blood_info = {"type": blood, **BLOOD_TYPE[blood]}
    type_id  = determine_type(zodiac["index"], chinese["index"], lp["number"], blood)
    type_data = TYPES[type_id]
    scores   = calculate_fortune_scores(type_id, year, month, day)

    today = date.today()
    month_str = f"{today.year}年{today.month}月"

    return {
        "name":       name,
        "birth":      f"{year}年{month}月{day}日",
        "navigator":  navigator,
        "month_str":  month_str,
        "zodiac":     zodiac,
        "chinese":    chinese,
        "life_path":  lp,
        "blood":      blood_info,
        "type_id":    type_id,
        "type":       type_data,
        "scores":     scores,
    }
