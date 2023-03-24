# LINE でボイスメモから文字起こしと整形してくれるやつ

LINE 上で音声を文字起こしし、GPT-3.5-turbo によって整形された文章を返信する LINE Bot の FastAPI サーバー側のソースコード

↓のツイートを見て LINE でサクッと出来たら便利だなと思ったのがきっかけで作りました。

> [@kensuu](https://twitter.com/kensuu/status/1638911266931761152)
> 1: 超おもしろい記事を頭の中で書く
> 2: それをそのまま言葉で話す
> 3:音声入力でテキストにする
> 4:ChatGPTで整形してもらう
> 5:noteに貼る
> 6:細かいところを修正
>
> ブログ書くのがめちゃくちゃ楽になってしまった。文章書くのが苦手な人でも、これならブログを毎日書けたりするのでは！

## 機能

- OpenAI Whisper API による音声メッセージの文字起こし
- GPT-3.5-turbo による文章整形

## セットアップ

### 環境変数の取得

1. [LINE Developers](https://developers.line.biz/ja/) で LINE Messaging API のチャンネルを作成し、チャンルアクセストークンとチャネルシークレットを取得
2. [OpenAI](https://platform.openai.com/signup/) でアカウントを作成し、API キーを取得

### 環境設定

1. Python 3.9 以上がインストールされていることを確認
2. このリポジトリをクローン
3. `poetry` をインストール
4. `poetry install` を実行して、必要なパッケージをインストール
5. `.env.sample` を参考に、 `CHANNEL_ACCESS_TOKEN`、`CHANNEL_SECRET`、`OPENAI_API_KEY` を取得した API キーに置き換えた `.env` ファイルを作成

### サーバーの実行

1. `sh dev.sh` を実行して、APIサーバーを起動
2. `http://127.0.0.1:8000/` にアクセスし、 `{"message": "Hello World"}` が返ってくることを確認

### LINE Bot との連携

1. [ngrok](https://ngrok.com/) をインストールして、`ngrok http 8000` を実行
2. LINE Developers コンソールで、Webhook URL を `https://*****/.ngrok.io/webhook` （ngrok で発行されたURL）に設定

## 使い方

1. LINE アプリで、Whisper GPT LINE Bot に音声メッセージを送信
2. 文字起こしと整形された文章が返信される

![demo image](https://gyazo.com/687cb3e57a97a941bce11a9b5695fcc6.png)

## デプロイ

AWS Lambda へのデプロイを想定

- `sh build.sh` を実行すると、デプロイ時に必要な zip ファイルが作成される
- AWS Console > AWS Lambda から「関数の作成」
  - 一から作成
    - 関数名は任意（これを {func_name} とする）
    - Python 3.9
    - x86_64
  - 「コード」>「アップロード元」>「.zipファイル」から `artifact.zip` をアップロード
  - 「コード」>「ランタイム設定」から、ハンドラの値を `{func_name}.main.lambda_handler` に設定
  - 「設定」>「環境変数」から、 `.env` ファイルに記載した環境変数を設定
- AWS Console > API Gateway から 「APIの作成」
  - REST API
    - 新しいAPI
  - 「リソース」>「アクション」>「メソッドの作成」
    - ANY
      - 統合タイプ: Lambda 関数
      - Lambda プロキシ統合の使用を選択
      - Lambda リージョン: ap-northeast-1
      - Lambda 関数: {func_name}
      - デフォルトタイムアウトの使用を選択
  - 「リソース」>「アクション」>「リソースの作成」
    - 「プロキシリソースとして設定する」を選択
    - リソース名: proxy
    - リソースパス: `/{proxy+}`
      - 統合タイプ: Lambda 関数プロキシ
      - Lambda リージョン: ap-northeast-1
      - Lambda 関数: {func_name}
      - デフォルトタイムアウトの使用を選択
  - 「アクション」>「APIのデプロイ」
    - 新しいステージ
- エンドポイントのURLの後ろに `/webhook` を追加して、LINE Developers コンソールで Webhook URL に設定

## Future Work

- ChatGPT に投げる prompt の改善

## ライセンス

MIT License
