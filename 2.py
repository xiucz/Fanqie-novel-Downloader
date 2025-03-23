import time
import requests
import bs4
import re
import os
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
<<<<<<< HEAD
from tqdm import tqdm as tqdm_original  # 修改导入方式，避免缓存
from collections import OrderedDict

# 全局配置
CONFIG = {
    "max_workers": 5,
    "max_retries": 3,
    "request_timeout": 15,
    "status_file": "chapter.json",
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ],
    "api_sources": {
        "primary": "http://rehaofan.jingluo.love",
        "backup": "https://api.cenguigui.cn/api/tomato/api"
    }
}

# 全局变量，用于GUI覆盖tqdm
tqdm = tqdm_original  # 默认使用原始tqdm，GUI会覆盖此变量

def get_headers(cookie=None):
    """生成随机请求头"""
    return {
        "User-Agent": random.choice(CONFIG["user_agents"]),
        "Cookie": cookie if cookie else get_cookie()
    }

def get_cookie():
    """生成或加载Cookie"""
    cookie_path = "cookie.json"
    if os.path.exists(cookie_path):
        try:
            with open(cookie_path, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # 生成新Cookie
    for _ in range(10):
        novel_web_id = random.randint(10**18, 10**19-1)
        cookie = f'novel_web_id={novel_web_id}'
        try:
            resp = requests.get(
                'https://fanqienovel.com',
                headers={"User-Agent": random.choice(CONFIG["user_agents"])},
                cookies={"novel_web_id": str(novel_web_id)},
                timeout=10
            )
            if resp.ok:
                with open(cookie_path, 'w') as f:
                    json.dump(cookie, f)
                return cookie
        except Exception as e:
            print(f"Cookie生成失败: {str(e)}")
            time.sleep(0.5)
    raise Exception("无法获取有效Cookie")

def down_text(it, mod=1):
    """下载章节内容"""
    max_retries = CONFIG.get('max_retries', 3)
    retry_count = 0
    content = ""
    
    while retry_count < max_retries:
        try:
            # 尝试使用主API获取内容
            api_url = f"{CONFIG['api_sources']['primary']}/content?item_id={it}"
            response = requests.get(api_url, timeout=CONFIG["request_timeout"])
            data = response.json()
            
            if data.get("code") == 0 and data.get("data", {}).get("content", ""):
                content = data.get("data", {}).get("content", "")
            else:
                # 如果主API失败，尝试备用API
                backup_api_url = f"{CONFIG['api_sources']['backup']}/content.php?item_id={it}"
                response = requests.get(backup_api_url, timeout=CONFIG["request_timeout"])
                data = response.json()
                if data.get("code") == 0:
                    content = data.get("data", {}).get("content", "")
            
            if content:
                # 移除HTML标签
=======
from lxml import etree
from tqdm import tqdm

# 全局变量
cookie_path = "cookie.json"
MAX_WORKERS = 5  # 默认线程数
OUTPUT_FORMAT = "txt"  # 默认输出格式：txt（单文件）或chapter（每章一个文件）

# 获取随机User-Agent
def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47",
    ]
    return random.choice(user_agents)

# 获取或加载Cookie
def get_cookie():
    bas = 1000000000000000000
    for i in range(random.randint(bas * 6, bas * 8), bas * 9):
        time.sleep(random.randint(50, 150) / 1000)
        cookie = 'novel_web_id=' + str(i)
        headers = {
            'User-Agent': get_random_user_agent(),
            'cookie': cookie
        }
        try:
            response = requests.get('https://fanqienovel.com', headers=headers, timeout=10)
            if response.status_code == 200 and len(response.text) > 200:
                try:
                    # 在打包环境下可能无法写入cookie文件，这里做异常处理
                    with open(cookie_path, 'w', encoding='utf-8') as f:
                        json.dump(cookie, f)
                    print(f"cookie已生成: {cookie}")
                except Exception as e:
                    print(f"cookie写入失败，但不影响使用: {str(e)}")
                return cookie
        except Exception as e:
            print(f"请求失败: {e}")
    return None

