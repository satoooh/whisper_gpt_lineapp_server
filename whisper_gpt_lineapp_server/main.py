import os
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, AudioMessage
from linebot.exceptions import InvalidSignatureError
import openai
from mangum import Mangum
from dotenv import load_dotenv


load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY


def transcribe_audio(file_path):
    with open(file_path, "rb") as f:
        transcription = openai.Audio.transcribe("whisper-1", f)["text"]
    return transcription


def format_text_with_chatgpt(transcription):
    prompt = f"文字起こし結果のデータ target が与えられるので、これをスクリプトとして整形してください。 \
        誤字脱字を修正し、フィラーを取り除くなどして読みやすくなるよう整形を実行してください。\
        整形後のメッセージ以外を絶対に出力しないこと。\n\n \
        target: {transcription}"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    text = completion["choices"][0]["message"]["content"]
    return text


@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):
    message_content = line_bot_api.get_message_content(event.message.id)

    with open("/tmp/tmp.m4a", "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    transcription = transcribe_audio("/tmp/tmp.m4a")
    print(f"transcription: {transcription}")
    formatted_text = format_text_with_chatgpt(transcription)
    print(f"formatted_text: {formatted_text}")

    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=formatted_text),
    )


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World!"}


@app.post("/webhook")
async def webhook(request: Request):
    print("Request received")
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()

    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid request")

    return {"status": "success"}


lambda_handler = Mangum(app, lifespan="off")
