#! /usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = "TKQ"
from session import SessionFactory
import tornado.web

settings = {"session_type": "redis",
            "expires_secs": 1200,
            "expires_days": 1,
            "session_server":{
                "host":"127.0.0.1",
                "port":"6379",
                }
            }
class SessionBaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session=SessionFactory.get_session_obj(self,**settings)




