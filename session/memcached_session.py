#! /usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = "TKQ"
from . import SessionBase
import memcache
from functools import wraps
try:
    import cPickle as pickle    # py2
except:
    import pickle               # py3



#单例模式连接池
class MemcachedSession(SessionBase):
    """
    配置信息格式
    settings = {"session_type": "memcached",
            "expires_secs": 60,
            "expires_days": 1,
            "session_server":{
                "host":"192.168.79.131",
                "port":"12000",
                "debug":True}
            }
    """
    sessionid_key = "__sessionId__"

    def __init__(self, handler,**settings):
        self.handler = handler
        self._init_settings( **settings)
        #单例模式创建连接池，如果已经存在，那么实例化的时候就不再创建连接池。
        if not hasattr(MemcachedSession,"MClient_pool"):
            MemcachedSession.MClient_pool=self._create_conn_pool( **self.session_server_dict)

        #从客户端获取__sessionId__的随机字符串:
        client_sessionid = handler.get_cookie(MemcachedSession.sessionid_key, None)

        if client_sessionid and MemcachedSession.MClient_pool.get(client_sessionid):
            self.sessionid_str = client_sessionid

        else:
            self.sessionid_str = self.create_session_id()
            MemcachedSession.MClient_pool.set(self.sessionid_str,{})
            print MemcachedSession.MClient_pool.get(self.sessionid_str)

        #设置或更新客户端的cookie，并更新其超时时间。
        self._set_cookie(MemcachedSession.sessionid_key,self.expires_days,self.expires_secs)
        # 获取并更新memcached缓存时间
        key=MemcachedSession.MClient_pool.get(self.sessionid_str)
        MemcachedSession.MClient_pool.set(self.sessionid_str, key, self.expires)



    def _create_conn_pool(self,**session_server):
        """
         创建memcached连接池
        :param session_server: 连接参数
        :return: 连接池
        """
        host = session_server.pop('host')
        port = session_server.pop('port')
        servers = '%s:%s' % (host, port)
        print "cereate pool"
        return memcache.Client([servers], **session_server)

    def _init_settings(self, **settings):
        """
        :param settings: 配置信息，超时时间，服务器连接字段等
        :return:
        """
        self.expires_secs = settings.get("expires_secs", None)
        self.expires_days = settings.get("expires_days", None)
        self.session_server_dict = settings.get("session_server")

    def __getitem__(self,key):
        ret_dict = MemcachedSession.MClient_pool.get(self.sessionid_str)
        ret = ret_dict.get(key, None)
        return ret

    def __setitem__(self, key, value):
        ret_dict = MemcachedSession.MClient_pool.get(self.sessionid_str)
        ret_dict[key] = value
        MemcachedSession.MClient_pool.set(self.sessionid_str,ret_dict,self.expires)

    def __delitem__(self, key):
        ret_dict = MemcachedSession.MClient_pool.get(self.sessionid_str)
        if key in ret_dict:
            del ret_dict[key]
        MemcachedSession.MClient_pool.set(self.sessionid_str, ret_dict,self.expires)

    def __contains__(self, key):
        ret_dict = MemcachedSession.MClient_pool.get(self.sessionid_str)
        return key in ret_dict

    @property
    def keys(self):
        """
        Return all keys in session object
        """
        ret_dict = MemcachedSession.MClient_pool.get(self.sessionid_str)
        return ret_dict.keys()
