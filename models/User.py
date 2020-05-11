from models import Model


class User(Model):
    """
    继承Models的数据类型后，定义具体的数据处理类型
    """
    def __init__(self, form):
        # log('form----', form)
        self.username = form.get('username', '')
        self.password = form.get('password', '')

    def validate_login(self):
        # return self.username == 'gua' and self.password == '123'
        # 实现真正的登录
        us = User.all()
        for u in us:
            if u.username == self.username and u.password == self.password:
                return True
        return False

    def validate_register(self):
        # log('--self.username, self.password', self.username,'--', self.password)
        return len(self.username) > 2 and len(self.password) > 2
