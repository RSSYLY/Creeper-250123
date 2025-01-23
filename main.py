from get_links import get_all_links

import csv
import time
from get_target_text import InfoExtractor  # 替换为实际模块路径

# 配置参数
QUERY_WORDS = "长城"  # 搜索关键词
REQUEST_INTERVAL = 0.1  # 请求间隔(秒)
MAX_RETRIES = 5  # 单条数据最大重试次数


def export_to_csv():
    urls = get_all_links(QUERY_WORDS, REQUEST_INTERVAL, MAX_RETRIES)
    total = len(urls)
    # 打印
    print(f"共获取到 {total} 条链接，开始获取每条链接内容")
    data = []
    for index, url in enumerate(urls, 1):
        try:
            # 带重试机制的请求
            for attempt in range(MAX_RETRIES):
                try:
                    item = InfoExtractor.get_target_data(url)
                    data.append(item)
                    print(f"[{index}/{total}] 成功获取：{url}")
                    break
                except Exception as e:
                    if attempt == MAX_RETRIES - 1:
                        raise
                    wait = REQUEST_INTERVAL * (attempt + 1)
                    print(f"[{index}/{total}] 第{attempt + 1}次重试 ({url})，等待{wait}秒...")
                    time.sleep(wait)

        except Exception as e:
            print(f"[{index}/{total}] 最终失败 {url}：{str(e)}")
            continue

        # 遵守请求间隔
        if index < total:
            time.sleep(REQUEST_INTERVAL)

    # 写入CSV（保持原有代码不变）
    if data:
        with open('output.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                'table_field1',
                'table_field2',
                'table_field3',
                'div_content'
            ])
            writer.writeheader()
            writer.writerows(data)
        print(f"成功导出 {len(data)} 条数据，失败 {len(urls) - len(data)} 条，导出文件在程序运行目录")
    else:
        print("无有效数据可导出")


if __name__ == "__main__":
    start = time.time()
    export_to_csv()
    print(f"总耗时：{time.time() - start:.2f}秒")
