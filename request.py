import requests
from bs4 import BeautifulSoup
import multiprocessing
from pymongo.errors import DuplicateKeyError  # 引入 DuplicateKeyError
from database import Database  # 引入資料庫類別


# 头部信息，模拟浏览器请求
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# 基础参数
base_url = "https://www.ithome.com.tw/news"
num_workers = 8

json_file = "ithome_news.json"

class Dump:
    def __init__(self, queue):
        self.queue = queue
        self.first_json_entry = True  # 记录是否是第一个 JSON 数据
        self.db_instance = None
        self.db_news_collection = None
        print("init")

        # 初始化 JSON，写入 `[`
        with open(json_file, "w", encoding="utf-8") as f:
            f.write("[\n")


    def save(self, data):
        # 手写 JSON 格式
        with open(json_file, "a", encoding="utf-8") as f:
            if not self.first_json_entry:
                f.write(",\n")  # 追加逗号换行，分隔 JSON 项
            self.first_json_entry = False  # 之后所有数据前都需要加逗号
            f.write(f'  {{"_id": "{data["_id"]}","url": "{data["url"]}","date": "{data["date"]}","title": "{data["title"]}","content":"{data["content"]}"}}')

            # 將資料存入 MongoDB
        try:
            self.db_news_collection.insert_one(data)
            print("資料已存入資料庫")
        except DuplicateKeyError:
            print("資料已存在，跳過")


    def data_analyze(self):
        self.db_instance = Database()
        self.db_news_collection = self.db_instance.get_collection('newsgaha')

        while True:
            (news_id, data) = self.queue.get()
            if news_id == -1:
                with open(json_file, "a", encoding="utf-8") as f:
                    f.write("]")
                break
            soup = BeautifulSoup(data, "html.parser")
            title_tag = soup.find("h1", class_="page-header")  # 文章标题
            #summary_tag = soup.find("div", class_="content-summary")
            date_tag = soup.find("span", class_="created")
            content_tag = soup.find("div", class_="field field-name-body field-type-text-with-summary field-label-hidden")

            if title_tag and content_tag:
                title = title_tag.get_text(strip=True).replace('"', "'")  # 替换双引号，防止 JSON 解析错误
                content = content_tag.get_text(strip=True).replace('"', "'")  # 替换双引号
                date = date_tag.get_text(strip=True).replace('"', "'")
                url = f"{base_url}/{news_id}"
                print(f"成功爬取: {news_id} - {title}")
                data = {"_id": url,
                        "url": url,
                        "date": date,
                        "title": title,
                        "content": content,
                        }
                self.save(data)  # 送入队列
            else:
                print(f"跳过: {news_id} - 可能是无效页面")

def fetch_news(news_id, queue):
    url = f"{base_url}/{news_id}"
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            queue.put((news_id, response.text)) #送入分析對列
        else:
            print(f"失败: {news_id} - HTTP 状态码 {response.status_code}")
    except requests.RequestException as e:
        print(f"请求错误: {news_id} - {e}")

def get_all_link(start, end):
    news_ids = []
    for page in range(start, end+1):  # 修改範圍以爬取更多頁
        url = f'{base_url}?page={page}'
        print(f"正在爬取: {url}")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 找到每篇文章的連結
            titles = soup.find_all('div', class_='view-content')[1].find_all('p', class_='title')  # 根據 iThome 的文章標題 class
            print(titles)
            for article in titles:
                print(article.text)
                a_tag = article.find('a')
                href = a_tag['href']
                news_id = int(href.split('/')[-1])
                news_ids.append(news_id)
    news_ids = list(set(news_ids))
    news_ids.sort()
    news_ids = news_ids[::-1]
    news_ids.append(-1)
    return news_ids

def main():
    manager = multiprocessing.Manager()
    queue = manager.Queue()  # 使用 Manager 创建共享队列

    # 创建数据存储进程
    dump = Dump(queue)
    dump_process = multiprocessing.Process(target=dump.data_analyze)
    dump_process.start()

    pool = multiprocessing.Pool(num_workers)
    #news_id_list = [i for i in range(0, 321+1)]
    #links = pool.starmap(get_all_link, [(news_id, news_id) for news_id in news_id_list])  # 使用 starmap 传递参数
    links = get_all_link(0, 321)
    print(links)

    # 多进程爬取
    pool.starmap(fetch_news, [(news_id, queue) for news_id in links])  # 使用 starmap 传递参数
    # 发送结束信号
    dump_process.join()
    print(f"所有新闻已爬取，数据已存入 {json_file}")

if __name__ == "__main__":
    main()