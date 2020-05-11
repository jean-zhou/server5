from models import Model


class Todo(Model):
    """
    定义todo类，继承model数据基类
    """
    def __init__(self, form):
        # 定义各种数据自己的属性
        self.id = form.get('id', None)
        self.title = form.get('title', '')