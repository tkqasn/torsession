#! /usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = "TKQ"
import uuid
import datetime
from abc import ABCMeta, abstractmethod


class SessionBase(object):
    __metaclass__ = ABCMeta

    def create_session_id(self):
        """
        :return: 生成随机session id
        """""
        return  uuid.uuid4().hex

    def _set_cookie(self, sessionid_key, expires_days, expires_secs):
        """
        :param expires_days: 超时时间天
        :param expires_secs: 超时时间秒
        :return: 为客户端设置并更新cookie超时时间
        """
        try:
            # 传入过期时间是天数
            if expires_days is not None and not expires_secs:
                # 每次访问更新客户端cookie超时时间，第一次访问则设置超时间
                #将天转化为秒
                self.expires=expires_days*24*60*60
                self.handler.set_cookie(sessionid_key, self.sessionid_str, expires_days=expires_days)
            # 传入过期时间是秒
            if expires_secs:
                self.expires = expires_secs
                expires_secs = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_secs)
                self.handler.set_cookie(sessionid_key, self.sessionid_str, expires=expires_secs)
        except Exception as e:
            raise e

    @abstractmethod
    def __init__(self, handler, expires_times):
        pass

    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def __delitem__(self, key):
        pass

    @abstractmethod
    def __contains__(self, key):
        pass

    @abstractmethod
    def keys(self):
        pass

class SessionFactory(object):
    @staticmethod
    def get_session_obj(handler,**session_settings):
        session_type = session_settings.get("session_type","cache")
        session_type=session_type.lower()
        obj = None
        module_name = "session.%s_session" %session_type
        try:
            # 通过反射,动态导入当前包下的文件名中的类
            # 必须这么写globals(), locals(), ['object']，否则仅导入__init__.py
            modul = __import__(module_name, globals(), locals(), ['object'])
            #反射出文件下面的类
            cls = getattr(modul,"%sSession" % session_type.capitalize())
        except Exception as e:
            raise e
        obj = cls(handler,**session_settings)

        return obj


if __name__ == '__main__':
    print globals()
    print locals()
    print ['object']