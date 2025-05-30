import re
import requests
from bs4 import BeautifulSoup
def m_text(text, start_str, end_str):
    return text.split(start_str)[1].split(end_str)[0]
def re_url(url):
    #移除URL中的图片尺寸参数（如-700x1050）
    return re.sub(r'-\d+x\d+(?=\.\w+$)', '', url)
def re_date(text):
    #提取日期格式 YYYY.MM.DD
    match = re.search(r'\d{4}.\d{2}.\d{2}', text)
    if match:
        return match.group()
    else:
        None
url="https://www.lss77.com/zx/qc/page/2"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.3"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    with open('log.txt', 'w', encoding='utf-8') as file:
        infos = soup.find_all('div', class_='entry-media')
        for info in infos:
            cover = re_url(info.find('img').get('data-src'))
            link = info.find('a')['href']
            title = info.find('img').get('alt')
            issuer = m_text(title,'[',']')
            pic_num = m_text(title,' [','P')
            pic_date = re_date(title)
            order = m_text(title,pic_date+' ',' ')
            people = m_text(title, order+' ', ' [')
            file.write(f"链接: {link}\n标题: {title}\n封面: {cover}\n发行机构: {issuer}\n发行时间: {pic_date}\n序列号: {order}\n模特: {people}\n图片数量: {pic_num}\n")
            print(f"链接: {link}\n标题: {title}\n封面: {cover}\n发行机构: {issuer}\n发行时间: {pic_date}\n序列号: {order}\n模特: {people}\n图片数量: {pic_num}\n")
else:
    print(f"未找到网页，请查看网络连接: {response.status_code}")
