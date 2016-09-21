#! /usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = "TKQ"


from . import SessionBase
import time

class CacheSession(SessionBase):
    '''
    配置信息格式
    settings = {"session_type": "cache",
                "expires_secs": 60,
                "expires_days": 1,
                }
    '''
    #内存中最大存储的cookie数量。防止无限增大耗尽内存。
    MAX_COOKIES=1200
    session_container = {}
    sessionid_key = "__sessionId__"

    def __init__(self, handler,**settings):
        self.handler = handler
        self._init_settings( **settings)
        #从客户端获取__sessionId__的随机字符串:
        client_sessionid = handler.get_cookie(CacheSession.sessionid_key, None)
        if client_sessionid and client_sessionid in CacheSession.session_container:
            self.sessionid_str = client_sessionid
        else:
            self.sessionid_str = self.create_session_id()
            CacheSession.session_container[self.sessionid_str] = {}
        #设置或更新客户端的cookie，并更新其超时时间。
        self._set_cookie(CacheSession.sessionid_key,self.expires_days,self.expires_secs)
        CacheSession.session_container[self.sessionid_str]["insert_time"]=time.time()
        print len(CacheSession.session_container)
        print CacheSession.session_container

    def _init_settings(self, **settings):
        """
        :param settings: 配置信息，超时时间，服务器连接字段等
        :return:
        """
        self.expires_secs = settings.get("expires_secs", None)
        self.expires_days = settings.get("expires_days", None)



    def _clear_sessions(self):
        """
        清空缓存容器中过期的session。
        :return:
        """
        print "clearing"
        for key,val in CacheSession.session_container.items():
            alive_time = time.time()-CacheSession.session_container[key].get("insert_time")
            print alive_time
            if alive_time > self.expires:
                del CacheSession.session_container[key]

    def __getitem__(self, key):
        ret = CacheSession.session_container[self.sessionid_str].get(key, None)
        return ret

    def __setitem__(self, key, value):
        CacheSession.session_container[self.sessionid_str][key] = value
        if len(CacheSession.session_container)>CacheSession.MAX_COOKIES:
            self._clear_sessions()

    def __delitem__(self, key):
        if key in CacheSession.session_container[self.sessionid_str]:
            del CacheSession.session_container[self.sessionid_str][key]

    def __contains__(self, key):
        return key in self.session_container[self.sessionid_str]

    @property
    def keys(self):
        """
        Return all keys in session object
        """
        return self.session_container[self.sessionid_str].keys()
