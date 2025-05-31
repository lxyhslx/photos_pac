import re
import os
import configparser
import requests
from bs4 import BeautifulSoup
#import time
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
def download_image(url,dir,filename):
    # 创建images目录（跨平台兼容）
    os.makedirs(dir, exist_ok=True)
    
    # 生成时间戳文件名
    #timestamp = int(time.time())
    #filename = f"{timestamp}.jpg"
    save_path = os.path.join(dir, filename)
    
    # 下载图片
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"图片已保存为：{save_path}")
        else:
            print(f"下载失败，HTTP状态码：{response.status_code}")
    except Exception as e:
        print(f"发生错误：{str(e)}")
def load_blacklist(file_path):
    """
    从指定文件加载黑名单词汇
    :param file_path: 文件路径
    :return: 黑名单词汇集合
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        print(f"警告：黑名单文件 {file_path} 未找到")
        return set()

def word_blacklist(text, word_set):
    """
    检查文本是否包含黑名单词汇
    :param text: 待检查文本
    :param word_set: 黑名单词汇集合
    :return: 是否包含黑名单词
    """
    return any(word.lower() in text.lower() for word in word_set)
cf = configparser.ConfigParser()
cf.read('config.ini')
page= cf.get('settings', 'page')
url="https://www.lss77.com/zx/qc/page/" + page
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.3"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    blacklist = load_blacklist('blacklist.txt')
    # 创建下一级目录（若不存在）
    next_dir = os.path.join(os.getcwd(), 'page')
    os.makedirs(next_dir, exist_ok=True)
    images_dir = os.path.join(os.getcwd(), 'images')
    os.makedirs(images_dir, exist_ok=True)
    file_path = os.path.join(next_dir, page + '.ini')
    with open(file_path, 'w', encoding='utf-8') as file:
        infos = soup.find_all('div', class_='entry-media')
        n = 0
        for info in infos:
            n += 1
            cover = re_url(info.find('img').get('data-src'))
            link = info.find('a')['href']
            title = info.find('img').get('alt')
            if word_blacklist(title, blacklist):
                print("⚠️ 文本包含黑名单词汇")
                continue
            else:
                print("✅ 文本通过检查")
            issuer = m_text(title,'[',']').upper()
            pic_num = m_text(title,'[','P').strip()
            pic_date = re_date(title)
            cover_date = pic_date.replace(".", "")
            order = m_text(title,pic_date+' ',' ')
            model = m_text(title, order+' ', '[').strip()
            file.write(f"[{n}]\nlink = {link}\ntitle = {title}\ncover = {cover}\nissuer = {issuer}\ndate = {pic_date}\norder = {order}\nmodel = {model}\nnum = {pic_num}\n")
            issuer_dir = os.path.join(images_dir, issuer)
            os.makedirs(issuer_dir, exist_ok=True)
            model_dir = os.path.join(issuer_dir, model)
            os.makedirs(model_dir, exist_ok=True)
            download_image(cover,model_dir,"cover-"+cover_date+"-"+order+".jpg")


    page = int(page)+1
    cf.set('settings', 'page', str(page))
    with open('config.ini', 'w') as configfile:
        cf.write(configfile)
else:
    print(f"未找到网页，请查看网络连接: {response.status_code}")
