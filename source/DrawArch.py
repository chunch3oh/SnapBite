from graphviz import Digraph

# 建立流程圖
dot = Digraph(comment='Diet Tracking Chatbot Workflow', format='png')
dot.attr(rankdir='LR', fontsize='12')
dot.attr('node', shape='box')

# 節點與負責模組
modules = {
    'A':  ('LINE Bot 傳送照片', 'Frontend'),
    'B':  ('Webhook 傳遞至 Python 後端', 'Server'),
    'C':  ('圖片處理與參照物辨識\n（OpenCV / YOLO）', 'Image Processing'),
    'D':  ('食物分類與份量推估', 'Image Processing'),
    'E':  ('查詢營養成分資料庫\n（USDA / 衛福部）', 'Nutrition'),
    'F':  ('計算每餐攝取數值', 'Nutrition'),
    'G':  ('回傳營養摘要與建議', 'Feedback'),
    'H':  ('儲存每日飲食資料', 'Storage'),
    'I':  ('產生每日圖表（Matplotlib）', 'Visualization'),
    'J':  ('傳送每日視覺化摘要回 LINE', 'Frontend')
}

# 模組對應顏色
colors = {
    'Frontend': '#F9F871',
    'Server': '#E2CFEA',
    'Image Processing': '#A1E3D8',
    'Nutrition': '#FFCF9C',
    'Feedback': '#FF9B9B',
    'Storage': '#B2B2B2',
    'Visualization': '#87A8D0',
}

# 加入節點
for step, (label, module) in modules.items():
    dot.node(step, label=label, style='filled', fillcolor=colors[module])

# 定義流程順序
edges = [
    ('A', 'B'),
    ('B', 'C'),
    ('C', 'D'),
    ('D', 'E'),
    ('E', 'F'),
    ('F', 'G'),
    ('F', 'H'),
    ('H', 'I'),
    ('I', 'J'),
]

# 加入邊
for src, dst in edges:
    dot.edge(src, dst)

# 輸出檔案
dot.render('diet_chatbot_workflow_diagram', format='png', directory='.', cleanup=False)