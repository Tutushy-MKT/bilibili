from drission_page import DrissionPage
from data_recorder import DataRecorder

# 初始化 DrissionPage
drission = DrissionPage()

# 假设你已经通过 drission.page 打开了相应的小红书用户页面
page = drission.page

# 初始化 DataRecorder
r = DataRecorder(file_name='notes_data.xlsx', auto_save=True)

# 定位包含笔记信息的 sections
container = page.ele('.feeds-container')
sections = container.eles('.note-item')

# 初始化 notes 列表来存放所有笔记信息
notes = []

# 遍历所有 section 元素来提取信息
for section in sections:
    # 判断笔记类型
    note_type = "视频" if section.ele('.play-icon', timeout=0) else "图文"

    # 提取笔记链接
    note_link = section.ele('tag:a', timeout=0).link

    # 提取标题
    title = section.ele('.title', timeout=0).text

    # 提取作者和点赞信息
    author_wrapper = section.ele('.author-wrapper')
    author = author_wrapper.ele('tag:a.author').text
    like = author_wrapper.ele('.count').text

    # 构造 note 字典
    note = {
        '作者': author,
        '笔记类型': note_type,
        '标题': title,
        '点赞数': like,
        '笔记链接': note_link
    }

    # 添加到 notes 列表
    notes.append(note)

# 将数据添加到 DataRecorder
r.add_data(notes)

# 保存数据
r.save()
