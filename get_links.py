import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import time

# 配置参数
BASE_URL = "http://www.ncha.gov.cn/jsearch/search.do"
STOP_TEXT = "找不到和您的查询"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_page(url, params, interval,max_retries):
    for attempt in range(max_retries + 1):  # 包含初始请求的总尝试次数
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"请求失败，第{attempt + 1}次尝试: {e}")
            if attempt < max_retries:
                print(f"将在 {max_retries - attempt} 次后重试...")
                time.sleep(interval)  # 添加重试间隔，避免频繁请求
    print(f"已达到最大重试次数（{max_retries}次），放弃请求")
    return None

def should_stop(html):
    soup = BeautifulSoup(html, "lxml")
    stop_element = soup.select_one("td.js-result > div > p:nth-child(1)")
    return stop_element and STOP_TEXT in stop_element.get_text()

def extract_links(html):
    soup = BeautifulSoup(html, 'lxml')
    links = []

    body = soup.find('body')
    if not body:
        return links

    target_table = None
    count = 0
    for child in body.children:
        if isinstance(child, Tag):
            count += 1
            if count == 7:
                if child.name == 'table':
                    target_table = child
                break

    if not target_table:
        return links

    td_js_result = target_table.select_one('tbody > tr > td.js-result')
    if not td_js_result:
        return links

    filtered_children = [
        child for child in td_js_result.find_all(recursive=False)
        if 'jsearchhuismall' not in child.get('class', []) and child.name == 'table'
    ]

    if filtered_children:
        filtered_children.pop()

    for child in filtered_children:
        a_tags = child.select('table tbody tr:first-child td.jsearchblue a[href]')
        for a in a_tags:
            links.append(a['href'])
    return links

def get_all_links(search_keyword, interval=5, max_retries=3):
    all_links = []
    current_page = 1

    # 构造本地请求参数
    local_params = {
        "appid": "1",
        "ck": "x",
        "colgroup": "1963,2048,2234,2235,2236,2237,2238,2318",
        "od": "1",
        "pagemode": "result",
        "pg": "10",
        "pos": "title,content",
        "q": search_keyword,
        "qq": "",
        "style": "3",
        "tmp_od": "0",
        "x": "55",
        "y": "11",
        "p": current_page
    }

    while True:
        local_params["p"] = current_page
        html = get_page(BASE_URL, params=local_params,interval=interval, max_retries=max_retries)
        print(f"请求第 {current_page} 页: {BASE_URL}?{urlencode(local_params)}")

        if not html:
            break

        if should_stop(html):
            print("到达最后一页，停止翻页")
            break

        page_links = extract_links(html)
        if not page_links:
            print("当前页没有找到有效链接")
            break

        all_links.extend(page_links)
        current_page += 1
        time.sleep(interval)

    return all_links

if __name__ == "__main__":
    # 示例用法：传递搜索关键词、间隔和最大重试次数
    result_links = get_all_links("隋大兴唐长安城", interval=1, max_retries=5)
    print("\n所有提取的链接：")
    print(result_links)
    print(f"总共提取到 {len(result_links)} 条链接")