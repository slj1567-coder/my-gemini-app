import os
import asyncio
import json
from datetime import datetime, timezone
import google.generativeai as genai
import edge_tts
from feedgen.feed import FeedGenerator
from duckduckgo_search import DDGS

# --- 設定 ---
# 請在 GitHub Settings -> Secrets 設定 GEMINI_API_KEY
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY")
PODCAST_TITLE = "每日 AI 科技報"
PODCAST_URL = "https://slj1567-coder.github.io/auto-news-podcast/"
RSS_FILENAME = "feed.xml"
AUDIO_DIR = "audio"

# --- 1. 搜尋新聞 ---
def search_news(topic="人工智慧 科技新聞"):
    print(f"🔍 正在搜尋: {topic}...")
    results = DDGS().text(topic, max_results=5, region="wt-wt", timelimit="d")
    news_summary = ""
    for r in results:
        news_summary += f"- {r['title']}: {r['body']}\n"
    return news_summary

# --- 2. Gemini 生成腳本 ---
def generate_script(news_text):
    print("🤖 Gemini 正在撰寫腳本...")
    genai.configure(api_key=GENAI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    你是一個 Podcast 製作人。請根據以下新聞，寫一段約 2 分鐘的單人播報稿。
    風格：專業、節奏明快、像廣播主持人。
    新聞內容：
    {news_text}
    
    請直接輸出播報內容文字即可，不要有 [音樂] 或 (笑聲) 等標註。
    """
    response = model.generate_content(prompt)
    return response.text

# --- 3. 文字轉語音 (Edge TTS) ---
async def text_to_speech(text, output_file):
    print("🎙️ 正在錄音 (Edge TTS)...")
    # zh-TW-HsiaoChenNeural 是台灣女聲，非常自然
    communicate = edge_tts.Communicate(text, "zh-TW-HsiaoChenNeural")
    await communicate.save(output_file)

# --- 4. 更新 RSS Feed ---
def update_rss(audio_filename, title, description):
    print("📡 正在更新 RSS...")
    fg = FeedGenerator()
    fg.load_extension('podcast')
    
    # 如果 RSS 已存在，理論上要讀取舊的並附加新的(這裡簡化為每次重建，或讀取現有xml邏輯需更複雜)
    # 為了教學簡單，我們這裡設定為「生成最新一集的 Feed」
    # *進階：你可以寫程式讀取舊 XML 加上新 Item*
    
    fg.title(PODCAST_TITLE)
    fg.link(href=PODCAST_URL, rel='alternate')
    fg.description('由 AI 自動生成的科技新聞')
    fg.language('zh-TW')
    
    # 新增這一集
    fe = fg.add_entry()
    fe.id(f"{PODCAST_URL}{audio_filename}")
    fe.title(title)
    fe.description(description)
    fe.enclosure(f"{PODCAST_URL}{audio_filename}", 0, 'audio/mpeg')
    fe.pubDate(datetime.now(timezone.utc))
    
    fg.rss_file(RSS_FILENAME)

# --- 主程式 ---
async def main():
    # 建立音訊資料夾
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    # 1. 獲取新聞
    news = search_news()
    
    # 2. 生成腳本
    script = generate_script(news)
    print(f"腳本預覽: {script[:100]}...")
    
    # 3. 生成音檔名稱 (使用日期)
    today_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{AUDIO_DIR}/news_{today_str}.mp3"
    
    # 4. 合成語音
    await text_to_speech(script, filename)
    
    # 5. 更新 RSS
    update_rss(filename, f"{today_str} 科技快報", script[:200])
    print("✅ 完成！")

if __name__ == "__main__":
    asyncio.run(main())
