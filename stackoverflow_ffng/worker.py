#!/usr/bin/env python
# coding=utf-8

# FFng
# LeoFufengLi@gmail.com
# 2016-07-06

from yascrapy.base import BaseWorker
import logging
import traceback
from string import strip
from urlparse import parse_qs
from urlparse import urlparse
from lxml import html
from yascrapy.request_queue import Request
from items import *


class Worker(BaseWorker):

    # A callback function for RabbitMQ
    # 给 RabbitMQ 用的回调函数
    def callback(self, channel, method, properties, body):
        resp_key = body
        response, err = self.resp_q.get(resp_key)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        if response is None:
            logging.warning("no match response to response_key %s" % resp_key)
            return
        if self.error_handler.handle_downloader_error(response):
            return
        if self.error_handler.handle_status_error(response):
            return
        logging.info('status code: %s url: %s' %
                     (response.status_code, response.url))
        try:
            item = self.parse(response)
        except Exception, e:
            logging.error("%s:%s:%s" %
                          (response.url, str(e), traceback.print_exc()))
            self.error_handler.handle_page_error(response)
        self.db_handler.update(item)

    def parse(self, response):
        item = None
        # 用户列表
        if 'users?page' in response.url:
            self._user_list_parse(response)
        # 最热提问 Top Questions
        elif 'postType=1' in response.url:
            item = self._questions_parse(response)
        # 最热回答 Top Answers
        elif 'postType=2' in response.url:
            item = self._answers_parse(response)
        # 用户主页
        elif '/users/' in response.url:
            item = self._user_parse(response)
        # 简历页面 CV page
        # 2016-07-07, sample URL: http://stackoverflow.com/cv/praveen
        elif '/cv/' in response.url:
            item = self._careers_parse(response)
        return item

    def _user_parse(self, response):
        item = StackoverflowUserItem()
        # http://stackoverflow.com/users/462627/praveen-kumar
        item['uid'] = int(response.url.split('/')[-2])
        for attr in ['name', 'age', 'member_time', 'last_visit_time', 'visitors',
                     'reputation', 'gold_badge', 'silver_badge', 'bronze_badge']:
            ret_list = response.xpath(getattr(self, attr + '_xpath'))
            if ret_list:
                item[attr] = ret_list.extract()[0]
            else:
                item[attr] = None

        for attr in ['current_position', 'avatar', 'twitter', 'github', 'blog', 'people_helped_number',
                     'last_seen_time', 'careers']:
            ret_list = response.xpath(getattr(self, attr + '_xpath'))
            if ret_list:
                item[attr] = ret_list[0].strip() if isinstance(
                    ret_list[0], str) else ret_list.extract()[0]
            else:
                item[attr] = None

        if item['careers']:
            self.new_task("%s?uid=%d" % (item["careers"], item["uid"]))

        try:
            item['location'] = response.xpath(self.location_xpath)[0].strip()
        except:
            item['location'] = ''
        try:
            item['answers'] = response.xpath(self.answers_xpath)[0].strip()
        except:
            item['answers'] = 0
        try:
            item['questions'] = response.xpath(self.questions_xpath)[1].strip()
        except:
            item['questions'] = 0
        item['name'] = response.xpath(self.name_xpath)[0].strip()
        try:
            item['visitors'] = response.xpath(
                'string(%s)' % self.visitors_xpath)[0].strip()
        except:
            pass

        item['about_me'] = response.xpath(self.about_me_xpath)[0].strip()
        top_questions_url = 'http://stackoverflow.com/users/profile/posts/%d?postType=1&sort=Votes' % item[
            'uid']
        top_answers_url = 'http://stackoverflow.com/users/profile/posts/%d?postType=2&sort=Votes' % item[
            'uid']
        self.new_task(top_questions_url)
        self.new_task(top_answers_url)
        item['top_tags'] = zip(response.xpath(self.top_tags_xpath),
                               map(strip, response.xpath(
                                   self.top_tags_votes_xpath).extract()),
                               map(strip, response.xpath(
                                   self.top_tags_posts_xpath).extract()),
                               )
        item['source'] = 'Desktop'

        for key in item:
            if isinstance(item[key], basestring):
                item[key] = item[key].strip()
            elif isinstance(item[key], list):
                for i in xrange(len(item[key])):
                    try:
                        item[key][i] = (item[key][i][0].strip(),
                                        int(item[key][i][
                                            1].strip().replace(',', '')),
                                        int(item[key][i][
                                            2].strip().replace(',', '')),
                                        )
                    except IndexError:
                        pass

        # 此处将数字字符串转为int
        for attr in ['answers', 'questions', 'gold_badge', 'silver_badge', 'bronze_badge']:
            item[attr] = int(item[attr].replace(',', '')) if item[attr] else 0

        item['reputation'] = int(item['reputation'].replace(',', ''))
        return item

    def _user_list_parse(self, response):
        user_urls = response.xpath(
            '//div[contains(@class, "user-details")]/a/@href').extract()
        for url in user_urls:
            url = 'http://stackoverflow.com%s' % url
            self.new_task(url)

    def _answers_parse(self, response):
        item = StackoverflowUserAnswersItem()
        item['uid'] = int(response.url.split('/')[-1].split('?')[0])
        item['top_answers'] = zip(response.xpath(self.top_answers_xpath).extract(),
                                  response.xpath(self.top_answers_votes_xpath),
                                  response.xpath(
                                      '//*["post-date"]/span/@title').extract()
                                  )
        return item

    def _questions_parse(self, response):
        item = StackoverflowUserQuestionsItem()
        item['uid'] = int(response.url.split('/')[-1].split('?')[0])
        item['top_questions'] = zip(response.xpath(self.top_questions_xpath),
                                    response.xpath(
                                        self.top_questions_votes_xpath),
                                    response.xpath(
                                        '//*["post-date"]/span/@title')
                                    )
        return item

    def _careers_parse(self, response):
        tree = html.fromstring(response.html)
        full_name_xapth = '//*[@id="section-personal"]/div/h1/text()'
        location_xpath = '//*[@id="user-meta"]/li[1]/text()[2]'
        website_xpath = '//*[@id="website"]/a/@href'
        twitter_xpath = '//a[@class="twitter"]/@href'
        tops_xpath = '//*[@class="tags-summary"]/div[@class="subsection"]'
        summary_xpath = '//*[@id="statement"]'
        like_techs_xpath = '//*[@id="technologies"]//div[@class="likes"]/span'
        dislike_techs_xpath = '//*[@id="technologies"]/div[2]/div[2]/div[2]/span'

        jobs_xpath = '//*[@id="cv-experience"]/div[contains(concat(" ", normalize-space(@class), " "), " cv-section ")]'
        educations_xpath = '//*[@id="cv-education"]/div[contains(concat(" ", normalize-space(@class), " "), " cv-section ")]'
        stackexchange_xpath = '//*[@id="stackexchange-accounts"]//div[@class="site"]/a/@href'
        projects_xpath = '//*[contains(concat(" ", normalize-space(@class), " "), " project ")]'
        writings_xpath = '//*[contains(concat(" ", normalize-space(@class), " "), " article ")]'
        readings_xpath = '//div[contains(concat(" ", normalize-space(@class), " "), " book ")]'
        tools_xpath = '//*[@id="cv-other"]/div[2]/p'

        full_name = tree.xpath(full_name_xapth)[0].strip()
        tmps = tree.xpath(location_xpath)[0].strip().split(',', 1)
        location = {
            "city": tmps[0],
            "country": tmps[1]
        }
        website = tree.xpath(website_xpath)[0]
        tmps = tree.xpath(twitter_xpath)
        if len(tmps) > 0:
            twitter = tmps[0]
        else:
            twitter = ""
        # print twitter
        top_nodes = tree.xpath(tops_xpath)
        # print len(top_nodes)
        tops = []
        for top_node in top_nodes:
            percent = top_node.xpath(
                'strong/text()')[0].replace('Top', '').strip()
            tags = []
            spans = top_node.xpath('span')
            for span in spans:
                tags.append(span.text_content())
            tops.append({
                "percent": percent,
                "tags": tags
            })
        # print tops
        summary = tree.xpath(summary_xpath)[0].text_content().strip()
        # print summary
        like_techs = []
        tmps = tree.xpath(like_techs_xpath)
        for tmp in tmps:
            tag = tmp.text_content().strip()
            like_techs.append(tag)
        dislike_techs = []
        try:
            tmps = tree.xpath(dislike_techs_xpath)
        except:
            tmps = []
        # print len(tmps)
        for tmp in tmps:
            tag = tmp.text_content().strip()
            dislike_techs.append(tag)
        # print dislike_techs

        jobs = []
        tmps = tree.xpath(jobs_xpath)
        for tmp in tmps:
            job = {}
            content = tmp.text_content()
            fields = [x.strip() for x in content.split('\n') if x.strip()]
            # print fields
            if "|" in fields[0]:
                work_time = [x.strip()
                             for x in fields[2].split(u'\u2013') if x.strip()]
            else:
                work_time = [x.strip()
                             for x in fields[1].split(u'\u2013') if x.strip()]
            job.update({
                "company": fields[1] if "|" in fields[0] else "",
                "position": fields[0].replace("|", "").strip(),
                "start": work_time[0],
                "end": work_time[1] if len(work_time) > 1 else ""
            })
            if len(fields) >= 5:
                job.update({
                    "tags": fields[3].split(' '),
                    "description": "".join(fields[4:])
                })
            else:
                job.update({
                    "tags": [],
                    "description": ""
                })
            if "company" not in job:
                job.update({"company": ""})
            jobs.append(job)
        # print jobs

        educations = []
        tmps = tree.xpath(educations_xpath)
        for tmp in tmps:
            education = {}
            content = [x.strip()
                       for x in tmp.text_content().split('\n') if x.strip()]
            work_time = [x.strip()
                         for x in content[2].split(u'\u2013') if x.strip()]
            # print content
            education.update({
                "major": content[0].replace("|", "").strip(),
                "school": content[1],
                "tags": content[3].split(" "),
                "description": content[4] if len(content) > 4 else "",
                "start": work_time[0],
                "end": work_time[1]
            })
            educations.append(education)
        # print educations

        stackexchanges = tree.xpath(stackexchange_xpath)
        # print stackexchanges

        projects = []
        tmps = tree.xpath(projects_xpath)
        for tmp in tmps:
            try:
                url = tmp.xpath(
                    'div//a[contains(concat(" ", normalize-space(@class), " "), " open-source ")]/@href')[0]
            except:
                url = ""
            try:
                source = \
                    tmp.xpath(
                        'div//a[contains(concat(" ", normalize-space(@class), " "), " open-source ")]/@title')[0]
            except:
                source = ""
            try:
                tags = tmp.xpath('div//div[@class="tags"]/span/text()')
            except:
                tags = []

            project = {}
            content = [x.strip()
                       for x in tmp.text_content().split('\n') if x.strip()]
            if len(tags) > 0:
                description = "".join(content[3:]) if len(content) > 3 else ""
            else:
                description = "".join(content[2:]) if len(content) > 2 else ""
            project.update({
                "url": url,
                "source": source,
                "tags": tags,
                "title": content[0],
                "description": description
            })
            projects.append(project)
        # print projects

        writings = []
        tmps = tree.xpath(writings_xpath)
        for tmp in tmps:
            try:
                url = tmp.xpath("div//a/@href")[0]
            except:
                url = ""
            content = [x.strip()
                       for x in tmp.text_content().split('\n') if x.strip()]
            # print content
            writings.append({
                "url": url,
                "title": content[0],
                "author": content[1],
                "description": "".join(content[2:]) if len(content) > 2 else ""
            })
        # print writings
        readings = []
        tmps = tree.xpath(readings_xpath)
        # print len(tmps)
        for tmp in tmps:
            try:
                url = tmp.xpath("div//a/@href")[0]
                title = tmp.xpath('div//a/text()')[0]
            except:
                url = ""
                title = ""
            try:
                subtitle = \
                    tmp.xpath(
                        'div//p[contains(concat(" ", normalize-space(@class), " "), " subtitle ")]/text()')[0].strip()
            except:
                subtitle = ""
            try:
                author = tmp.xpath('div//p[contains(concat(" ", normalize-space(@class), " "), " location ")]/text()')[
                    0].strip()
            except:
                author = ""
            try:
                nodes = [x.text_content().strip() for x in
                         tmp.xpath('div//div[contains(concat(" ", normalize-space(@class), " "), " description ")]/p')]
                description = "".join(nodes)
            except:
                description = ""

            readings.append({
                "url": url,
                "subtitle": subtitle,
                "title": title,
                "author": author,
                "description": description
            })
        # print readings

        tools = []
        tmps = tree.xpath(tools_xpath)
        for tmp in tmps:
            content = tmp.text_content().strip().replace("\n", "")
            content = " ".join(content.split())
            tools.append(content)
        # print tools
        item = {
            "full_name": full_name,
            "location": location,
            "website": website,
            "twitter": twitter,
            "stackexchanges": stackexchanges,
            "summary": summary,
            "tops": tops,
            "tops": tops,
            "like_techs": like_techs,
            "dislike_techs": dislike_techs,
            "jobs": jobs,
            "educations": educations,
            "readings": readings,
            "writings": writings,
            "tools": tools,
            "projects": projects
        }
        # print "enter `_careers_parse` function"
        item = StackoverflowCareersItem()
        query = urlparse(response.url).query
        item["uid"] = parse_qs(query)["uid"][0]
        name = response.url.split("/")[-1]
        if "?" in name:
            name = name.split("?")[0]
        item["name"] = name
        for k in item:
            item[k] = item[k]
        return item

    def new_task(self, url):
        self.req_q.safe_push(
            Request(
                url=url, crawler_name=self.crawler_name, proxy_name=self.proxy_name
            ),
            self.publish_channel
        )