# 模拟浏览器请求
def get_headers():
    return {
        "User-Agent": get_random_user_agent(),
        "Cookie": get_cookie()
    }

# 加密内容解析
CODE_ST = 58344
CODE_ED = 58715
charset = ['D', '在', '主', '特', '家', '军', '然', '表', '场', '4', '要', '只', 'v', '和', '?', '6', '别', '还', 'g',
           '现', '儿', '岁', '?', '?', '此', '象', '月', '3', '出', '战', '工', '相', 'o', '男', '首', '失', '世', 'F',
           '都', '平', '文', '什', 'V', 'O', '将', '真', 'T', '那', '当', '?', '会', '立', '些', 'u', '是', '十', '张',
           '学', '气', '大', '爱', '两', '命', '全', '后', '东', '性', '通', '被', '1', '它', '乐', '接', '而', '感',
           '车', '山', '公', '了', '常', '以', '何', '可', '话', '先', 'p', 'i', '叫', '轻', 'M', '士', 'w', '着', '变',
           '尔', '快', 'l', '个', '说', '少', '色', '里', '安', '花', '远', '7', '难', '师', '放', 't', '报', '认',
           '面', '道', 'S', '?', '克', '地', '度', 'I', '好', '机', 'U', '民', '写', '把', '万', '同', '水', '新', '没',
           '书', '电', '吃', '像', '斯', '5', '为', 'y', '白', '几', '日', '教', '看', '但', '第', '加', '候', '作',
           '上', '拉', '住', '有', '法', 'r', '事', '应', '位', '利', '你', '声', '身', '国', '问', '马', '女', '他',
           'Y', '比', '父', 'x', 'A', 'H', 'N', 's', 'X', '边', '美', '对', '所', '金', '活', '回', '意', '到', 'z',
           '从', 'j', '知', '又', '内', '因', '点', 'Q', '三', '定', '8', 'R', 'b', '正', '或', '夫', '向', '德', '听',
           '更', '?', '得', '告', '并', '本', 'q', '过', '记', 'L', '让', '打', 'f', '人', '就', '者', '去', '原', '满',
           '体', '做', '经', 'K', '走', '如', '孩', 'c', 'G', '给', '使', '物', '?', '最', '笑', '部', '?', '员', '等',
           '受', 'k', '行', '一', '条', '果', '动', '光', '门', '头', '见', '往', '自', '解', '成', '处', '天', '能',
           '于', '名', '其', '发', '总', '母', '的', '死', '手', '入', '路', '进', '心', '来', 'h', '时', '力', '多',
           '开', '己', '许', 'd', '至', '由', '很', '界', 'n', '小', '与', 'Z', '想', '代', '么', '分', '生', '口',
           '再', '妈', '望', '次', '西', '风', '种', '带', 'J', '?', '实', '情', '才', '这', '?', 'E', '我', '神', '格',
           '长', '觉', '间', '年', '眼', '无', '不', '亲', '关', '结', '0', '友', '信', '下', '却', '重', '己', '老',
           '2', '音', '字', 'm', '呢', '明', '之', '前', '高', 'P', 'B', '目', '太', 'e', '9', '起', '稜', '她', '也',
           'W', '用', '方', '子', '英', '每', '理', '便', '西', '数', '期', '中', 'C', '外', '样', 'a', '海', '们',
           '任']

def interpreter(cc):
    """解析加密内容"""
    bias = cc - CODE_ST
    if 0 <= bias < len(charset):  # 检查bias是否在charset的有效范围内
        if charset[bias] == '?':
            return chr(cc)
        return charset[bias]
    return chr(cc)  

def down_text(it, headers):
    """下载章节内容"""
    max_retries = 3  # 最大重试次数
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 使用新API获取内容
            api_url = f"http://rehaofan.jingluo.love/content?item_id={it}"
            response = requests.get(api_url, headers=headers, timeout=10)  # 超时时间
            data = response.json()
            
            if data.get("code") == 0:
                content = data.get("data", {}).get("content", "")
                # 清理HTML标签并保留段落结构
