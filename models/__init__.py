import json
from utils import log


def load(path):
    """
    获取路径文件的内容
    """
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        # 修改文件内数据为json格式
        return json.loads(s)


def save(data, path):
    """
    把一个dict 或者 list 写入文件
    """
    # 修改可存储的数据格式
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8') as f:
        # 写入数据
        f.write(s)


class Model(object):
    """
    Model是一个数据基类
    """
    @classmethod
    def db_path(cls):
        """
        获得当前类的数据文件路径
        """
        # cls 表示这个类本身
        classname = cls.__name__
        # 获取以类作为文件名路径的文件
        path = 'data/{}.txt'.format(classname)
        return path

    @classmethod
    def new(cls, form):
        """
        类似于使用js的new，显式的实例化一个类
        """
        m = cls(form)
        return m

    @classmethod
    def all(cls):
        """
        得到当前类存储实例
        """
        # 拿到路径
        path = cls.db_path()
        # 载入数据
        models = load(path)
        # 拿到数据可迭代对象
        ms = [cls.new(m) for m in models]
        return ms

    @classmethod
    def find_by(cls, **kwargs):
        """
        根据数据属性的查找数据的方法
        比如可以通过username查询，也可以通过id查询
        拆解出传输参数的k, v，然后和数据原有的所有属性做匹配，找到以后，返回对应的数据
        """
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        all = cls.all()
        for m in all:
            if v == m.__dict__[k]:
                return m
        return None

    @classmethod
    def find_all(cls, **kwargs):
        """
        根据数据属性的查找数据的方法
        比如可以通过username查询，也可以通过id查询
        拆解出传输参数的k, v，然后和数据原有的所有属性做匹配，找到以后，返回对应的数据
        """
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        all = cls.all()
        data = []
        for m in all:
            if v == m.__dict__[k]:
                data.append(m)
        return data

    def save(self):
        """
        保存数据，如果数据没有id，就添加，如果已经有id，就替换
        """
        # 拿到当前数据的所有数据
        models = self.all()
        # 默认添加最开始的数据下标是 0
        first_index = 0
        # 判断是否已经有id
        if self.__dict__.get('id') is None:
            # 没有id就添加id，
            if len(models) > 0:
                # 如果不是第一个数据，就在数据所有数据后添加
                # log('--models[-1]', models[-1].id)
                self.id = models[-1].id + 1
            else:
                self.id = first_index
            # 添加了id以后，把数据存到models中
            models.append(self)
        else:
            # 如果已经有id，说明这个数据已经存在于数据库中，
            # 就修改数据的 id 值
            index = -1
            # enumerate是python函数，可以把
            for i, m in enumerate(models):
                if m.id == self.id:
                    index = i
                    break
            if index > -1:
                models[index] = self
        # __dict__ 包括所有的属性和值的字典
        l = [m.__dict__ for m in models]
        path = self.db_path()
        save(l, path)

    def __repr__(self):
        """
        返回对象的字符串格式
        """
        # 拿到对象的类名的字符串格式
        classname = self.__class__.__name__
        # 使用（）打印字典的值，以便出现空值可以直接发现
        # 打印所有类内属性的字符串
        # .items() 方法把序列变为可以迭代对象
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        # 遍历时换行 js的join和python的join
        s = '\n'.join(properties)
        # 格式化，类名和对应的数据对应显示
        return '< {}\n{} >\n'.format(classname, s)

