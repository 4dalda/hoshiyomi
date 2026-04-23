#!/usr/bin/env python3
"""星詠みChronicle 毎日ランキング結果からX投稿文を3パターン自動生成するスクリプト"""

import sys
from datetime import date

HASHTAGS = "詳しくはnoteで🌙 #星詠みChronicle #今日の運勢"
MAX_CHARS = 140

TYPE_NAMES = [
    "牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
    "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座",
]

CAT_NAMES = ["叢雲", "ノヴァ", "フレイヤ", "グレイス"]


def generate_pattern_a(overall_top: str, today: str) -> str:
    text = f"✨{today}の総合運No.1は【{overall_top}】！今日はあなたの星が輝く一日。運気を味方につけて、思い切った一歩を踏み出してみて。{HASHTAGS}"
    return text


def generate_pattern_b(cat: str, overall_top: str, love_top: str, work_top: str, today: str) -> str:
    if cat == "叢雲":
        text = (
            f"【{today}・叢雲より】本日の総合運筆頭は{overall_top}でございます。"
            f"恋愛は{love_top}、仕事は{work_top}が輝きを放っております。"
            f"皆様、どうぞ穏やかな一日をお過ごしくださいませ。{HASHTAGS}"
        )
    elif cat == "ノヴァ":
        text = (
            f"YO🔥{today}のランキング発表〜！"
            f"総合No.1は{overall_top}でSHOW！"
            f"恋愛は{love_top}、ワークは{work_top}がマジでアツいよ〜！"
            f"レッツゴー！{HASHTAGS}"
        )
    elif cat == "フレイヤ":
        text = (
            f"ニャー…🐾{today}のNo.1は{overall_top}だよ…ゴロゴロ。"
            f"恋愛は{love_top}ちゃん、お仕事は{work_top}ちゃんがいい感じ…。"
            f"みんな、ゆっくりいい日にしてね…ふわ〜。{HASHTAGS}"
        )
    elif cat == "グレイス":
        text = (
            f"…{today}の結果を教えてあげるわ。"
            f"総合1位は{overall_top}。恋愛は{love_top}、仕事は{work_top}。"
            f"…別に、参考にしてほしいとかじゃないけど。{HASHTAGS}"
        )
    else:
        text = generate_pattern_a(overall_top, today)
    return text


def generate_pattern_c(money_top: str, today: str) -> str:
    text = (
        f"💰{today}の金運No.1は【{money_top}】！"
        f"今日はお財布の紐をちょっとだけゆるめてみて。"
        f"良い出費が、さらなる豊かさを引き寄せるかも🌟 {HASHTAGS}"
    )
    return text


def check_length(label: str, text: str) -> str:
    length = len(text)
    warning = f" ⚠ {length}字（140字超過）" if length > MAX_CHARS else f"（{length}字）"
    return f"{label}{warning}\n{text}"


def prompt_select(prompt: str, choices: list[str]) -> str:
    print(prompt)
    for i, c in enumerate(choices, 1):
        print(f"  {i}. {c}")
    while True:
        raw = input("番号を入力: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return choices[int(raw) - 1]
        print("  → 正しい番号を入力してください。")


def prompt_type(prompt: str, allow_custom: bool = True) -> str:
    print(prompt)
    for i, t in enumerate(TYPE_NAMES, 1):
        print(f"  {i:>2}. {t}", end="   " if i % 4 != 0 else "\n")
    print()
    print("  0. その他（直接入力）" if allow_custom else "")
    while True:
        raw = input("番号または名前を入力: ").strip()
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= len(TYPE_NAMES):
                return TYPE_NAMES[n - 1]
            if n == 0 and allow_custom:
                return input("タイプ名を入力: ").strip()
        elif raw:
            return raw
        print("  → 入力してください。")


def main():
    today = date.today().strftime("%Y/%m/%d")
    print(f"\n星詠みChronicle X投稿文ジェネレーター  [{today}]")
    print("=" * 50)

    # 総合運ランキング入力
    print("\n【総合運ランキング 1〜12位を入力してください】")
    overall_ranking = []
    for rank in range(1, 13):
        t = prompt_type(f"\n{rank}位:", allow_custom=True)
        overall_ranking.append(t)

    # 各カテゴリ1位
    print("\n【各運勢の1位を入力してください】")
    love_top = prompt_type("\n恋愛運 1位:")
    work_top = prompt_type("\n仕事運 1位:")
    money_top = prompt_type("\n金運 1位:")

    # ナビゲーター猫選択
    print()
    cat = prompt_select("\n【ナビゲーター猫を選んでください】", CAT_NAMES)

    overall_top = overall_ranking[0]

    print("\n" + "=" * 50)
    print("■ 生成された投稿文")
    print("=" * 50)

    pattern_a = generate_pattern_a(overall_top, today)
    pattern_b = generate_pattern_b(cat, overall_top, love_top, work_top, today)
    pattern_c = generate_pattern_c(money_top, today)

    print("\n▼ パターンA：総合運1位シンプル版")
    print(check_length("", pattern_a))

    print("\n▼ パターンB：{cat}バージョン".format(cat=cat))
    print(check_length("", pattern_b))

    print("\n▼ パターンC：金運コラボ版")
    print(check_length("", pattern_c))

    print("\n" + "=" * 50)
    print("📋 総合運ランキング")
    for i, t in enumerate(overall_ranking, 1):
        print(f"  {i:>2}位: {t}")
    print(f"  恋愛運1位: {love_top}  仕事運1位: {work_top}  金運1位: {money_top}")
    print("=" * 50)


if __name__ == "__main__":
    main()
