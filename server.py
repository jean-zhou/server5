import socket
import urllib.parse

from utils import log

# from routes import route_dict
# from routes import route_static
# todo路由程序
from routes_todo import route_dict as todo_route


class Request(object):
    """
    定义请求的类
    """
    def __init__(self):
        """
        类的属性
        """
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.headers = {}
        self.cookies = {}

    def add_cookies(self):
        """
        前端请求的对象中已经有cookie，给请求对象设置cookie属性
        """
        # 第一次登录没有 cookie的时候，就置为空值
        cookies = self.headers.get('Cookie', '')
        log('----cookies', cookies)
        # 拆分出cookie
        kvs = cookies.split('; ')
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self, header):
        """
        拆解出headers内部的属性
        """
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        # 获取新的请求的header后，清除上一次存储的的cookies，
        self.cookies = {}
        self.add_cookies()

    def form(self):
        """
        格式化body内容，解析为字典并返回
        body格式：a=b&c=d&e=1
        """
        body = urllib.parse.unquote(self.body)
        args = body.split('&')
        # log('body.split(--)', body.split('&'))
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
            # log('---f[k] = v', f)
        return f


# 实例化请求内容
request = Request()


def error(request, code=404):
    """
    定义错误页面
    """
    e = {
        404: b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1> NOT FOUND</h1>'
    }
    # 如果code为404，则调用此函数，如果不是，则为空参数
    return e.get(code, b'')


def parsed_path(path):
    """
    解析path的path和query
    """
    # 如果没有query，就默认为空
    index = path.find('?')
    if index == -1:
        return path, {}
    # 是否可以不写else
    path, query_string = path.split('?', 1)
    args = query_string.split('&')
    query = {}
    for arg in args:
        k, v = arg.split('=')
        query[k] = v
    return path, query


def response_for_path(path):
    path, query = parsed_path(path)
    # 设置request的path和query
    request.path = path
    request.query = query
    # 根据routes返回对应的内容
    r = {        # '/static': route_static
        # '/': route_index,
    }
    # 更新todo的routes
    r.update(todo_route)
    # 设置返回的内容
    response = r.get(path, error)
    # log('--进入responese for path', response)
    return response(request)


def run(host='', port=3000):
    """
    启动服务器
    """
    with socket.socket() as s:
        s.bind((host, port))
        while True:
            s.listen(5)
            connection, address = s.accept()
            # 获取请求
            r = connection.recv(1000)
            r = r.decode('utf-8')
            # 防止chrome发送空请求，程序崩溃
            if len(r.split()) < 2:
                continue
            # 请求头：GET /masdsd HTTP/1.1
            request.method = r.split()[0]
            # 解析header头部信息
            request.add_headers(r.split('\r\n\r\n', 1)[0].split('\r\n')[1:])
            request.body = r.split('\r\n\r\n', 1)[1]
            # 解析请求的路径
            path = r.split()[1]
            # 拿到path对应的内容
            response = response_for_path(path)
            # 响应发给客户端
            # log('----response ----', response)
            connection.sendall(response)
            # 处理完请求，关闭连接
            connection.close()


if __name__ == '__main__':
    """
    服务器
    """
    config = dict(
        host='',
        port=3000,
    )
    run(**config)

