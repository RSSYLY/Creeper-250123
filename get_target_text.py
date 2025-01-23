import requests
from bs4 import BeautifulSoup


class InfoExtractor:
    @staticmethod
    def get_target_data(url):
        """
        从指定URL提取结构化数据
        :param url: 网页URL
        :return: 包含四个字段的字典对象
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # 处理编码
            response.encoding = response.apparent_encoding
            if response.encoding.lower() != 'utf-8':
                response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            # 初始化结果字典
            result = {
                'table_field1': '',
                'table_field2': '',
                'table_field3': '',
                'div_content': ''
            }

            # 提取表格数据
            table = soup.select_one(
                '#barrierfree_container div.zwxxgk_box div.scroll_main1 '
                'div > div > table'
            )

            if table:
                targets = [(2, 2), (3, 2), (1, 4)]
                table_fields = []

                for row, col in targets:
                    try:
                        tr = table.find_all('tr')[row - 1]
                        td = tr.find_all('td')[col - 1]
                        table_fields.append(td.get_text(strip=True))
                    except (IndexError, AttributeError):
                        table_fields.append('')

                # 更新表格字段
                result.update({
                    'table_field1': table_fields[0],
                    'table_field2': table_fields[1],
                    'table_field3': table_fields[2]
                })

            # 提取新增的div内容
            div_content = soup.select_one(
                '#barrierfree_container > div.zwxxgk_box > div.scroll_main1 > div > div > div'
            )

            if div_content:
                result['div_content'] = div_content.get_text(' ', strip=True)

            return result

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return {k: '' for k in result}  # 返回空字典
        except Exception as e:
            print(f"解析失败: {e}")
            return {k: '' for k in result}


# 使用示例
if __name__ == "__main__":
    test_url = "http://www.ncha.gov.cn/art/2017/5/23/art_2237_25498.html"  # 替换实际URL
    data = InfoExtractor.get_target_data(test_url)
    print("提取结果：")
    for key, value in data.items():
        print(f"{key}: {value}")