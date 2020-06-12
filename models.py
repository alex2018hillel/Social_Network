import peewee
import datetime
from passlib.hash import pbkdf2_sha256 as sha256
from peewee import *
import re
from settings import POSTGRES


db = PostgresqlDatabase(POSTGRES['db'],
						user=POSTGRES['user'],
						password=POSTGRES['pw'],
						host=POSTGRES['host'],
						port=POSTGRES['port']
						)

def generate_hash(password):
	return sha256.hash(password)

def verify_hash(password, hash):
	return sha256.verify(password, hash)


class User(Model):
	username = CharField(unique = True)
	email = CharField(unique = True)
	password = CharField(max_length = 100)
	is_admin = BooleanField(default = False)

	class Meta:
		database = db


	def get_posts(self):
		return Post.select().where(Post.user == self)


	@classmethod
	def create_user(cls, username, email, password, admin=False):
		try:
			with db.transaction():
				cls.create(
					username = username,
					email = email,
					password = generate_hash(password),
					is_admin = admin
					)
		except IntegrityError:
			raise ValueError("User already exists")


	@classmethod
	def validate_username(cls, username):
		if re.search("^[a-z0-9_-]{3,15}$", username):
			return (username)


	@classmethod
	def validate_email(cls, email):
		if re.search("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email):
			return (email)


	@classmethod
	def validate_password(cls, password):
		if len(password) < 8:
			return {"message": "Make sure your password is at lest 8 letters"}
		elif re.search('[0-9]',password) is None:
			return {"message": "Make sure your password has a number in it"}
		elif re.search('[A-Z]',password) is None:
			return {"message": "Make sure your password has a capital letter in it"}
		else:
			return (password)



class Post(Model):
	timestamp = DateTimeField(default = datetime.datetime.now)
	user = ForeignKeyField(User, related_name = 'posts')
	content = TextField()

	class Meta:
		database = db
		table_name = 'post'


class Like(Model):
    user = ForeignKeyField(User, column_name='user_id')
    post = ForeignKeyField(Post, column_name='post_id')
    timestamp = DateTimeField(default = datetime.datetime.now)

    class Meta:
        database = db
        table_name = 'likes'


class Unlike(Model):
	user = ForeignKeyField(User, column_name='user_id')
	post = ForeignKeyField(Post, column_name='post_id')
	timestamp = DateTimeField(default = datetime.datetime.now)

	class Meta:
		database = db
		table_name = 'unlikes'


class RevokedTokenModel(Model):
    __tablename__ = 'revoked_tokens'
    jti = CharField(max_length = 100)

    def add(self):
        RevokedTokenModel.create(self)


    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)


def initialize():
	try:
		db.connect()
		print('db.connect()')
		db.create_tables([User, Post, Like, Unlike, Activity], safe = True)

	except peewee.InternalError as px:
		print(str(px))

