# CLAUDE.md — fluoro-sim-alpha

Claude Code 向けのプロジェクト指示・引き継ぎメモ。

## このプロジェクトは何か

スマホのカメラで血管模型を撮影し、外部モニターに映して**フルオロスコピー（X線透視）を模擬する PWA**。
実機の C-arm（アンギオ装置）と同じ2ペダル操作を再現する:

- **観察 / Observe** ペダル … 踏んでいる間だけライブ映像を表示、離すと黒画面（透視の ON/OFF 模擬）
- **撮影 / Acquire** ペダル … 踏んでいる間だけシネ撮影（最大10秒）、離すと右上のワイプでループ再生

フレームワークもビルドも無し。`index.html` 一枚に HTML/CSS/JS を全部入れた依存ゼロの単一ファイル構成。

### 位置づけ（大きなプロジェクトの一部）

カテーテル手技の練習キット（**手術練習キット**）を構成する2系統のうちの「映像側」。

```
手術練習キット（依頼者: 亀井先生 / 医師）
├─ 脈動ポンプ PoC (pulse-pump)   … 心拍波形を再現する送液ポンプ（M5Stack Core2 + TMC2209 + Kamoer）
│    https://github.com/ojimpo/pulse-pump
└─ 透視シミュレーター (fluoro-sim) … ← このリポジトリ。血管模型を透視風に大画面表示する PWA
```

血管模型を暗箱の中で下からバックライト照明し、上のスマホカメラで撮影 → DP Alt Mode で外部モニターにミラーリング、
という運用を想定している（明るい背景に暗いデバイスが映る＝実際の透視画像と同じ見え方）。

### alpha である点に注意

これは**テスト用の使い捨て alpha デプロイ**。本番リポジトリは `fluoro-sim` を予定しており、名前衝突を避けるため `-alpha` を付けている。
このリポジトリの URL（https://ojimpo.github.io/fluoro-sim-alpha/ ）は本番として配布しないこと。

## ファイル構成

- `index.html` … 全部入り（HTML + CSS + JS、1ファイル）
- `manifest.json` … PWA manifest（`display: fullscreen` / `orientation: landscape`）
- `README.md` … 利用者・概要向け説明
- PWA アイコンは未同梱（OS 既定を使う）

## 実装済み機能（index.html）

- **観察 / 撮影の2ペダル**。物理フットスイッチ（キーボード扱い）と画面下のオンスクリーンペダルの両対応
- **撮影ペダルが観察より優先**。撮影中は観察の押下/解放が画面制御を触らない
- **10秒キャップ**。上限到達で `recordCut` を立て、ペダルを離すまで待ってから待機に戻す
- **リプレイワイプ**。撮影クリップを右上でループ再生、タップで保存シート、× で消去
- **Rec（セッション録画）**。ペダルとは独立にセッション全体を録画する第2の `MediaRecorder`（`start(1000)` でタイムスライス）
- **表示モード**を `mono → inverted → color` で循環（`I` キー or Mono ボタン）。CSS `filter` で透視風（grayscale/contrast/brightness、反転で X 線風）
- **保存**は `navigator.share()`（写真 App 等へ）→ 非対応なら `<a download>` にフォールバック
- **USB/BT フットスイッチのキー割り当て**。開始画面で登録し `localStorage` に永続化

## 設計思想・ハマりどころ（iOS Safari 前提）

主要ターゲットは **iPhone 15 以降 + iOS Safari**（DP Alt Mode 対応機）。以下は調査・実装で確定した勘所。

- **1画面完結（シングルページ）にする**。SPA で URL ハッシュが変わるとカメラが切れる報告があるため、画面遷移を作らない
- **フットスイッチは「任意のキー = 観察」設計**。機種でキー割り当てが違うため。撮影キーだけ登録すれば他の全キーが観察になる（`classifyKey`）
  - `keydown` の `repeat` は無視（長押しリピート防止）、`Escape`・修飾キーは除外、`I` は keyup 側で表示モード循環
- **`getUserMedia` はユーザージェスチャー起点**（Start ボタンの click 内）で呼ぶ。`facingMode: environment` / 1920×1080 ideal
- **`MediaRecorder` は MIME タイプを指定しない**（`new MediaRecorder(stream)`）。Safari の MIME 処理に癖があり未指定が最も安定。保存拡張子は `blob.type` から判定
- **PWA standalone だとカメラ許可が毎回プロンプトされる**（WebKit Bug #215884）。Safari で直接 URL を開けば回避できる（実用上は毎回1タップでも可）
- **フルスクリーン/ミラーリング**は DP Alt Mode のスクリーンミラーで外部モニターにそのまま出る。縦向き時は回転を促すヒントを表示

## 開発・デプロイ

- **ホスティング**: GitHub Pages（main / root）。サーバー不要の静的配信
- ローカル確認はブラウザで `index.html` を開くだけ。実機確認は iPhone Safari で GitHub Pages の URL を開く
- 変更は `index.html` を直接編集する（ビルドステップ無し）

## 兄弟プロジェクト pulse-pump の運用に倣う

pulse-pump 側では機能ごとにコミットを分け、README/CLAUDE.md/DEVLOG.md を同期し、実機確認を都度取る運用が確立している。
このリポジトリでも、**機能単位でコミットを分け、実機（iPhone Safari）で確認してから進める**方針に揃える。

## 残タスク・今後

- Canvas 経由のリアルタイム画像処理（明度反転・コントラストのパラメータ調整 UI）※現状は CSS filter の固定値
- Service Worker（オフライン対応）とホーム画面追加まわりの詰め
- Bluetooth フットスイッチ（ページターナーペダル等）での実機テスト
- 本番 `fluoro-sim` リポジトリへの移行

## 関連（Cosense: kouki プロジェクト）

- `透視シミュレーターPWA 実装プラン` … 設計意図と実装プランの原典
- `透視シミュレーター構成検討` … スマホ選定（DP Alt Mode）・筐体/光学系・コスト検討
- `手術練習キット` / `NBCAポンプ班` … 上位プロジェクト
- `脈動ポンプPoC 進捗ログ` … 兄弟プロジェクト（pulse-pump）の開発ログ
