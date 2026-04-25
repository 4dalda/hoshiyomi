#!/usr/bin/env python3
import json
import math
from datetime import date

import anthropic

TYPES = {
    1:  {"name": "フレイムドラゴン",    "jp": "炎の龍",    "attr": "火",
         "personality": "情熱的で行動力抜群。思い立ったら即行動。後先より今を生きる、本能のまま突き進む存在。",
         "strength": "リーダーシップ、突破力、カリスマ性",
         "weakness": "飽きっぽい、後先考えない、カッとなりやすい",
         "gag": "全力疾走したけどゴール忘れてた系。財布を忘れて颯爽と出かけるタイプ。"},
    2:  {"name": "アビスマーメイド",    "jp": "深海の人魚", "attr": "水",
         "personality": "感受性豊か、ミステリアス。独自の世界観を持ち、誰も気づかない深さで物事を感じ取る。",
         "strength": "共感力、直感力、芸術センス",
         "weakness": "傷つきやすい、気分のムラが激しい、説明が下手",
         "gag": "感動して泣いてたら理由を忘れてた系。LINEの返信が3日後になりがち。"},
    3:  {"name": "サンダーエンジェル",  "jp": "雷の天使",   "attr": "風・雷",
         "personality": "正義感が強く、白黒はっきりつけたい完璧主義。誠実さで周囲の信頼を勝ち取る存在。",
         "strength": "誠実さ、分析力、揺るぎない信頼感",
         "weakness": "融通が利かない、自他に厳しすぎる、グレーゾーンが苦手",
         "gag": "正論を言いすぎて場の空気を凍らせる系。謝り方が論文みたいになりがち。"},
    4:  {"name": "グリーンスピリット",  "jp": "森の精霊",   "attr": "大地・木",
         "personality": "おおらかでマイペース。自然体で周りをほっとさせる癒しの存在。急がず、確かに。",
         "strength": "包容力、粘り強さ、安定感",
         "weakness": "優柔不断、変化が苦手、のんびりしすぎ",
         "gag": "返事はするけど動かない系。「あとでやる」が口癖で気づいたら3ヶ月経ってる。"},
    5:  {"name": "ルナウィッチ",        "jp": "月の魔女",   "attr": "闇・月",
         "personality": "知的でクール。観察力が鋭く、腹の中では全部お見通し。秘密の多い神秘的な存在。",
         "strength": "洞察力、戦略思考、冷静な判断力",
         "weakness": "皮肉っぽい、本音を言わない、距離を置きすぎる",
         "gag": "全部わかってるのに言わない系。心の中のツッコミが秒速だが口は閉じてる。"},
    6:  {"name": "ソーラーヒーロー",    "jp": "太陽の勇者", "attr": "光・火",
         "personality": "明るく無邪気、みんなのムードメーカー。どんな場でも太陽のように輝き、人を巻き込む。",
         "strength": "行動力、明るさ、人を巻き込む力",
         "weakness": "考えが浅い、空気読めない、テンションが空回りする",
         "gag": "場の空気を読まずに全力でボケる系。葬式でも明るい話題を探してしまう。"},
    7:  {"name": "ストーンジャイアント", "jp": "山の巨人",   "attr": "大地・岩",
         "personality": "無口だが頼れる存在。動じない大黒柱タイプ。いざという時こそ真価を発揮する。",
         "strength": "忍耐力、安定感、いざという時の底力",
         "weakness": "口下手、感情表現が苦手、頑固すぎる",
         "gag": "大事なことを一言も言わない系。好きな人への告白が「…うん」だけになりがち。"},
    8:  {"name": "テンペストイーグル",  "jp": "嵐の鷲",    "attr": "風・空",
         "personality": "自由奔放で好奇心旺盛。どこにでも飛んでいく冒険者。常に新しい風を運んでくる。",
         "strength": "適応力、発想力、スピード感",
         "weakness": "飽きっぽい、約束を忘れる、落ち着きがない",
         "gag": "風のように去っていく系。「ちょっと待って」と言いながら戻ってこない。"},
    9:  {"name": "ブロッサムゴッデス",  "jp": "花の女神",   "attr": "花・光",
         "personality": "社交的で愛され上手。人の心をほぐす天才。その笑顔が場の全てを変える力を持つ。",
         "strength": "コミュニケーション力、愛嬌、場の調整力",
         "weakness": "八方美人、断れない、流されやすい",
         "gag": "全員に「あなたが一番好き」と思わせてしまう系。"},
    10: {"name": "フロストドラゴン",    "jp": "氷の龍",    "attr": "氷・水",
         "personality": "クールで知的。プライドが高い完璧主義者。表面は冷静だが、内心では誰より情熱的。",
         "strength": "集中力、審美眼、高い基準を維持する力",
         "weakness": "人を寄せ付けない、プライドが邪魔をする、負けを認めない",
         "gag": "絶対に「わからない」と言わない系。迷子になっても地図を見ない。"},
    11: {"name": "アースデーモン",      "jp": "大地の魔神", "attr": "大地・火",
         "personality": "エネルギッシュで欲望に正直。やりたいことを全力でやる。本能のままに生きる圧倒的な存在感。",
         "strength": "実行力、バイタリティ、本能的な強さ",
         "weakness": "自己中になりやすい、欲張りすぎる、空腹時は別人",
         "gag": "お腹が空くと人格が変わる系。重要な会議の前に必ずお腹が鳴る。"},
    12: {"name": "スターセージ",        "jp": "星の賢者",   "attr": "星・宇宙",
         "personality": "哲学的でロマンチスト。宇宙レベルで物事を考える思想家。常人には見えない真実を見通す。",
         "strength": "創造力、大局観、独創的なアイデア",
         "weakness": "現実離れしてる、説明がわかりにくい、日常のことが苦手",
         "gag": "スケールが大きすぎて日常会話が噛み合わない系。コンビニで何を買うか30分悩む。"},
}

