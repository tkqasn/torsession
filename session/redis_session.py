#! /usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = "TKQ"
from . import SessionBase
import redis

#单例模式连接池
class RedisSession(SessionBase):
    """
    配置信息：
    settings = {"session_type": "redis",
            "expires_secs": 1200,
            "expires_days": 1,
            "session_server":{
                "host":"127.0.0.1",
                "port":"6379",
                }
            }
    """

    sessionid_key = "__sessionId__"

    def __init__(self, handler,**settings):
        self.handler = handler
        self._init_settings( **settings)
        #单例模式创建连接池，如果已经存在，那么实例化的时候就不再创建连接池。
        if not hasattr(RedisSession,"conn_pool"):
            RedisSession.conn_pool=self._create_conn_pool( **self.session_server_dict)

        #从客户端获取__sessionId__的随机字符串:
        client_sessionid = handler.get_cookie(RedisSession.sessionid_key, None)

        if client_sessionid and RedisSession.conn_pool.exists(client_sessionid):
            self.sessionid_str = client_sessionid

        else:
            self.sessionid_str = self.create_session_id()
            #在redis中创建空的hash值,先设置{"None","None"}，再删除None.就创建了个空字典
            RedisSession.conn_pool.hset(self.sessionid_str,None,None)
            RedisSession.conn_pool.hdel(self.sessionid_str,None)
            print RedisSession.conn_pool.hgetall(self.sessionid_str)
            print self.sessionid_str

        #设置或更新客户端的cookie，并更新其超时时间。
        self._set_cookie(RedisSession.sessionid_key,self.expires_days,self.expires_secs)
        # 获取并更新memcached缓存时间
        RedisSession.conn_pool.expire(self.sessionid_str,  self.expires)



    def _create_conn_pool(self,**session_server):
        """
         创建redis连接池
        :param session_server: 连接参数
        :return: 连接池
        """
        host = session_server.pop('host')
        port = session_server.pop('port')
        print "cereate pool"
        pool = redis.ConnectionPool(host=host, port=port)
        con_pool = redis.Redis(connection_pool=pool)
        return con_pool

    def _init_settings(self, **settings):
        """
        :param settings: 配置信息，超时时间，服务器连接字段等
        :return:
        """
        self.expires_secs = settings.get("expires_secs", None)
        self.expires_days = settings.get("expires_days", None)
        self.session_server_dict = settings.get("session_server")

    def __getitem__(self,key):
        ret = RedisSession.conn_pool.hget(self.sessionid_str,key)
        return ret

    def __setitem__(self, key, value):
        print key,value
        RedisSession.conn_pool.hset(self.sessionid_str,key,value)
        print "set key"

    def __delitem__(self, key):
        RedisSession.conn_pool.hdel(self.sessionid_str, key)

    def __contains__(self, key):
        ret = RedisSession.conn_pool.hexists(self.sessionid_str,key)
        return ret


    @property
    def keys(self):
        """
        Return all keys in session object
        """
        ret_dict = RedisSession.conn_pool.hgetall(self.sessionid_str)
        return ret_dict
