import requests
from bs4 import BeautifulSoup
from database import Database  # 引入資料庫類別
from datetime import datetime
from pymongo.errors import DuplicateKeyError  # 引入 DuplicateKeyError
import time  # 引入 time 模組

# 初始化資料庫
db_instance = Database()
news_collection = db_instance.get_collection('news')  # 使用 'news' 集合

# 定義 iThome 文章的 URL 模板
base_url = "https://ithelp.ithome.com.tw/articles?page={}"  # iThome 的文章分頁 URL
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
}

# 爬取前 50 頁的文章（假設每頁 10 篇，共 500 篇）
for page in range(1, 51):  # 修改範圍以爬取更多頁
    url = base_url.format(page)
    print(f"正在爬取: {url}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到每篇文章的連結
        articles = soup.find_all('a', class_='qa-list__title-link')  # 根據 iThome 的文章標題 class
        for article in articles:
            title = article.get_text(strip=True)
            href = article['href']

            # 檢查 href 是否為完整 URL
            if href.startswith('http'):
                link = href
            else:
                link = "https://ithelp.ithome.com.tw" + href  # 拼接完整連結

            print(f"標題: {title}")
            print(f"連結: {link}")

            # 爬取文章內容
            article_response = requests.get(link, headers=headers)
            if article_response.status_code == 200:
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                # 提取文章內容
                content = article_soup.find('div', class_='markdown__style').get_text(strip=True)  # 根據文章內容的 class

                # 提取文章的發佈時間
                time_element = article_soup.find('a', class_='qa-header__info-time')  # 根據時間的 class
                if time_element:
                    published_time = time_element.get_text(strip=True)
                else:
                    published_time = None  # 如果找不到時間，設為 None

                print(f"內容: {content[:100]}...")  # 只顯示前 100 個字
                print(f"發佈時間: {published_time}")

                # 將資料存入 MongoDB
                try:
                    news_collection.insert_one({
                        '_id': link,  # 使用文章連結作為唯一 ID，避免重複
                        'title': title,
                        'link': link,
                        'content': content,
                        'published_time': published_time,  # 儲存發佈時間
                        'scraped_time': datetime.now()  # 紀錄爬取時間
                    })
                    print("資料已存入資料庫")
                except DuplicateKeyError:
                    print("資料已存在，跳過")
            else:
                print(f"無法訪問文章內容，狀態碼: {article_response.status_code}")
            print("-" * 50)
            time.sleep(1)  # 延遲 1 秒
    else:
        print(f"無法訪問分頁，狀態碼: {response.status_code}")