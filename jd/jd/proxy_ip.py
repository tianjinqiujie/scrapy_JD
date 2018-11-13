import random
import requests


class ProxyMiddleware(object):

   ip_list = []
    
   def get_ip(self):
       ret = requests.get("http://proxy.httpdaili.com/apinew.asp?text=true&noinfo=true&sl=10&ddbh=gs921302&tdsourcetag=s_pctim_aiomsg")  # 你需要的网址
       ret.encoding = "UTF-8"
       return ret.text

   def verification(self, ip):
       ret = requests.get('http://www.baidu.com', timeout=3,
                          proxies={"https": "https://{}".format(ip)})

       if ret.status_code == 200:
           return ip
       return

   def process_request(self, request, spider):
       ret = self.get_ip().split("\r\n")
       ret_ip = random.choice(ret)
       ret_ip = self.verification(ret_ip)
       if ret_ip:
           self.ip_list.append(ret_ip)
       #return self.ip_list