ATTR_LIST = ['火', '水', '風', '大地', '闇・月', '光', '花', '氷', '星']

ATTR_TYPES = {
    '火':     [1, 6, 11],
    '水':     [2, 10],
    '風':     [3, 8],
    '大地':   [4, 7, 11],
    '闇・月': [5],
    '光':     [6, 9],
    '花':     [9],
    '氷':     [10],
    '星':     [12],
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

FORTUNE_PHRASES = {
    3: [
        lambda t: f'{t["jp"]}よ、今日は星々が最大の加護を与える日。全てが流れるように進み、周囲を自然と引き寄せる輝きが宿る。',
        lambda t: f'{t["jp"]}の今日は内なる声に耳を傾けよ。直感が冴え渡り、その感覚に従うことが最善の結果をもたらす。',
        lambda t: f'{t["jp"]}にとって今日は準備と休息の日。深いところで大きな力が蓄えられている。',
        lambda t: f'{t["jp"]}の今日は人との縁が全ての鍵。感謝を言葉にすることで運気が好転する。',
        lambda t: f'{t["jp"]}よ、今日は自分自身を信じよ。これまで歩んできた道は間違っていない。堂々と前を向け。',
    ],
}

# ニャビゲーター4匹の口調定義
CHARACTERS = [
    {
        "name": "霞雲（むらくも）",
        "style": (
            "落ち着いた深みのある和風・古典的な口調。「じゃ」「おる」「知れ」などの文語・古語を自然に使う。"
            "静かな威厳と慈しみがある。1〜2文で完結させること。"
        ),
    },
    {
        "name": "ノヴァ",
        "style": (
            "ハイテンション・ツッコミ系のカジュアルな口調。「！！」多用、「マジで」「ヤバい」「じゃん」など若者言葉。"
            "テンポよく短く。対象タイプのあるある・弱みにもさらっと触れてOK。1〜2文で完結させること。"
        ),
    },
    {
        "name": "フレイヤ",
        "style": (
            "優しく包み込む癒し系の口調。語尾に「ゴロゴロ…」を入れる（猫キャラ）。"
            "穏やかで温かく読者が安心できる言葉。「♪」も使ってよい。1〜2文で完結させること。"
        ),
    },
    {
        "name": "グレイス",
        "style": (
            "クールでツンデレな口調。「…」で始めることが多く、「別に心配してるわけじゃないけど」"
            "「嫌いじゃないけど」など本音を隠しながら温かさが滲み出る。1〜2文で完結させること。"
        ),
    },
]

# システムプロンプト（キャッシュ対象）
_SYSTEM_PROMPT = (
    "あなたは星詠みサイト「星詠み」に登場する4人のニャビゲーターです。\n"
    "それぞれ異なる口調・個性を持ち、今日の総合運1位のタイプに対してコメントします。\n\n"
    "## 出力形式\n"
    "以下のJSONのみを返してください。コードブロック・説明文は不要です。\n"
    '{"霞雲（むらくも）": "コメント本文", "ノヴァ": "コメント本文", '
    '"フレイヤ": "コメント本文", "グレイス": "コメント本文"}\n\n'
    "## キャラクター口調\n"
    + "\n".join(f"- {c['name']}: {c['style']}" for c in CHARACTERS)
    + "\n\n## 注意\n"
    "毎回少しずつ表現を変えて新鮮なコメントにすること。\n"
    "同じタイプでも日によって違う側面にフォーカスしてよい。"
)


# ============================================================
# ランキング計算
# ============================================================

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


def get_fortune(tid: int, th: int) -> str:
    phrases = FORTUNE_PHRASES[th]
    return phrases[(tid + th) % len(phrases)](TYPES[tid])


# ============================================================
# Claude API: キャラクターコメント生成
# ============================================================

def _make_client() -> anthropic.Anthropic:
    """Return an Anthropic client, falling back to session token when no API key is set."""
    import os
    if os.environ.get("ANTHROPIC_API_KEY"):
        return anthropic.Anthropic()
    token_file = os.environ.get("CLAUDE_SESSION_INGRESS_TOKEN_FILE")
    if token_file:
        token = open(token_file).read().strip()
        return anthropic.Anthropic(auth_token=token)
    return anthropic.Anthropic()  # will raise if neither is available


def generate_character_comments(tid: int, d: date) -> dict:
    t = TYPES[tid]
    client = _make_client()

    user_content = (
        f"今日（{d.year}年{d.month}月{d.day}日）の総合運1位タイプ:\n"
        f"名前: {t['name']}（{t['jp']}）\n"
        f"属性: {t['attr']}\n"
        f"性格: {t['personality']}\n"
        f"強み: {t['strength']}\n"
        f"弱み: {t['weakness']}\n"
        f"あるある: {t['gag']}\n\n"
        "4人それぞれのコメントをJSON形式で出力してください。"
    )

    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=[{"type": "text", "text": _SYSTEM_PROMPT,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        response = stream.get_final_message()

    for block in response.content:
        if block.type == "text":
            text = block.text.strip()
            # モデルがコードフェンスで囲んだ場合に対応
            if text.startswith("```"):
                lines = text.splitlines()
                text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
            return json.loads(text)

    return {c["name"]: "（コメント取得失敗）" for c in CHARACTERS}


# ============================================================
# note用テキスト生成
# ============================================================

def generate_note_text(d: date) -> str:
    th = 3
    js_day = (d.weekday() + 1) % 7
    dow_jp = DOW_JP[js_day]
    lucky_attr = get_lucky_attr(d)
    dow_info = get_dow_attr(d)
    ranking = get_ranking(th, d)
    top3 = ranking[:3]
    first_tid = top3[0]

    print("  Claude APIでコメント生成中...", flush=True)
    comments = generate_character_comments(first_tid, d)

    lines = []

    # ヘッダー
    lines += [
        f"# ✨ 今日の星詠み｜{d.year}年{d.month}月{d.day}日（{dow_jp}）総合運ランキング",
        "",
        f"🗓 {d.year}年{d.month}月{d.day}日（{dow_jp}曜日）",
        f"🔮 ラッキー属性：**{lucky_attr}**",
        f"📅 曜日ボーナス属性：**{dow_info['attr']}**（{dow_info['label']}）",
        "",
        "---",
        "",
    ]

    # TOP 3
    lines += ["## 🏆 今日の総合運 TOP 3", ""]
    medal = ["🥇", "🥈", "🥉"]
    for rank_idx, tid in enumerate(top3):
        t = TYPES[tid]
        score = get_score(rank_idx + 1)
        lucky_item = get_lucky_item(tid, th)
        fortune_text = get_fortune(tid, th)
        lines += [
            f"### {medal[rank_idx]} 第{rank_idx + 1}位：{t['name']}（{t['jp']}）",
            f"- 属性：{t['attr']}",
            f"- 運気スコア：{score}点",
            f"- ラッキーアイテム：{lucky_item}",
            f"- 今日の運勢：{fortune_text}",
            "",
        ]

    lines += ["---", ""]

    # キャラクターコメント（1位のみ）
    first_t = TYPES[first_tid]
    lines += [
        f"## 💬 ニャビゲーターより｜{first_t['name']}（{first_t['jp']}）への一言",
        "",
    ]
    for c in CHARACTERS:
        name = c["name"]
        comment = comments.get(name, "（コメントなし）")
        lines += [
            f"**{name}より**",
            f"> {comment}",
            "",
        ]

    lines += [
        "---",
        "",
        "星詠みサイトでは、あなた自身の柱タイプや今日の詳細な運勢を確認できます。",
        "ぜひチェックしてみてください✨",
        "",
        "#星詠み #運勢 #占い #総合運 #今日のラッキー",
    ]

    return "\n".join(lines)


# ============================================================
# main
# ============================================================

def main():
    d = date.today()
    th = 3

    js_day = (d.weekday() + 1) % 7
    dow_jp = DOW_JP[js_day]
    lucky_attr = get_lucky_attr(d)
    dow_info = get_dow_attr(d)
    ranking = get_ranking(th, d)

    print("=" * 52)
    print("  星詠み 総合運ランキング")
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
        print(f"       属性            : {t['attr']}")
        print(f"       運気スコア      : {score}点")
        print(f"       ラッキーアイテム: {lucky_item}")
        print()

    print("note用テキストを生成します")
    note_text = generate_note_text(d)

    print()
    print("=" * 52)
    print("【note用テキスト】")
    print("=" * 52)
    print(note_text)

    filename = f"hoshiyomi_{d.strftime('%Y%m%d')}.md"
    filepath = f"/home/user/hoshiyomi/{filename}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(note_text)
    print()
    print(f"→ ファイル保存: {filename}")


if __name__ == "__main__":
    main()
