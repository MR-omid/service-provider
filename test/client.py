import io
import socket,sys,json,base64
import zipfile
import zlib
from datetime import datetime


token = "K6KrzQxt7eITDXnA7upjfA9pKi6s2OU68ZaBYy1y4+cICR2rq2+eOiIG04aUEam4J0Ku4h/xHp72/OKxn7QcnPQNGTnOTDf2nfv/TUYgQRdVKCZxK+9mftIDXV0w0mrBPGxjjILJD8QAtxIFmqZL5fPyVg3Wznez1O3Heo2osKM="
#data = b'{"data":"modules/crawler/storage/2018-03-11/feb250e0-12c2-4740-ab61-0e0d53f0e014.html","type":0}'
#####commands data####################
log_command_data = b'{"data":{"process_id":"null","limit":10,"offset":0,"orderDirection":"ASC"},"type":"0"}'

module_list_command_data = b'{}'

download_data = b'{"data":"modules/crawler/storage/2018-03-11/feb250e0-12c2-4740-ab61-0e0d53f0e014.html","type":"0"}'

get_configs_command_data = b'{}'

set_configs_command_data = b'{"data":[{"alias": "bing_search", "max": 0, "output": [1], "input": [0], "code": 101, "id": 2548, "active": false, "is_action": false}, {"alias": "bing_api", "max": 0, "output": [1], "input": [0], "code": 102, "id": 2549, "active": false, "is_action": false}, {"alias": "google_search", "max": 0, "output": [1], "input": [0], "code": 105, "id": 2550, "active": true, "is_action": false}, {"alias": "google_api", "max": 0, "output": [1], "input": [0], "code": 106, "id": 2551, "active": true, "is_action": false}, {"alias": "similar_domain", "max": 0, "output": [12], "input": [12], "code": 108, "id": 2552, "active": true, "is_action": false}, {"alias": "whois", "max": 3, "output": [0, 2, 4], "input": [12], "code": 109, "id": 2553, "active": true, "is_action": false}, {"alias": "parser", "max": 0, "output": [1, 2, 3, 4], "input": [0, 9], "code": 110, "id": 2554, "active": true, "is_action": false}, {"alias": "crawler", "max": 0, "output": [9], "input": [1], "code": 111, "id": 2555, "active": true, "is_action": false}, {"alias": "facebook", "max": 0, "output": [0], "input": [0], "code": 112, "id": 2556, "active": true, "is_action": false}, {"alias": "module_list", "max": 0, "output": [0], "input": [0], "code": 0, "id": 2557, "active": true, "is_action": true}, {"alias": "log", "max": 0, "output": [0], "input": [0], "code": 1, "id": 2558, "active": true, "is_action": true}, {"alias": "download", "max": 0, "output": [0], "input": [0], "code": 2, "id": 2559, "active": true, "is_action": true}, {"alias": "get_configs", "max": 0, "output": [0], "input": [0], "code": 3, "id": 2560, "active": true, "is_action": true}, {"alias": "set_configs", "max": 0, "output": [0], "input": [0], "code": 4, "id": 2561, "active": true, "is_action": true}, {"alias": "system_information", "max": 0, "output": [0], "input": [0], "code": 5, "id": 2562, "active": true, "is_action": true}, {"alias": "cancel_process", "max": 0, "output": [0], "input": [0], "code": 6, "id": 2563, "active": true, "is_action": true}],"type":"0"}'

system_information_data = b'{}'

cancel_process_command_data = b'{"data":{"process_id":"null"},"type":"0"}'

########modules data################



facebook_data = b'{"data":{"facebook_id":"neymarjr","method_id":1,"username":"14433273760","password":"DPE14433273760","max_result":10},"type":"0"}'

facebook_data_search = b'{"data":{"term":"fringe","method_id":7,"username":"14433273760","password":"!Q@W#E$R"},' \
                       b'"type":"0"}'

bing_search_data = b'{"data":{"method_id":1,"term":"fringe","max_result":4 },"type":"0"}'

bing_api_data = b'{"data":{"method_id":1,"term":"fringe","max_result":4, "api_key":"5a269d7af54843b0969933c8baf91e0b"},"type":"0"}'

google_search_data = b'{"data":{"method_id":1,"term":"fringe","max_result":1 },"type":"0"}'

google_api_data = b'{"data":{"method_id":1,"term":"fring","max_result":4, "api_key":"005502272161542267996:hmaj0txhxdq\u0635", ' \
                  b'"cse_id":"005502272161542267996:hmaj0txhxdq"},"type":"0"}'

parser_data = b'{"data":{"method_id":2,"region":"IR","on_demand":"[4]","path":"/home/dpe/PycharmProjects/F.SystemAPI.01/modules/crawler/storage/2018-09-02/111a37ec-3976-4313-9831-e0e73621525b.html"},' \
              b'"type":9} '
