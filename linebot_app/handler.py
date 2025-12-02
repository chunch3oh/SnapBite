import logging
import os
import tempfile
from typing import List

from linebot import LineBotApi
from linebot.models import ImageMessage, MessageEvent, TextSendMessage

from source.image_analysis import Analyst
from .reply_format import format_analysis_message
from .storage import save_analysis_log

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

analyst = Analyst(language="zh-TW")

HELP_TEXT = (
    "傳送餐點照片，我會回覆營養摘要。\n"
    "指令：\n"
    "- help：查看說明\n"
    "- 任何文字：回覆操作提示"
)


def handle_text_message(event: MessageEvent, unsupported: bool = False) -> List[TextSendMessage]:
    if unsupported:
        return [TextSendMessage(text="目前僅支援文字或照片訊息。")]

    user_text = (event.message.text or "").strip().lower()

    if user_text in ("help", "說明", "?"):
        return [TextSendMessage(text=HELP_TEXT)]

    return [
        TextSendMessage(
            text="請直接傳餐點照片，我會分析營養並以文字回覆。\n需要指令清單請輸入 help。"
        )
    ]


async def handle_image_message(event: MessageEvent, line_bot_api: LineBotApi) -> List[TextSendMessage]:
    message_id = event.message.id
    user_id = getattr(event.source, "user_id", "") or ""

    tmp_path = None
    try:
        message_content = line_bot_api.get_message_content(message_id)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            for chunk in message_content.iter_content():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        analysis = analyst.analyze_image(tmp_path)
        reply_text = format_analysis_message(analysis)

        try:
            save_analysis_log(user_id=user_id, message_id=message_id, analysis=analysis)
        except Exception:
            logger.exception("Failed to persist analysis for message %s", message_id)

    except Exception:
        logger.exception("Failed to handle image message %s", message_id)
        reply_text = "圖片處理失敗，請稍後再試。"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                logger.warning("Failed to remove temp file %s", tmp_path)

    return [TextSendMessage(text=reply_text)]