>>>>>>> 1ecb4f51e6909ebc6583015ecc10efdfed97a261
                content = re.sub(r'<header>.*?</header>', '', content, flags=re.DOTALL)
                content = re.sub(r'<footer>.*?</footer>', '', content, flags=re.DOTALL)
                content = re.sub(r'</?article>', '', content)
                content = re.sub(r'<p idx="\d+">', '\n', content)
                content = re.sub(r'</p>', '\n', content)
                content = re.sub(r'<[^>]+>', '', content)
<<<<<<< HEAD
                content = re.sub(r'\\u003c|\\u003e', '', content)
                content = re.sub(r'\n{2,}', '\n', content).strip()
                content = '\n'.join(['    ' + line if line.strip() else line for line in content.split('\n')])
                break
        except Exception as e:
            print(f"请求失败: {str(e)}, 重试第{retry_count + 1}次...")
            retry_count += 1
            time.sleep(1 * retry_count)
    
    return content

def get_book_info(book_id, headers):
    """获取书名、作者、简介"""
    # 首先尝试从网页获取信息
    url = f'https://fanqienovel.com/page/{book_id}'
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            
            # 获取书名
            name_element = soup.find('h1')
            name = name_element.text if name_element else None
            
            # 获取作者
            author_name_element = soup.find('div', class_='author-name')
            author_name = None
            if author_name_element:
                author_name_span = author_name_element.find('span', class_='author-name-text')
                author_name = author_name_span.text if author_name_span else None
            
            # 获取简介
            description_element = soup.find('div', class_='page-abstract-content')
            description = None
            if description_element:
                description_p = description_element.find('p')
                description = description_p.text if description_p else None
            
            if name and author_name and description:
                return name, author_name, description
    except Exception as e:
        print(f"从网页获取书籍信息失败: {str(e)}")
    
    # 如果网页获取失败，尝试使用API获取
    try:
        # 尝试备用API
        backup_api_url = f"{CONFIG['api_sources']['backup']}/detail.php?book_id={book_id}"
        response = requests.get(backup_api_url, timeout=CONFIG["request_timeout"])
        data = response.json()
        
        if data.get("code") == 0 and data.get("data"):
            book_data = data.get("data", {})
            name = book_data.get("book_name", "未知书名")
            author_name = book_data.get("author_name", "未知作者")
            description = book_data.get("abstract", "无简介")
            return name, author_name, description
    except Exception as e:
        print(f"从API获取书籍信息失败: {str(e)}")
    
    print(f"无法获取书籍信息，状态码: {response.status_code if 'response' in locals() else '未知'}")
    return "未知书名", "未知作者", "无简介"

def extract_chapters(soup):
    """解析章节列表"""
    chapters = []
    for idx, item in enumerate(soup.select('div.chapter-item')):
        a_tag = item.find('a')
        if not a_tag:
            continue
        
        raw_title = a_tag.get_text(strip=True)
        
        # 特殊章节
        if re.match(r'^(番外|特别篇|if线)\s*', raw_title):
            final_title = raw_title
        else:
            clean_title = re.sub(
                r'^第[一二三四五六七八九十百千\d]+章\s*',
                '', 
                raw_title
            ).strip()
            final_title = f"第{idx+1}章 {clean_title}"
        
        chapters.append({
            "id": a_tag['href'].split('/')[-1],
            "title": final_title,
            "url": f"https://fanqienovel.com{a_tag['href']}",
            "index": idx
        })
    
    # 检查章节顺序
    expected_indices = set(range(len(chapters)))
    actual_indices = set(ch["index"] for ch in chapters)
    if expected_indices != actual_indices:
        print("警告：章节顺序异常，可能未按阿拉伯数字顺序排列！")
        chapters.sort(key=lambda x: x["index"])
    
    return chapters

