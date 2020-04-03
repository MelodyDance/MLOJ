
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

# 新建数据库对象
db = SQLAlchemy()
# 新建 login_manager 对象
login_manager = LoginManager()


# 定义login_manager对象需要的 加载用户的方法
@login_manager.user_loader
def load_user(uid):
	from models import UserTable
	return UserTable.query.get(int(uid))



# # 这个应该是定义：用户未登录时应该跳转的页面
# login_manager.login_view = 'login'
# # login_manager.login_message = 'Your custom message'
# login_manager.login_message_category = 'warning'


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return jsonify(code = 36,message = 'user unauthorized,please login')