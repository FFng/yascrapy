#!/usr/bin/env python
# coding=utf-8

# FFng
# LeoFufengLi@gmail.com
# 2016-07-06

from items import *

crawler_name = 'stackoverflow_ffng'
proxy_name = 'http_oversea'
html_404_strings = [['Page', 'Not', 'Found'], ]
bloomd_capacity = 1e8
bloomd_error_rate = 1e-5
request_queue_count = 6
response_queue_count = 5


# mongo plugin settings
domain = 'http://stackoverflow.com'
db_name = 'stackoverflow_2016_07_06'

mongo_ip = "192.168.0.101"
mongo_port = 27017
plugins = [
    "yascrapy.plugins.mongo",
    "yascrapy.plugins.handle_error",
    "yascrapy.plugins.handle_proxy",
]

mongo_tables = [
    {'name': 'users', 'index': 'uid', 'type': StackoverflowUserItem},
    {'name': 'careers', 'index': 'uid', 'type': StackoverflowCareersItem},
    {'name': 'questions', 'index': 'uid',
        'type': StackoverflowUserQuestionsItem},
    {'name': 'answers', 'index': 'uid',
        'type': StackoverflowUserAnswersItem}
]

test_urls = ["http://stackoverflow.com/users/462627/praveen-kumar"]


# all xpath strings
# sample URL:
# 1. http://stackoverflow.com/users/462627/praveen-kumar
# 2. http://stackoverflow.com/users/6309/vonc

# 1. 基础信息
# 1.01 邮箱

# 1.02 电话

# 1.03 头像
avatar_xpath = '//div[contains(@class, "avatar")]/img/@src'
# 1.04 用户名
user_name_xpath = '//h2[@class="user-card-name"]/text()[1]'
# 1.05 性别

# 1.06 出生年月

# 1.07 居住地/城市
location_xpath = '//span[@class="icon-location"]/../text()'
# 1.08 个性签名
bio_xpath = 'string(//div[@class="bio"])'
# 1.09 所在行业 -> current_position 当前职位
current_position_xpath = '//div[@class="current-position"]/text()'


# 2. 站点特性
# 2.01	加入站点时间长度
member_since_xpath = '//*[text()[contains(., "Member for")]]/span[@title]/@title'
# 2.02	主页被浏览量
profile_views = '//span[contains(@class, "icon-eye")]/../text()'
# 2.03 最近登录时间
last_seen_xpath = '//span[@class="icon-time"]/../span[@title]/@title'
# 2.04	回答数
answers_xpath = '//div[contains(@class, "stat answers")]/span[@class="number"]'
# 2.05	提问数
questions_xpath = '//div[contains(@class, "stat questions")]/span[@class="number"]'
# 2.06	影响了多少人
people_helped_xpath = '//*[contains(@class, "people-helped")]/span[@class="number"]/text()'
# 2.07	最热标签 【标签名】【分数】【回答次数】
top_tag = '//div[@class="tag-container row"][1]//a[@class="post-tag"]'
top_tag_score = '//div[@class="tag-container row"][1]//span[text()="Score"]/../text()'
top_tag_posts = '//div[@class="tag-container row"][1]//span[text()="Posts"]/../text()'
top_tag_list = '//div[@class="tag-container row"]//a[@class="post-tag"]'
top_tag_score_list = '//div[@class="tag-container row"]//span[text()="Score"]/../text()'
top_tags_post_list = '//div[@class="tag-container row"]//span[text()="Posts"]/../text()'

# 2.08	勋章
#  2.08.01	金牌数
gold_badge_xpath = '//span[@class="badge1-alternate"]/span[@class="badgecount"]'
# 2.08.02	银牌数
silver_badge_xpath = '//span[@class="badge2-alternate"]/span[@class="badgecount"]'
# 2.08.03 铜牌数
bronze_badge_xpath = '//span[@class="badge3-alternate"]/span[@class="badgecount"]'
# 2.09	最热回答和提问（T5）	【标题】【点赞】【时间】【类型】
# 最热提问和最热回答是2个动态请求，可以用 URL 中的`PostType=1 or =2`判断
# 2.09.01 最热提问(Top 5)
top_questions_title_list_xpath = '//div[@class="row post-container"][position()<=5]/a'
top_questions_link_list_xpath = '//div[@class="row post-container"][position()<=5]/a/@href'
top_questions_date_list_xpath = '//div[@class="row post-container"][position()<=5]/span[@class="post-date"]/span/@title'
top_questions_vote_list_xpath = '//div[@class="row post-container"][position()<=5]/span[@class="vote accepted"]'

# 2.09.02 最热回答(Top 5)
top_answers_title_list_xpath = '//div[@class="row post-container"][position()<=5]/a'
top_answers_link_list_xpath = '//div[@class="row post-container"][position()<=5]/a/@href'
top_answers_date_list_xpath = '//div[@class="row post-container"][position()<=5]/span[@class="post-date"]/span/@title'
top_answers_vote_list_xpath = '//div[@class="row post-container"][position()<=5]/span[@class="vote accepted"]'

# 2.10	StackOverflow 简历
# 这是指向当前用户的CV的链接
CV_page_xpath = '//div[contains(@class, "with-careers")]/a/@href'

# 3. 站点关联
# 3.01 blog
blog_xpath = '//span[@class="icon-site"]/../a/@href'
# 3.02	Twitter
twitter_xpath = '//span[@class="icon-twitter"]/../a/@href'
# 3.03	GitHub
github_xpath = '//span[@class="icon-github"]/../a/@href'


# 4. 简历表字段
# sample URL:
# 1. http://stackoverflow.com/cv/praveen
# 2. http://stackoverflow.com/cv/vonc

# 4.1.	自我介绍
statement = '//div[@id="statement"]'
# 4.2.	工作经历:
# 4.2.01	公司名称
# 4.2.02	部门/职位
# 4.2.03	职位描述
# 4.2.04	入职时间
# 4.2.05	离职时间
# 4.3.	教育经历:
# 4.3.01	学校名称
# 4.3.02	专业/院系
# 4.3.03	学历
# 4.3.04	入学时间
# 4.3.05	（预）毕业时间
# 4.4.	奖项荣誉:
# 4.4.01	奖项名称
# 4.4.02	获奖时间
# 4.4.03	详细描述
# 4.5.	项目经历:
# 4.5.01	项目名称
# 4.5.02	扮演职责
# 4.5.03	在职时间
# 4.5.04	详细描述
# 4.6.	其他信息
# 4.6.01 简历表中的姓名
CV_name_xpath = '//div[@id="section-personal"]//h1/text()'
# 4.6.02 求职意向
CV_tech_likes_xpath = '//div[@class="likes"]/span/text()'


educations_xpath = '//*[@id="cv-education"]/div[contains(concat(" ", normalize-space(@class), " "), " cv-section ")]'
stackexchange_xpath = '//*[@id="stackexchange-accounts"]//div[@class="site"]/a/@href'
projects_xpath = '//*[contains(concat(" ", normalize-space(@class), " "), " project ")]'
writings_xpath = '//*[contains(concat(" ", normalize-space(@class), " "), " article ")]'
readings_xpath = '//div[contains(concat(" ", normalize-space(@class), " "), " book ")]'
tools_xpath = '//*[@id="cv-other"]/div[2]/p'