def load_status(save_path):
    """加载下载状态"""
    status_file = os.path.join(save_path, CONFIG["status_file"])
    if os.path.exists(status_file):
        try:
            with open(status_file, 'r') as f:
                return set(json.load(f))
        except:
            pass
    return set()

def save_status(save_path, downloaded):
    """保存下载状态"""
    status_file = os.path.join(save_path, CONFIG["status_file"])
    with open(status_file, 'w') as f:
        json.dump(list(downloaded), f)

def download_chapter(chapter, headers, save_path, book_name, downloaded):
    """下载单个章节"""
    if chapter["id"] in downloaded:
        return None
    
    content = down_text(chapter["id"])
    if content:
        output_file_path = os.path.join(save_path, f"{book_name}.txt")
        with open(output_file_path, 'a', encoding='utf-8') as f:
            f.write(f'{chapter["title"]}\n')
            f.write(content + '\n\n')
        downloaded.add(chapter["id"])
        return chapter["index"], content
    return None

def Run(book_id, save_path):
    """运行下载"""
=======
                content = re.sub(r'\n{2,}', '\n', content).strip()
                content = '\n'.join(['    ' + line if line.strip() else line for line in content.split('\n')])
                
                return content
        except requests.exceptions.RequestException as e:
            retry_count += 1
            print(f"网络请求失败，正在重试({retry_count}/{max_retries}): {str(e)}")
            time.sleep(2 * retry_count)  # 重试延迟时间
        except Exception as e:
            retry_count += 1
            print(f"下载出错，正在重试({retry_count}/{max_retries}): {str(e)}")
            time.sleep(1 * retry_count)
    
    print("达到最大重试次数，下载失败")
    return None

def funLog(text, headers):
    """解析章节内容"""
    content = down_text(text.url.split('/')[-1], headers)
    return content

def extract_chatper_titles(soup):
    """提取章节标题"""
    titles = []
    for item in soup.select('div.chapter-item'):
        title = item.get_text(strip=True)
        if title:
            titles.append(title)
    return titles

def get_book_info(book_id, headers):
    """获取书名、作者、简介"""
    url = f'https://fanqienovel.com/page/{book_id}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"网络请求失败，状态码: {response.status_code}")
        return None, None, None

    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    
    # 获取书名
    name_element = soup.find('h1')
    name = name_element.text if name_element else "未知书名"
    
    # 获取作者
    author_name_element = soup.find('div', class_='author-name')
    author_name = None
    if author_name_element:
        author_name_span = author_name_element.find('span', class_='author-name-text')
        author_name = author_name_span.text if author_name_span else "未知作者"
    
    # 获取简介
    description_element = soup.find('div', class_='page-abstract-content')
    description = None
    if description_element:
        description_p = description_element.find('p')
        description = description_p.text if description_p else "无简介"
    
    return name, author_name, description

def download_chapter(div, headers, save_path, book_name, titles, i, total, output_format="txt"):
    """下载单个章节"""
    if not div.a:
        print(f"第 {i + 1} 章没有链接，跳过")
        return None
    
    detail_url = f"https://fanqienovel.com{div.a['href']}"
    response = requests.get(detail_url, headers=headers)
    content = funLog(response, headers)

    if content:
        try:
            if output_format == "txt":
                # 所有章节保存在一个文件中
                output_file_path = os.path.join(save_path, f"{book_name}.txt")
                # 确保文件路径有效
                os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
                with open(output_file_path, 'a', encoding='utf-8') as f:
                    if f is None:  # 额外检查文件对象
                        raise IOError(f"无法打开文件: {output_file_path}")
                    f.write(f'{titles[i]}\n')
                    f.write(content + '\n\n')
            elif output_format == "chapter":
                # 每个章节保存为独立文件
                chapter_dir = os.path.join(save_path, book_name)
                os.makedirs(chapter_dir, exist_ok=True)
                # 替换文件名中的非法字符
                safe_title = re.sub(r'[\\/*?:"<>|]', "", titles[i])
                chapter_file = os.path.join(chapter_dir, f"{i+1:04d}_{safe_title}.txt")
                with open(chapter_file, 'w', encoding='utf-8') as f:
                    if f is None:  # 额外检查文件对象
                        raise IOError(f"无法打开文件: {chapter_file}")
                    f.write(f'{titles[i]}\n\n')
                    f.write(content)
            
            print(f'已下载 {i + 1}/{total}')
            return True
        except Exception as e:
            print(f"写入文件时出错: {str(e)}")
            return False
    else:
        print(f"第 {i + 1} 章下载失败")
        return False

