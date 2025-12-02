from linebot_app.reply_format import format_analysis_message


def test_format_analysis_message_returns_summary_with_items():
    analysis = {
        "food_items": [
            {
                "name": "烤雞胸",
                "portion_size": "150g",
                "calories": "250 kcal",
                "macronutrients": {"carbs": "0g", "protein": "35g", "fat": "8g"},
            },
            {
                "name": "糙米飯",
                "portion_size": "1碗",
                "calories": "220 kcal",
                "macronutrients": {"carbs": "45g", "protein": "5g", "fat": "2g"},
            },
        ]
    }

    message = format_analysis_message(analysis)

    assert "分析完成" in message
    assert "烤雞胸" in message and "150g" in message
    assert "糙米飯" in message and "220 kcal" in message
    assert "碳水 45g" in message


def test_format_analysis_message_when_no_items():
    message = format_analysis_message({})
    assert "未能解析" in message
