import os
import sys
import json
import time
import click
from flask import Flask,request,abort
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api,Resource,fields,marshal_with,marshal_with_field,reqparse
from flask_login import LoginManager,UserMixin,login_user, logout_user, current_user, login_required
from models import UserTable,CourseTable,HomeworkTable,UserHomeworkTable
from extensions import db,login_manager
from settings import config
# 获取配置文件中定义的资源目录
RESOURCES_FOLDER = config['RESOURCES_FOLDER']

'''
资源操作相关API
'''

# /api/courses
class CourcesAPI(Resource):
	# 设定course对象的字典格式
	course_fields={
		'cid':fields.Integer,
		'course_name':fields.String,
		'course_desc':fields.String,
		'course_begin_time':fields.Integer,
		# 由于course与courseware是一对多关系，一个course对应多个courseware，course对象会存储对应的courseware组成的数组
		'coursewares':fields.List(fields.Nested({
				'cwid':fields.Integer,
				'cid':fields.Integer,
				'course_name':fields.String
			})),
		'homeworks':fields.List(fields.Nested({
				'hid':fields.Integer,
				'cid':fields.Integer,
				'htype':fields.Integer,
				'homework_desc':filename.String,
				'homework_begin_time':fields.Integer
			}))
	}
	# 工具函数，将Course对象按照course_fields所规定的字典格式json化为字典
	@marshal_with(course_fields)
	def serialize_course(self,course):
		return course


	# 获取所有课程信息
	def get(self):
		
	# 新建一个课程
	def post(self):
		pass


# /api/course?cid=xxx
class CourseAPI(Resource):
	course_fields={
		'cid':fields.Integer,
		'course_name':fields.String,
		'course_desc':fields.String,
		'course_begin_time':fields.Integer,
		'coursewares':fields.List(fields.Nested({
				'cwid':fields.Integer,
				'cid':fields.Integer,
				'course_name':fields.String
			})),
		'homeworks':fields.List(fields.Nested({
				'hid':fields.Integer,
				'cid':fields.Integer,
				'htype':fields.Integer,
				'homework_desc':filename.String,
				'homework_begin_time':fields.Integer
			}))
	}
	@marshal_with(course_fields)
	def serialize_course(self,course):
		return course

	# 获取某课程的信息
	def get(self):
		# 新建解析器对象，用来获取request中的参数
		parse = reqparse.RequestParser()
		# 检查request中的cid，如果为int，则加入到parse对象中，如果不为int，返回‘错误的cid’
		parse.add_argument('cid',type=int,help='错误的cid',default='1')
		# 将parse对象中的参数读取到args中
		args = parse.parse_args()
		# 获取args中的cid
		cid = args.get('cid') # 现在算是成功把request中的cid存入到cid变量里了

		try:
			# 从数据库中读取指定course对抗
			course = CourseTable.query.get(cid)
		except:
			# 如果获取失败，则返回错误
			return jsonify(code = 11,message='node not exist, query fail')

		# 由于我对try 机制不太了解，所以在这又加了一道判断
		if course == None:
			return jsonify(code = 11,message='node not exist, query fail')
		# 返回得到的course对象，这里的course是model对象，不可序列化，所以不能直接放入返回的json里面
		# 需要把course中的各个字段对应放到一个dict里面，这个功能上面封装成了serialize_course函数
		# 具体详见  https://wangbei.xyz/2020/03/26/flask-model%E5%AF%B9%E8%B1%A1%E8%BD%ACjson/
		return jsonify(code=0,message='OK', data = self.serialize_course(course) ) 


	# 修改某课程
	def put(self):
		pass
	# 删除某课程
	def delete(self):
		pass

# /api/courseware?cid=xxx
class CoursewareAPI(Resource):
	courseware_fields={
		'cwid':fields.Integer,
		'cid':fields.Integer,
		'course_name':fields.String
	}
	@marshal_with(courseware_fields)
	def serialize_courseware(self,courseware):
		return courseware


	# 下载课件
	def get(self):
		pass
	# 上传课件
	def post(self):
		pass

	def delete(self):
		pass

# /api/course/homeworks?cid=xxx
class HomeworksAPI(Resource):
	homework_fields={
		'hid':fields.Integer,
		'cid':fields.Integer,
		'htype':fields.Integer,
		'homework_desc':filename.String,
		'homework_begin_time':fields.Integer,
		'files':fields.List(fields.Nested({
				'hid':fields.Integer,
				'cid':fields.Integer,
				'htype':fields.Integer,
				'homework_desc':filename.String,
				'homework_begin_time':fields,Integer
			}))
	}
	@marshal_with(homework_fields)
	def serialize_homework(self,homework):
		return homework
	# 获取所有作业信息
	def get(self):
		pass
	# 新建课程
	def post(self):
		pass

# /api/course/homework?hid=xxx
class HomeworkAPI(Resource):
	homework_fields={
		'hid':fields.Integer,
		'cid':fields.Integer,
		'htype':fields.Integer,
		'homework_desc':fields.String,
		'homework_begin_time':fields.Integer,
		'files':fields.List(fields.Nested({
				'hid':fields.Integer,
				'cid':fields.Integer,
				'htype':fields.Integer,
				'homework_desc':filename.String,
				'homework_begin_time':fields.Integer
			}))
	}
	@marshal_with(homework_fields)
	def serialize_homework(self,homework):
		return homework

	# 获取某作业
	def get(self):
		pass
	# 修改某作业
	def put(self):
		pass
	# 删除某作业
	def delete(self):
		pass

# /api/course/homework/datasets?hid=xxx
class DatasetAPI(Resource):
	file_fields = {
		'fid':fields.Integer,
		'hid':fields.Integer,
		'ftype':fields.String,
		'filename':fields.String
	}
	@marshal_with(file_fields)
	def serialize_file(self,file):
		return file

	def get(self):
		# TODO ：验证用户身份，不允许学生下载 standard 文件
		pass

	def post(self):
		pass

	def delete(self):
		pass

# /api/user/course/homework?uid=xxx&hid=xxx
# 学生提交的作业
class StudentHomeworkAPI(Resource):
	user_homework_fields = {
		'hid':fields.Integer,
		'uid':fields.Integer,
		'score':fields.Integer,
		'is_finished':fields.Integer,
		'submit_file_name':fields.String,
		'submit_time':fields.Integer
	}
	@marshal_with(user_homework_fields)
	def serialize_file(self,user_homework):
		return user_homework
	# 获取某学生的某作业
	def get(self):
		pass
	# 某学生上传某作业
	def post(self):
		pass

# /api/course/homework/score?uid=xxx&hid=xxx
class ScoreAPI(Resource):
	user_homework_fields = {
		'hid':fields.Integer,
		'uid':fields.Integer,
		'score':fields.Integer,
		'is_finished':fields.Integer,
		'submit_file_name':fields.String,
		'submit_time':fields.Integer
	}
	@marshal_with(user_homework_fields)
	def serialize_file(self,user_homework):
		return user_homework
	# get某学生的某作业的分数
	def get(self):
		pass
	# 打分
	def post(self):
		pass



# util 辅助函数

# 为file生成文件名
import hashlib
def generate_file_name(fid,hid):
	return hashlib.md5(
				(str(fid) + '_' + str(hid)).encode('utf-8')).hexdigest()

# 为submit生成文件名
import hashlib
def generate_file_name(hid,uid):
	return hashlib.md5(
				(str(hid) + '_' + str(uid)).encode('utf-8')).hexdigest()
