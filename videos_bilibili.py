import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import pandas as pd

def clean_illegal_xml_characters(input_string):
    illegal_xml_re = re.compile(u'[\u0000-\u0008\u000B\u000C\u000E-\u001F\uD800-\uDFFF\uFFFE-\uFFFF]')
    return illegal_xml_re.sub('', input_string)

# 设置 Chrome WebDriver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
# 如果不需要浏览器界面，可以使用 Headless 模式
# options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)  # 设置显式等待

# 数据列表，用于存储所有视频信息
data_list = []

try:
    # 访问 Bilibili 用户视频页面
    driver.get('https://space.bilibili.com/429582883/video')
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.small-item')))

    # 翻页循环
    while True:
        # 滚动至页面底部，确保所有元素加载完毕
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # 等待异步内容加载

        # 重新获取视频元素
        videos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.small-item')))

        # 如果实际抓取的视频数量与页面展示的不一致，记录下来
        scraped_videos_count = len(data_list)
        if len(videos) != scraped_videos_count:
            print(f"Warning: expected to scrape {len(videos)} videos, but only got {scraped_videos_count}. Rechecking the page...")

        # 获取视频信息
        try:
            for video in videos:
                # 获取视频封面图片的URL
                cover_img = video.find_element(By.CSS_SELECTOR, 'picture.b-img__inner > img').get_attribute('src')
                # 获取视频标题
                title = video.find_element(By.CSS_SELECTOR, 'a.title').get_attribute('title')
                # 获取视频播放长度
                video_length = video.find_element(By.CSS_SELECTOR, '.length').text
                # 获取播放量
                play_count = video.find_element(By.CSS_SELECTOR, '.play > span').text
                # 获取发布时间
                time_published = video.find_element(By.CSS_SELECTOR, '.time').text.strip()

                # 清洗数据
                title = clean_illegal_xml_characters(title)
                play_count = clean_illegal_xml_characters(play_count)
                time_published = clean_illegal_xml_characters(time_published)

                data_list.append({
                    'Cover Image': cover_img,
                    'Title': title,
                    'Length': video_length,
                    'Play Count': play_count,
                    'Published Time': time_published
                })
        except StaleElementReferenceException:
            print("StaleElementReferenceException caught, retrying...")
            continue

        # 尝试找到并点击“下一页”按钮
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.be-pager-next:not(.be-pager-disabled) > a')))
            # 使用 JavaScript 来访问父元素并检查是否有 'be-pager-disabled' 类
            parent_class = driver.execute_script("return arguments[0].parentNode.className;", next_button)
            if 'be-pager-disabled' in parent_class:
                break
            next_button.click()
        except TimeoutException:
            print("No more pages or 'Next' button not clickable.")
            break

except TimeoutException:
    print("Timed out waiting for page to load.")
finally:
    driver.quit()  # 确保在抓取后关闭驱动

# 将数据列表转换为DataFrame
df = pd.DataFrame(data_list)

# 保存DataFrame到Excel文件
excel_path = r'C:\Users\86132\Desktop\videos_bilibili.xlsx'
try:
    df.to_excel(excel_path, index=False)
    print(f'数据已保存到 {excel_path}')
except Exception as e:
    print(f"Error while saving to Excel: {e}")
