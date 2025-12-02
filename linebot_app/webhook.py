import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import ImageMessage, MessageEvent, TextMessage

from .handler import handle_image_message, handle_text_message

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise RuntimeError("LINE credentials missing. Please set LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET.")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

app = FastAPI(title="SnapBite LINE Webhook")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/callback", response_class=PlainTextResponse)
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = (await request.body()).decode("utf-8")

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError as exc:
        raise HTTPException(status_code=400, detail="Invalid signature") from exc

    for event in events:
        if not isinstance(event, MessageEvent):
            continue

        if isinstance(event.message, TextMessage):
            replies = handle_text_message(event)
        elif isinstance(event.message, ImageMessage):
            replies = await handle_image_message(event, line_bot_api)
        else:
            replies = handle_text_message(event, unsupported=True)

        if replies:
            line_bot_api.reply_message(event.reply_token, replies)

    return PlainTextResponse("OK")
