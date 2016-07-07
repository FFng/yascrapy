#!/usr/bin/env python
# coding=utf-8

# FFng
# LeoFufengLi@gmail.com
# 2016-07-06

import settings
import sys
import os
from producer import Producer
from stackoverflow import Worker


reload(sys)
sys.setdefaultencoding("utf-8")
root_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(root_path, ".."))
sys.path.append(os.path.join(root_path, "../.."))
