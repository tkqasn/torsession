#! /usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = "TKQ"

import tornado.web
import tornado.httpserver
import tornado.ioloop
from basehandler import SessionBaseHandler




class MainHandler(SessionBaseHandler):
    def get(self):
        self.write("Memory Session Object Demo:<br/>")
        if "sv" in self.session:
            current_value = self.session["sv"]
        else:
            current_value = 0
        if not current_value:
            self.write("current_value is None(0)<br/>")
            current_value = 1
        else:
            current_value = int(current_value) + 1
        self.write('<br/> Current Value is: %d' % current_value)
        self.session["sv"] = current_value
        print self.session.keys
class DelHandler(SessionBaseHandler):
    def get(self):
        self.write("Memory Session Object Demo:<br/>")
        if "sv" in self.session:
            current_value = self.session["sv"]
            del self.session["sv"]
            self.session["sb"]=1
        # print self.session.keys



app = tornado.web.Application(
    handlers=[(r"/index", MainHandler),
              (r"/del", DelHandler)])


if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8887)
    tornado.ioloop.IOLoop.instance().start()
