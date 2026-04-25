# hoshiyomi プロジェクト

## 自動コマンド

ユーザーが「今日の運勢」と入力したら、確認なしに即座に以下を実行すること：

```bash
python3 /home/user/hoshiyomi/hoshiyomi_ranking.py
```

実行後、生成された `hoshiyomi_YYYYMMDD.md` の内容をそのまま表示すること。

## プロジェクト概要

星詠みサイト（https://4dalda.github.io/hoshiyomi/）の総合運ランキングを自動計算し、
ニャビゲーター4匹のコメントをClaude APIで生成してnote用記事を出力するツール。

## ファイル構成

- `hoshiyomi_ranking.py` — メインスクリプト
- `requirements.txt` — 依存パッケージ（anthropic>=0.50.0）
- `hoshiyomi_YYYYMMDD.md` — 実行日ごとに生成されるnote用記事

## スクリプトの仕様

- テーマ: 総合運（theme=3）固定
- ランキング計算: サイトのJavaScript LCGロジックをPythonで再現（float()で倍精度演算を模倣）
- モデル: `claude-sonnet-4-5`
- キャラクター: 霞雲（むらくも）・ノヴァ・フレイヤ・グレイス
- 認証: `ANTHROPIC_API_KEY` 環境変数、なければ `CLAUDE_SESSION_INGRESS_TOKEN_FILE` にフォールバック
