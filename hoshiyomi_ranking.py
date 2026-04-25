#!/usr/bin/env python3
import math
from datetime import date

TYPES = {
    1:  {"name": "フレイムドラゴン",   "jp": "炎の龍",    "attr": "火"},
    2:  {"name": "アビスマーメイド",    "jp": "深海の人魚", "attr": "水"},
    3:  {"name": "サンダーエンジェル",  "jp": "雷の天使",   "attr": "風・雷"},
    4:  {"name": "グリーンスピリット",  "jp": "森の精霊",   "attr": "大地・木"},
    5:  {"name": "ルナウィッチ",        "jp": "月の魔女",   "attr": "闇・月"},
    6:  {"name": "ソーラーヒーロー",    "jp": "太陽の勇者", "attr": "光・火"},
    7:  {"name": "ストーンジャイアント","jp": "山の巨人",   "attr": "大地・岩"},
    8:  {"name": "テンペストイーグル",  "jp": "嵐の鷲",    "attr": "風・空"},
    9:  {"name": "ブロッサムゴッデス",  "jp": "花の女神",   "attr": "花・光"},
    10: {"name": "フロストドラゴン",    "jp": "氷の龍",    "attr": "氷・水"},
    11: {"name": "アースデーモン",      "jp": "大地の魔神", "attr": "大地・火"},
    12: {"name": "スターセージ",        "jp": "星の賢者",   "attr": "星・宇宙"},
}

ATTR_LIST = ['火', '水', '風', '大地', '闇・月', '光', '花', '氷', '星']

ATTR_TYPES = {
    '火':    [1, 6, 11],
    '水':    [2, 10],
    '風':    [3, 8],
    '大地':  [4, 7, 11],
    '闇・月':[5],
    '光':    [6, 9],
    '花':    [9],
    '氷':    [10],
    '星':    [12],
}

DOW_BONUS = {
    0: {"attr": "星",   "label": "神秘と宇宙の力が満ちる日曜"},
    1: {"attr": "大地", "label": "地の力で土台が固まる月曜"},
    2: {"attr": "火",   "label": "炎の意志が燃え上がる火曜"},
    3: {"attr": "水",   "label": "水の流れが縁を運ぶ水曜"},
    4: {"attr": "大地", "label": "大地の生命力が成長を促す木曜"},
    5: {"attr": "光",   "label": "光の祝福が降り注ぐ金曜"},
    6: {"attr": "風",   "label": "自由な風が新展開を運ぶ土曜"},
}

DOW_JP = ["日", "月", "火", "水", "木", "金", "土"]

LUCKY = [
    '赤いアイテム', 'カフェでの会話', 'ピンクのハンカチ', '手書きのメモ',
    '夕暮れの散歩', '手帳', '青色のペン', '朝のルーティン', 'コーヒーの香り',
    '整理された机', '黄色いもの', '神社参拝', '丸いコイン', '招き猫',
    '財布の整理', '星空観察', '深呼吸', '白いもの', '好きな音楽', '感謝の言葉',
]


def get_lucky_attr(d: date) -> str:
    s = d.year * 10000 + d.month * 100 + d.day
    return ATTR_LIST[s % len(ATTR_LIST)]


def get_dow_attr(d: date) -> dict:
    js_day = (d.weekday() + 1) % 7  # JS getDay(): 0=Sun, Python weekday(): 0=Mon
    return DOW_BONUS[js_day]


def has_bonus(tid: int, attr: str) -> bool:
    return tid in ATTR_TYPES.get(attr, [])


def get_ranking(th: int, d: date) -> list:
    date_seed = d.year * 10000 + d.month * 100 + d.day
    la = get_lucky_attr(d)
    da = get_dow_attr(d)["attr"]
    scores = []
    for i in range(1, 13):
        s = (date_seed * 31 + th * 7919 + i * 1013) & 0x7fffffff
        # JS uses IEEE 754 double for arithmetic; product ~6.9e17 exceeds 2^53
        # so precision is lost. Replicate with float() before masking.
        s = int(float(s) * 1103515245 + 12345) & 0x7fffffff
        s = int(float(s) * 1103515245 + 12345) & 0x7fffffff
        base = s % 60 + 20
        if has_bonus(i, da):
            base += 12
        if has_bonus(i, la):
            base += 15
        scores.append({"tid": i, "score": base})
    scores.sort(key=lambda x: (-x["score"], x["tid"]))
    return [s["tid"] for s in scores]


def get_score(rank: int) -> int:
    return round(95 - (rank - 1) * 6 + math.sin(rank) * 3)


def get_lucky_item(tid: int, th: int) -> str:
    return LUCKY[(tid * 3 + th * 7) % len(LUCKY)]


def main():
    d = date.today()
    th = 3  # 総合運

    js_day = (d.weekday() + 1) % 7
    dow_jp = DOW_JP[js_day]
    lucky_attr = get_lucky_attr(d)
    dow_info = get_dow_attr(d)
    ranking = get_ranking(th, d)

    print("=" * 52)
    print(f"  星詠み 総合運ランキング")
    print(f"  {d.year}年{d.month}月{d.day}日（{dow_jp}曜日）")
    print("=" * 52)
    print(f"  ラッキー属性    : {lucky_attr}")
    print(f"  曜日ボーナス属性: {dow_info['attr']}（{dow_info['label']}）")
    print("=" * 52)
    print()

    medal = ["🥇", "🥈", "🥉"]
    for i, tid in enumerate(ranking[:3]):
        t = TYPES[tid]
        score = get_score(i + 1)
        lucky_item = get_lucky_item(tid, th)
        print(f"  {medal[i]} 第{i + 1}位: {t['name']}（{t['jp']}）")
        print(f"       属性          : {t['attr']}")
        print(f"       運気スコア    : {score}点")
        print(f"       ラッキーアイテム: {lucky_item}")
        print()


if __name__ == "__main__":
    main()