parser_data1 = b'{"data":{"method_id":1,"content":"the email address is info@peykasa.ir and google.com or https://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python  and' \
               b'the phone number is 09127062377 and ipaddress is 178.189.92.118:3129 <a href = tel:+649446aas1709>61709</a>"},"type":0}'

similar_domain_data = b'{"data":{"domain":"www.co.similar.co.com","method_id":1},"type":0}'

whois_data = b'{"data":{"domain":"time.ir"},"type":0}'
whois_api_data =  b'{"data":{"method_id":4,"domain":"time.com", "api_key":"141e4c24854a48030vb27ce8225f76461"},"type":0}'
ip_loc =  b'{"data":{"method_id":1,"ip":"206.189.222.146", "api_key":"22891424DD"},"type":0}'  # insuffiecient api
ip_loc_isproxy =  b'{"data":{"method_id":2,"ip":"206.189.222.146", "api_key":"02EF404A06"},"type":0}'  # insuffiecient api

twitter_data = b'{"data":{"method_id":2,"user_id":"s0_hail", "consumer_key":"FVwtwnnQhkecUTnbnfxeGbHYJ", "consumer_secret":"y6tvwIIXbvGF6McaZuvgkaFqcZAnJHm3NOnWale6XxUWgHgC3X", "access_key":"922436153638359040-gSnTdp9l10sPEUGQjbctNAMe5SMAWSb","access_secret":"jFA2kjmEXsvfdkmHGw4AdibIkGExNNT6qWHnsSytPuUd8"},"type":0}'

crawler_data = b'{"data":{"method_id":1,"base_url_constraint":"True","url":"https://www.sony.com","depth":0 },"type":"9"}'
insta_data = b'{"data":{"method_id":1,"user_id":"s0_hail","username":"chelsea.naspnetworks", "password":"Hivaithai2" },"type":"0"}'



screenshot_data = b'{"data":{"method_id":1,"url":"http://www.blogfa.com/" },"type":"9"}'
###########################################
#
# f = open("update.zip","rb")
# file_data = f.read()
# f.close()
# file_data = base64.b64encode(file_data)
# modile list {101:'bing_search',102:'bing_api',105:'google_search',106:'google_api',108:'similar_domain',
# 109:'whois',110:'parser',111:'crawler',112:'facebook',0:'moduleList',1:'log',2:'download',3:'get_configs',4:'set_configs',5:'system_information',6:'cancel_process'}
# info params: size:priority:timeout:route:callback:token
module_code, module_version = 7, 'v_1_0'
# body_data = log_command_data
# body_data = b'{"data":{"info":{"code":1001, "alias":"new", "input": [0,1], "output": [0]},"file":"%s"},"type":"0"}' % file_data
download_data_zip =  b'{"data":{"process_id":"aa4251b1f83a4492b4977923b5b35d84"},"type":"9"}'
cancel_data =  b'{"data":{"process_id":"4114fc29486b477f8e806bf115cb84d3"},"type":"9"}'
# modules = [{'data': ip_loc_isproxy, 'code': 115}]
# modules = [{'data': whois_api_data, 'code': 109}]
# modules = [{'data': crawler_data, 'code': 111}]
modules = [{'data': whois_api_data, 'code':109}]
#modules = [{'data': system_information_data, 'code': 5}]

def gzip_compress(data):
    z = zlib.compressobj(-1, zlib.DEFLATED, 31)
    compress_data = z.compress(data) + z.flush()
    return compress_data


def gzip_decompress(data):
    z = zlib.decompressobj(16 + zlib.MAX_WBITS)
    decompress_data = z.decompress(data)
    return decompress_data

for module in modules:
    info = "%s:1:10:%d:%s:%s:%s" % (
    len(gzip_compress(module.get('data'))), module.get('code'), 'v_1_0', base64.b64encode(b"http://192.168.4.135:8000/callback.php").decode(),
    token)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = '127.0.0.1'
    server_port = 8001
    client_socket.connect((server_address, server_port))
    client_socket.sendall(info.encode())
    res = client_socket.recv(1024)
    res = json.loads(res.decode().replace("'", '"'))['status']
    if res == "accept":
        client_socket.sendall(gzip_compress(module.get('data')))
        full_res = b''
        while True:
            try:
                data = client_socket.recv(1024)
                if data:
                    full_res += data
                else:
                    break
            except:
                break
        # print(gzip_decompress(full_res))
    elif res == "reject":
        # print("server rejected")
        pass
    #
    # if True:
    #     import ast
    #     {'muffin': 'lolz', 'foo': 'kitty'}
    #     a = gzip_decompress(full_res)
    #     a= a.decode()
    #     a =        ast.literal_eval(a)
    #     print(type(a))
    #     decode = base64.b64decode(a['data'])
    #     with zipfile.ZipFile(io.BytesIO(decode)) as zf:
    #         # save zip file in vendor/install_module
    #         (zf.extractall(path= '/home/dpe/Desktop/F.SystemAPI1/test/zip'))