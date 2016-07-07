#!/usr/bin/env python
# coding=utf-8

# FFng
# LeoFufengLi@gmail.com
# 2016-07-06


# User basic information
# 基础信息
class StackoverflowUserItem(dict):

    uid = None
    name = None  # 1.04 用户名
    avatar = None  # 1.03 头像
    login = None
    location = None  # 1.07 居住地/城市
    age = None  # 1.06 出生年月
    member_time = None  # 2.01 加入站点时间长度
    last_visit_time = None  # 2.03 最近登陆时间
    visitors = None  # 2.02 主页被浏览量
    bio = None  # 1.08 个性签名
    reputation = None
    gold_badge = None  # 2.08.01 金牌数
    silver_badge = None  # 2.08.02 银牌数
    bronze_badge = None  # 2.08.03 铜牌数
    answers = None  # 2.04 回答数
    questions = None  # 2.05 提问数
    top_tags = None  # 2.07 最热标签
    source = None
    github = None  # 3.03 GitHub
    twitter = None  # 3.02 Twitter
    blog = None  # 3.01 blog
    current_position = None
    people_helped_number = None  #
    last_seen_time = None
    careers = None  # 1.09 所在行业


class StackoverflowUserAnswersItem(dict):
    uid = None
    top_answers = None


class StackoverflowUserQuestionsItem(dict):
    uid = None
    top_questions = None


class StackoverflowQuestionItem(dict):
    uid = None
    rank = None
    title = None
    tags = None
    author_name = None
    author_uri = None
    author_uid = None
    link = None
    published = None
    updated = None
    content = None
    answers = None


class StackoverflowCareersItem(dict):
    uid = None
    name = None
    full_name = None
    location = None
    website = None
    twitter = None
    stackexchanges = None
    current_job = None
    summary =None
    tops = None
    like_techs = None
    dislike_techs = None
    jobs = None
    educations = None
    readings = None
    tools = None
    projects = None
    writings = None