def Run(book_id, save_path, output_format=None):
    """运行下载"""
    global MAX_WORKERS, OUTPUT_FORMAT
    
    # 如果提供了output_format参数，更新全局OUTPUT_FORMAT
    if output_format:
        OUTPUT_FORMAT = output_format
        
>>>>>>> 1ecb4f51e6909ebc6583015ecc10efdfed97a261
    headers = get_headers()
    
    # 获取书籍信息
    name, author_name, description = get_book_info(book_id, headers)
<<<<<<< HEAD
    if name == "未知书名":
        print("无法获取书籍信息，请检查小说ID或网络连接。")
        return

    # 尝试获取章节列表
    chapters = []
    try:
        # 首先尝试从网页获取章节列表
        url = f'https://fanqienovel.com/page/{book_id}'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, 'lxml')
            chapters = extract_chapters(soup)
    except Exception as e:
        print(f"从网页获取章节列表失败: {str(e)}")
    
    # 如果网页获取失败或章节为空，尝试使用API获取
    if not chapters:
        try:
            # 尝试使用备用API获取所有章节
            backup_api_url = f"{CONFIG['api_sources']['backup']}/all_items.php?book_id={book_id}"
            response = requests.get(backup_api_url, timeout=CONFIG["request_timeout"])
            data = response.json()
            
            if data.get("code") == 0 and data.get("data"):
                items_data = data.get("data", [])
                chapters = []
                for idx, item in enumerate(items_data):
                    raw_title = item.get("title", f"第{idx+1}章")
                    
                    # 特殊章节
                    if re.match(r'^(番外|特别篇|if线)\s*', raw_title):
                        final_title = raw_title
                    else:
                        clean_title = re.sub(
                            r'^第[一二三四五六七八九十百千\d]+章\s*',
                            '', 
                            raw_title
                        ).strip()
                        final_title = f"第{idx+1}章 {clean_title}"
                    
                    chapters.append({
                        "id": item.get("item_id"),
                        "title": final_title,
                        "url": f"https://fanqienovel.com/reader/{item.get('item_id')}",
                        "index": idx
                    })
        except Exception as e:
            print(f"从API获取章节列表失败: {str(e)}")
    
    if not chapters:
        print("无法获取章节列表，请检查小说ID或网络连接。")
        return

    downloaded = load_status(save_path)
    todo_chapters = [ch for ch in chapters if ch["id"] not in downloaded]

    if not todo_chapters:
        print("所有章节已是最新，无需下载")
        return

    print(f"开始下载：《{name}》, 总章节数: {len(chapters)}, 待下载: {len(todo_chapters)}")
    os.makedirs(save_path, exist_ok=True)

    # 写入书籍信息
    output_file_path = os.path.join(save_path, f"{name}.txt")
    if not os.path.exists(output_file_path):
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(f"小说名: {name}\n作者: {author_name}\n内容简介: {description}\n\n")

    # 多线程下载并缓存内容
    content_cache = OrderedDict()
    success_count = 0

    # 顺序下载
    sequential_chapters = todo_chapters[:5]
    for chapter in sequential_chapters:
        result = download_chapter(chapter, headers, save_path, name, downloaded)
        if result:
            index, content = result
            content_cache[index] = (chapter, content)
            success_count += 1

    # 使用多线程下载
    remaining_chapters = todo_chapters[5:]
    with ThreadPoolExecutor(max_workers=CONFIG["max_workers"]) as executor:
        futures = {executor.submit(download_chapter, ch, headers, save_path, name, downloaded): ch for ch in remaining_chapters}
        
        # 使用全局tqdm变量，这样GUI可以覆盖它
        # 修改为直接调用tqdm函数来确保兼容GUI的进度条
        progress_bar = tqdm(total=len(remaining_chapters), desc="下载进度", unit="章")
        for future in as_completed(futures):
            chapter = futures[future]
            try:
                result = future.result()
                if result:
                    index, content = result
                    content_cache[index] = (chapter, content)
                    success_count += 1
            except Exception as e:
                print(f"章节 [{chapter['title']}] 处理失败: {str(e)}")
            finally:
                # 每处理一个章节就更新一次进度条
                progress_bar.update(1)
                progress_bar.refresh()  # 强制刷新进度条
        
        # 确保进度条关闭
        progress_bar.close()

    # 按顺序写入文件
    if content_cache:
        sorted_chapters = sorted(content_cache.items(), key=lambda x: x[0])
        with open(output_file_path, 'a', encoding='utf-8') as f:
            for index, (chapter, content) in sorted_chapters:
                f.write(f"{chapter['title']}\n")
                f.write(content + '\n\n')

    # 保存下载状态
    save_status(save_path, downloaded)

    print(f"下载完成！成功: {success_count}, 失败: {len(todo_chapters)-success_count}")

