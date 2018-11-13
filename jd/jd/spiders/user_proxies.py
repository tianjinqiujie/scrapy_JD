import requests
import random

url = 'http://proxy.httpdaili.com/apinew.asp?text=true&noinfo=true&sl=10&ddbh=gs921302'
response = requests.get(url)
content = response.text
with open('ipadd.txt', 'w')as f:
    f.write(content)
file = open('./ipadd.txt')
content = file.readline()
mk_ip = 'http://' + content

PROXIES_LIST = [
    mk_ip
    # "http://121.31.103.8:8123",
    # "http://121.234.221.149:3456",
    # "https://123.7.61.8:53281",
    # "https://119.3.20.128:80",
]
