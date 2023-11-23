# -*- coding: utf-8 -*-

import sys
import threading

if sys.version_info < (3, 0, 0):
    pass
else:
    pass

from wsgiref.simple_server import make_server
from mdx_util import *
from mdict_query import IndexBuilder
from loguru import logger

content_type_map = {
    'html': 'text/html; charset=utf-8',
    'js': 'application/x-javascript',
    'ico': 'image/x-icon',
    'css': 'text/css',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'mp3': 'audio/mpeg',
    'mp4': 'audio/mp4',
    'wav': 'audio/wav',
    'spx': 'audio/ogg',
    'ogg': 'audio/ogg',
    'eot': 'font/opentype',
    'svg': 'text/xml',
    'ttf': 'application/x-font-ttf',
    'woff': 'application/x-font-woff',
    'woff2': 'application/font-woff2',
}

base_path = os.path.dirname(os.path.abspath(__file__))
resource_path = os.path.join(base_path, 'mdx')
logger.info("resource_path: {}", resource_path)
builder = None


def get_url_map():
    result = {}
    files = []

    # resource_path = '/mdx'
    file_util_get_files(resource_path, files)
    for p in files:
        if file_util_get_ext(p) in content_type_map:
            p = p.replace('\\', '/')
            result[re.match('.*?/mdx(/.*)', p).groups()[0]] = p
    return result


def application(environ, start_response):
    path_info = environ['PATH_INFO'].encode('iso8859-1').decode('utf-8')
    m = re.match('/(.*)', path_info)
    word = ''
    if m is not None:
        word = m.groups()[0]
    try:
        return serve_content(path_info, start_response)
    except EntryNotFoundError as e:
        return [e.args[0].encode('utf-8')]


def serve_content(path_info, start_response):
    url_map = get_url_map()

    if path_info in url_map:
        url_file = url_map[path_info]
        content_type = content_type_map.get(file_util_get_ext(url_file), 'text/html; charset=utf-8')
        start_response('200 OK', [('Content-Type', content_type)])
        return [file_util_read_byte(url_file)]
    elif file_util_get_ext(path_info) in content_type_map:
        content_type = content_type_map.get(file_util_get_ext(path_info), 'text/html; charset=utf-8')
        start_response('200 OK', [('Content-Type', content_type)])
        return get_definition_mdd(path_info, builder)
    else:
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        return get_definition_mdx(path_info[1:], builder)

    # start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    # return [b'<h1>WSGIServer ok!</h1>']


# 新线程执行的代码
def loop(port=8000):
    # 创建一个服务器，IP地址为空，端口是8000，处理函数是application:
    httpd = make_server('', port, application)
    logger.info("Serving HTTP on port {}...", port)
    # 开始监听HTTP请求:
    httpd.serve_forever()


if __name__ == '__main__':
    from config import settings

    mdx_file = os.path.join(settings.base_dir, settings.filename)
    builder = IndexBuilder(mdx_file)
    t = threading.Thread(target=loop, args=(settings.port,))
    t.start()
    t.join()
