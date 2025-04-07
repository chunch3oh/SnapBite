# 🥗 SnapBite

SnapBite 是一個整合 LINE Bot 與 AI 圖像分析的飲食追蹤系統。使用者只需透過 LINE 傳送餐點照片，系統便能自動辨識食物、分析份量與營養成分，並提供即時建議與每日視覺化報告。

![系統架構圖](images/architecture.png)
## 📦 功能特色

- 📸 圖像辨識：自動偵測食物與參照物
- 🍱 份量推估：使用電腦視覺分析食物比例
- 🔍 營養計算：結合資料庫精準估算熱量與營養素
- 💬 飲食建議：根據攝取情況給出即時回饋
- 📊 視覺化報告：每日生成飲食雷達圖與營養統計圖

## 🧩 技術架構

- **前端**：LINE Bot（部署於 Zeabur）
- **後端**：Python + Gradio，負責圖像處理與 API 回應
- **AI 模型**：YOLOv8 / OpenCV / 自訂分類器
- **資料來源**：USDA FoodData Central、台灣食物營養資料庫
- **視覺化**：Matplotlib / Plotly

## 🛠 專案結構

```
SnapBite/
├── source/
│   ├── DrawArch.py          # 系統流程圖產生器
│   ├── image_analysis.py    # 圖像辨識與尺寸估算
│   ├── nutrition.py         # 營養計算邏輯
│   ├── suggest.py           # 飲食建議生成模組
│   ├── visualize.py         # 視覺化每日飲食數據
│
├── linebot/
│   ├── webhook.py           # 接收 LINE 訊息並處理
│   ├── handler.py           # 文字與圖片分析流程
│   └── reply_format.py      # 格式化回傳訊息
│
├── data/                    # 儲存使用者餐點與營養紀錄
└── README.md
```

## 🚀 快速開始

1. 安裝 Python 套件：
   ```bash
   pip install -r requirements.txt
   ```

2. 執行 Gradio 後端測試：
   ```bash
   python source/app.py
   ```

3. 在 Zeabur 部署 webhook 並綁定 LINE Bot

## 📮 聯絡我們

由 Chun 開發，專為實用又溫暖的健康生活打造。