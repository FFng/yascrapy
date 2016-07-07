#!/usr/bin/env python
# coding=utf-8

# FFng
# LeoFufengLi@gmail.com
# 2016-07-06

from yascrapy.base import BaseProducer
from yascrapy.request_queue import Request
import random


class Producer(BaseProducer):

    def run(self):
        # 2016-07-06, user amount = 4*9 * 151263 = 5,445,468
        max_page = 151263
        page_counter = 0
        channel = self.rabbitmq_conn.channel()

        for i in xrange(1, max_page + 1):
            url = 'http://stackoverflow.com/users?page=%d&tab=reputation&filter=week' % i
            page_counter += 1
            if page_counter % 1000 == 0:
                print page_counter
            q = random.choice(self.req_queues)
            r = Request(url=url,
                        timeout=15,
                        headers={},
                        crawler_name=self.crawler_name,
                        proxy_name='http_oversea',
                        method='GET',
                        params={},
                        data='')
            q.safe_push(r, channel)

        channel.close()
        self.rabbitmq_conn.close()
