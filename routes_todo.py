from utils import log
# from models import User
# from models import Message

# 引入todo类
from models.Todo import Todo

import random


def template(name):
    """
    模板处理函数
    """
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def route_index(request):
    """
    主页的处理函数, 返回主页的响应
    """
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
    body = template('index.html')
    r = header + '\r\n' + body
    # log('----route_index', r)
    return r.encode(encoding='utf-8')


def current_user(request):
    """
    验证登录的用户，
    如果没有，就是游客
    """
    # log('====, request', request.cookies)
    session_id = request.cookies.get('user', '')
    log('session_id---', session_id)
    log('----session', session)
    username = session.get(session_id, '【游客】')
    # log('---username', username)
    return username


def random_str():
    """
    设置随机数
    """
    seed = 'asdasdasdasdwqcxcxcxcvcvfgr31wqs'
    s = ''
    for i in range(15):
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def response_with_headers(headers):
    """
    设置cookie情况下的header
    这个时候的headers内容
    Content-Type: text/html
    Set-Cookie: asdsdasdd(session_id 随机数)
    """
    header = 'HTTP/1.1 200 OK\r\n'
    header += ''.join(['{}: {}\r\n'.format(k, v)
                       for k, v in headers.items()])
    return header


def route_login(request):
    """
    登录页面，设置cookie
    """
    # header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
    headers = {
        'Content-Type': 'text/html',
    }
    # 拿到登录用户信息，验证 session
    username = current_user(request)
    # 设置默认值
    if request.method == 'POST':
        # 格式化url传的参数
        form = request.form()
        # 保存登录信息
        u = User.new(form)
        if u.validate_login():
            # 验证登录成功后，设置随机的session到cookie
            session_id = random_str()
            session[session_id] = u.username
            log('---session[session_id]', session[session_id])
            headers['Set-Cookie'] = 'user={}'.format(session_id)
            result = '登录成功'
        else:
            result = '用户名或密码错误'
    else:
        result = ''
    body = template('login.html')
    # 动态替换页面内容
    body = body.replace('{{result}}', result)
    body = body.replace('{{username}}', username)
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_register(request):
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
    if request.method == 'POST':
        form = request.form()
        # log('form-----2', form)
        u = User.new(form)
        # log('---u.validate_register()', u.validate_register())
        if u.validate_register():
            u.save()
            result = '注册成功 <br> <pre>{}</pre>'.format(User.all())
        else:
            result = '用户名长度或密码必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


message_list = []


def route_message(request):
    if request.method == 'POST':
        form = request.form()
        msg = Message.new(form)
        message_list.append(msg)
    body = template('message.html')
    msgs = '<br>'.join([str(m) for m in message_list])
    body = body.replace('{{messages}}', msgs)
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_static(request):
    """
    处理静态文件的函数，不写路由，而是根据参数直接获取
    页面的请求<img src="/static?file=doge.gif"/>
    GET /static?file=doge.gif
    path, query = response_for_path(/static?file=doge.gif)
    path "/static"
    query {
        file:doge.gif
    }
    """
    filename = request.query.get('file', 'doge.gif')
    path = 'static/' + filename
    # 'rb'表示以二进制格式打开
    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n'
        img = header + b'\r\n' + f.read()
        return img


def response_with_headers(headers, code=200):
    """
    生成头部信息
    Content-Type: text/html
    Set-Cookie: asdsdasdd(session_id 随机数)
    """
    header = 'HTTP/1.1 {} OK\r\n'.format(code)
    header += ''.join(['{}: {}\r\n'.format(k, v)
                       for k, v in headers.items()])
    return header


def redirect(url):
    """
    利用浏览器的 302响应的特点，写重定向
    添加一个Location属性
    """
    headers = {
        'Location': url,
    }
    r = response_with_headers(headers, 302) + '\r\n'
    return r.encode('utf-8')


def index(request):
    """
    todo首页，查看所有的todo
    """
    headers = {
        'Content-Type': 'text/html'
    }
    # 拿到 所有todo
    todo_list = Todo.all()
    # 生成todo的html
    todo_html = ''.join(['<h3>{}: {}</h3>'.format(t.id, t.title) for t in todo_list])
    # 替换模板文件中的字符串
    body = template('todo_index.html')
    body = body.replace('{{todos}}', todo_html)
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode(encoding='utf')


def add(request):
    """
    add 功能
    """
    headers = {
        'Content-Type': 'text/html',
    }
    if request.method == 'POST':
        form = request.form()
        t = Todo.new(form)
        # 保存todo到数据库
        t.save()
    # 拿到后端返回的数据后，再重定向到首页，就可以看到新增的数据
    return redirect('/todo')


# todo程序的路由
route_dict = {
    # GET请求
    '/todo': index,
    '/todo/add': add,
}