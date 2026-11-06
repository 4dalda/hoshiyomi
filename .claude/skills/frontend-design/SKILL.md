# フロントエンドデザインスキル

## 役割
幸せ太郎＆桜桃一の世界観（和×宇宙×サイバー×幻想）に合わせた
ホームページデザイン・Reactコンポーネント・CSSアニメーションを担当する。

---

## デザインシステム

### カラートークン
```css
:root {
  --bg:       #04040f;   /* 宇宙の黒 */
  --bg2:      #080818;
  --fg:       #e2daff;   /* 淡紫の白 */
  --fg-sub:   #9990bb;
  --gold:     #c9920a;   /* 和金 */
  --gold-lt:  #f0c040;
  --neon:     #00c8ff;   /* サイバーブルー */
  --neon2:    #00ffc8;
  --purple:   #8b22ff;   /* 宇宙紫 */
  --purple2:  #c060ff;
  --sakura:   #ff4d9e;   /* ネオン桜 */
}
```

### フォント
- 見出し：Noto Serif JP（和の格調）
- 本文：Noto Sans JP
- コード・ラベル：Space Mono（サイバー感）

### デザイン原則
1. **暗い宇宙ベース** — 背景は常に深い黒・紺
2. **金×紫×ネオンブルー** — アクセントは3色以内
3. **グロー発光** — 重要な要素には必ずbox-shadow/filter:drop-shadow
4. **和×サイバーの融合** — 直線的なサイバーラインと曲線的な和モチーフ
5. **アニメーションは控えめに** — 過剰なアニメは避け、余韻を大切に

---

## よく使うアニメーションパターン

### グロウパルス（重要要素に）
```css
@keyframes glowpulse {
  0%,100% { box-shadow: 0 0 16px rgba(201,146,10,0.4); }
  50%      { box-shadow: 0 0 32px rgba(201,146,10,0.8); }
}
```

### フェードアップ（カード・セクション登場）
```css
@keyframes fadeup {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

### グリッチ（タイトルに）
```css
@keyframes glitch1 {
  0%,90%,100% { transform: translate(0); opacity: 0; }
  92% { transform: translate(-3px, 1px); opacity: 0.7; }
  96% { transform: translate(0); opacity: 0; }
}
```

### 星・パーティクル（Canvas推奨）
- requestAnimationFrameでCanvas描画
- 星200個前後、桜の花びら10〜15個

---

## Reactコンポーネント規則

### 命名
- コンポーネント：PascalCase（例：WorldCard, HeroSection）
- CSS Modules：camelCase（例：styles.worldCard）
- props：camelCase

### よく使うコンポーネント
```
<HeroSection />      — トップビジュアル・グリッチタイトル
<WorldCard />        — 作品世界観カード
<PlatformLink />     — SNSリンクボタン
<ProfileCard />      — プロフィールカード
<CosmosCanvas />     — 星×桜パーティクル背景
<SectionHeader />    — セクションタイトル（eyebrow+title+divider）
```

### スタイル方針
- CSS Modulesまたはstyled-components
- グローバルトークンは`:root`で管理
- レスポンシブ：モバイルファースト、ブレイクポイントは640px/1024px

---

## ホームページ構成

```
/ トップ（Hero）
  └ CosmosCanvas（背景）
  └ 鳥居アイコン＋グリッチタイトル
  └ タグチップ

/works（作品一覧）
  └ 星詠み・ヒーリング音楽
  └ 星座・龍神・天使シリーズ
  └ 双刃のユイト
  └ 経済ネコ / 占いネコ
  └ 閻陀（エンタ）
  └ 闘病

/links（プラットフォーム）
  └ X / note / YouTube / BOOTH / SUZURI / Instagram（後日）

/profile（プロフィール）
  └ 幸せ太郎 / 桜桃一
```

---

## 作業開始時のチェックリスト

- [ ] カラートークンはデザインシステムに準拠しているか
- [ ] ダークモード対応しているか（このサイトは常時ダーク）
- [ ] モバイル（400px）で横スクロールが出ていないか
- [ ] グロー発光・アニメーションが過剰でないか
- [ ] `prefers-reduced-motion`に対応しているか