def main():
    print("""欢迎使用番茄小说下载器精简版！
作者：Dlmos（Dlmily）
Github：https://github.com/Dlmily/Tomato-Novel-Downloader-Lite
赞助/了解新产品：https://afdian.com/a/dlbaokanluntanos
------------------------------------------""")
    
    book_id = input("请输入小说ID：").strip()
    save_path = input("保存路径（留空为当前目录）：").strip() or os.getcwd()

    try:
        Run(book_id, save_path)
    except Exception as e:
        print(f"运行错误: {str(e)}")

if __name__ == "__main__":
    main()
=======
    if not name:
        print("无法获取书籍信息，请检查小说ID或网络连接。")
        return

    # 获取章节列表
    url = f'https://fanqienovel.com/page/{book_id}'
    response = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'lxml')

    li_list = soup.select("div.chapter-item")
    total = len(li_list)
    titles = extract_chatper_titles(soup)

    # 确保保存路径存在
    try:
        save_path = os.path.abspath(save_path)
        os.makedirs(save_path, exist_ok=True)
        print(f"保存路径: {save_path}")
    except Exception as e:
        print(f"创建保存目录失败: {str(e)}")
        return

    try:
        # 如果是TXT格式，创建并写入小说信息
        if OUTPUT_FORMAT == "txt":
            output_file_path = os.path.join(save_path, f"{name}.txt")
            with open(output_file_path, 'w', encoding='utf-8') as f:
                # 写入书籍信息
                f.write(f'小说名: {name}\n作者: {author_name}\n内容简介: {description}\n\n')
        elif OUTPUT_FORMAT == "chapter":
            # 为分章节创建目录
            chapter_dir = os.path.join(save_path, name)
            os.makedirs(chapter_dir, exist_ok=True)
            # 创建书籍信息文件
            info_file = os.path.join(chapter_dir, "书籍信息.txt")
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f'小说名: {name}\n作者: {author_name}\n内容简介: {description}\n')
    except Exception as e:
        print(f"创建初始文件失败: {str(e)}")
        return

    # 使用多线程下载章节
    print(f"使用 {MAX_WORKERS} 个线程下载")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for i, div in enumerate(li_list):
            headers = get_headers()
            futures.append(executor.submit(download_chapter, div, headers, save_path, name, titles, i, total, OUTPUT_FORMAT))
        
        # 使用进度条
        for _ in tqdm(as_completed(futures), total=total, desc="下载进度"):
            pass

    # 如果是EPUB格式，转换TXT到EPUB
    if OUTPUT_FORMAT == "epub":
        try:
            from ebooklib import epub
            print("正在将TXT转换为EPUB...")
            
            # 创建EPUB书籍
            book = epub.EpubBook()
            book.set_identifier(f'fanqie_{book_id}')
            book.set_title(name)
            book.set_language('zh-CN')
            book.add_author(author_name)
            
            # 添加CSS样式
            style = '''
            @namespace epub "http://www.idpf.org/2007/ops";
            body {
                font-family: SimSun, serif;
                line-height: 1.5;
            }
            h1 {
                text-align: center;
                margin-bottom: 1em;
            }
            '''
            nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
            book.add_item(nav_css)
            
            # 添加简介章节
            intro = epub.EpubHtml(title="简介", file_name="intro.xhtml", lang="zh-CN")
            intro.content = f"<h1>简介</h1><p>{description}</p>"
            book.add_item(intro)
            
            # 读取所有章节
            chapters = []
            txt_path = os.path.join(save_path, f"{name}.txt")
            chapter_content = ""
            chapter_title = ""
            chapter_index = 0
            
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    # 跳过书籍信息
                    for _ in range(4):
                        f.readline()
                    
                    for line in f:
                        line = line.strip()
                        if line and line in titles:
                            # 保存上一章节
                            if chapter_title and chapter_content:
                                c = epub.EpubHtml(title=chapter_title, file_name=f'chapter_{chapter_index}.xhtml')
                                c.content = f"<h1>{chapter_title}</h1>{chapter_content.replace(chr(10), '<br/>')}"
                                book.add_item(c)
                                chapters.append(c)
                            
                            # 新章节
                            chapter_title = line
                            chapter_content = ""
                            chapter_index += 1
                        else:
                            if chapter_title:  # 确保我们已经有了章节标题
                                chapter_content += line + "\n"
            except Exception as e:
                print(f"读取TXT文件失败: {str(e)}")
                return
            
            # 添加最后一章
            if chapter_title and chapter_content:
                c = epub.EpubHtml(title=chapter_title, file_name=f'chapter_{chapter_index}.xhtml')
                c.content = f"<h1>{chapter_title}</h1>{chapter_content.replace(chr(10), '<br/>')}"
                book.add_item(c)
                chapters.append(c)
            
            # 添加导航
            book.toc = [intro] + chapters
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # 定义书籍脊柱
            spine = [intro, 'nav'] + chapters
            book.spine = spine
            
            # 写入EPUB文件
            try:
                epub_path = os.path.join(save_path, f"{name}.epub")
                epub.write_epub(epub_path, book, {})
                print(f"EPUB格式已创建: {epub_path}")
            except Exception as e:
                print(f"写入EPUB文件失败: {str(e)}")
        except ImportError:
            print("EPUB转换失败: 缺少ebooklib库。您可以使用 'pip install ebooklib' 安装后重试。")
        except Exception as e:
            print(f"EPUB转换过程中出错: {str(e)}")

    if OUTPUT_FORMAT == "txt":
        print(f"小说已下载到: {os.path.join(save_path, f'{name}.txt')}")
    elif OUTPUT_FORMAT == "chapter":
        print(f"小说已下载到: {os.path.join(save_path, name)}")
    elif OUTPUT_FORMAT == "epub":
        print(f"小说已下载到: {os.path.join(save_path, f'{name}.epub')}")
    
def main():
    book_id = input("欢迎使用番茄小说下载器精简版！\n作者：Dlmos（Dlmily）\n基于DlmOS驱动\nGithub：https://github.com/Dlmily/Tomato-Novel-Downloader-Lite\n参考代码：https://github.com/ying-ck/fanqienovel-downloader/blob/main/src/ref_main.py\n赞助/了解新产品：https://afdian.com/a/dlbaokanluntanos\n\n请输入小说 ID：")
    save_path = input("请输入保存路径：")
    
    Run(book_id, save_path)
    print("下载完成！")

if __name__ == "__main__":
    main()
>>>>>>> 1ecb4f51e6909ebc6583015ecc10efdfed97a261
