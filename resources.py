from settings import JWT_SECRET_KEY
import jwt
from flask import jsonify, g
from flask_restful import Resource, reqparse, request
import datetime
from  more_itertools import unique_everseen
from peewee import fn
from flask import current_app as app
from models import User, Post, Like, Unlike, RevokedTokenModel, generate_hash, verify_hash
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_jwt_identity,
                                get_raw_jwt,
                                set_access_cookies,
                                set_refresh_cookies)


parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('email', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)

parser_post = reqparse.RequestParser()
parser_post.add_argument('content', help = 'This field cannot be blank', required = True)

parser_like = reqparse.RequestParser()
parser_like.add_argument("like", help = 'This field cannot be blank', required = True)
parser_like.add_argument('post_id', help = 'This field cannot be blank', required = True)

parser_like_count = reqparse.RequestParser()
parser_like_count.add_argument('date_from', type = str)
parser_like_count.add_argument('date_to', type = str)

class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        app.logger.info(request)
        username = User.validate_username(data['username'])
        email = User.validate_email(data['email'])
        passw = User.validate_password(data['password'])
        try:
            User.create(
            username = username,
            email = email,
            password = generate_hash(passw)
            )
            '''
            turn ON, if use the JWT access cookie:
            # app.config['JWT_TOKEN_LOCATION'] =  ["cookies"]
            '''
            # access_token = create_access_token(identity = data['username'])
            # refresh_token = create_refresh_token(identity = data['username'])
            resp = jsonify({'refresh': True, 'code': 200})
            '''
            turn ON, if use the JWT access cookie:
            # app.config['JWT_TOKEN_LOCATION'] =  ["cookies"]
            '''
            # set_access_cookies(resp, access_token)
            # set_refresh_cookies(resp, refresh_token)
            return resp
        except:
            app.logger.error('Something went wrong (UserRegistration)')
            return {'message': 'Something went wrong (UserRegistration)', 'code': 500}


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        app.logger.info(request)
        g.user = User.get(User.username == data['username'])
        if not g.user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        if verify_hash(data['password'], g.user.password):
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            '''
            turn ON, if use the JWT access cookie:
            # app.config['JWT_TOKEN_LOCATION'] =  ["cookies"]
            '''
            # set_access_cookies(resp, access_token)
            # set_refresh_cookies(resp, refresh_token)
            # try:
            #     Activity.create(conect = 'conect')
            #
            # except:
            #     return {'message': 'Something went wrong (delete_instance_Unlike)',
            #             'code': 500
            #             }
        else:
            app.logger.error('Wrong credentials')
            return {'message': 'Wrong credentials'}
        app.logger.error('Logged in as {}'.format(g.user.username))
        return {
                'message': 'Logged in as {}'.format(g.user.username),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'code': 201
            }


class PostCreate(Resource):
    @jwt_required
    def post(self):
        app.logger.info(request)
        data = parser_post.parse_args()
        username = get_jwt_identity()
        user_id = User.select().where(User.username == username)
        try:
            Post.create(content = data['content'], user_id = user_id)
            return {
                'refresh': True,
                'code': 200
            }
        except:
            app.logger.error('Something went wrong(PostCreate)')
            return {'message': 'Something went wrong(PostCreate)', 'code': 500}


class PostLike(Resource):
    @jwt_required
    def post(self):
        data = parser_like.parse_args()
        app.logger.info(request)
        like = data['like']
        post_id = data['post_id']
        username = get_jwt_identity()
        user_id = User.select().where(User.username == username)
        if Post.select().where((Post.user_id == user_id) & (Post.id == post_id)).count() > 0:
            app.logger.info('This post is yours. You are not entitled to this action')
            return  {'message': 'This post is yours. You are not entitled to this action',
                     'code': 200
                     }
        else:
            if like == 'True':
                if Like.select().where((Like.user_id == user_id) & (Like.post_id == post_id)).count() > 0:
                    resp = jsonify({'refresh': True,
                                    'action': 'like',
                                    'code': 200})
                    return resp

                elif Unlike.select().where((Unlike.user_id == user_id) & (Unlike.post_id == post_id)).count() > 0:
                    try:
                        category = Unlike.get((Unlike.user_id == user_id) & (Unlike.post_id == post_id))
                        category.delete_instance()
                        app.logger.info('delete_instance_Unlike{}'.format(post_id))

                    except:
                        app.logger.error('Something went wrong (False)')
                        return {'message': 'Something went wrong (False)',
                                'code': 500
                                }
                try:
                    Like.create(user_id = user_id, post_id = post_id)
                    resp = jsonify({'refresh': True,
                                    'action': 'like',
                                    'code': 200})
                    return resp

                except:
                    app.logger.error('Something went wrong (delete_instance_Unlike)')
                    return {'message': 'Something went wrong (delete_instance_Unlike)',
                            'code': 500
                            }

            elif like == 'False':
                if Unlike.select().where((Unlike.user_id == user_id) & (Unlike.post_id == post_id)).count() > 0:
                    resp = jsonify({'refresh': True,
                                    'action': 'unlike',
                                    'code': 200})
                    return resp
                elif Like.select().where((Like.user_id == user_id) & (Like.post_id == post_id)).count() > 0:
                    try:
                        category = Like.get((Like.user_id == user_id) & (Like.post_id == post_id))
                        category.delete_instance()
                        app.logger.info('delete_instance_Like{}'.format(post_id))

                    except:
                        app.logger.error('Something went wrong (delete_instance_Like)')
                        return {'message': 'Something went wrong (delete_instance_Like)',
                                'code': 500
                                }
                try:
                    Unlike.create(user_id = user_id, post_id = post_id)#
                    resp = jsonify({'refresh': True,
                                    'action': 'unlike',
                                    'code': 200})
                    return resp

                except:
                    app.logger.error('Something went wrong (False)')
                    return {'message': 'Something went wrong (False)', 'code': 500}


class LikeCount(Resource):
    @jwt_required
    def get(self):
        '''
        "analytics about how many likes was made"
        Example url: /api/analitics/?date_from=2020-02-02&date_to=2020-02-15
        :return: analytics aggregated by day
        '''
        data = parser_like_count.parse_args()
        app.logger.info(request)
        date___from, date___to = data['date_from'],data['date_to']
        date__from = date___from +' 00:00:00.000001'
        date__to = date___to +' 00:00:00.000001'
        date_from = datetime.datetime.strptime((date__from), '%Y-%m-%d %H:%M:%S.%f')
        date_to = datetime.datetime.strptime((date__to), '%Y-%m-%d %H:%M:%S.%f')
        all_like = Like.select().where((Like.timestamp > date_from) & (Like.timestamp < date_to)).count()
        all_unlike = Unlike.select().where((Unlike.timestamp > date_from) & (Unlike.timestamp < date_to)).count()

        days = []
        day = (Like
                .select(Like.timestamp)
                .where((Like.timestamp > date_from) & (Like.timestamp < date_to))
                .tuples())
        for d in day:
            days.append(d[0].strftime("%m/%d/%Y"))
        days_list = list(reversed(list(unique_everseen(days))))

        count_likes = []
        query = (Like
                 .select(fn.count(Like.id).alias('count'))
                 .group_by(fn.date_trunc('day', Like.timestamp))
                 .where((Like.timestamp > date_from) & (Like.timestamp < date_to))
                 .tuples())
        for q in query:
             count_likes.append(q[0])
        agr_like = dict(zip(days_list, count_likes))

        unlike_days = []
        unlike_day = (Unlike
               .select(Unlike.timestamp)
               .where((Unlike.timestamp > date_from) & (Unlike.timestamp < date_to))
               .tuples())
        for d in unlike_day:
            unlike_days.append(d[0].strftime("%m/%d/%Y"))
        unlike_days_list = list(reversed(list(unique_everseen(unlike_days))))

        count_unlikes = []
        query = (Unlike
                 .select(fn.count(Unlike.id).alias('count'))
                 .group_by(fn.date_trunc('day', Unlike.timestamp))
                 .where((Unlike.timestamp > date_from) & (Unlike.timestamp < date_to))
                 .tuples())
        for q in query:
            count_unlikes.append(q[0])

        agr_unlike = dict(zip(unlike_days_list, count_unlikes))
        app.logger.info('count likes by day')
        return {'all like from period': all_like,
                'all unlike from period': all_unlike,
                'count likes by day': agr_like,
                'count unlikes by day': agr_unlike,
                'code': 200
                }


class UserActivity(Resource):
    @jwt_required
    def get(self, user):
        '''
        "analytics about how many likes was made"
        Example url: /api/activity/username
        :param user: username
        :return: when user was login last time
        and when he mades a last request to the service
        '''
        app.logger.info(request)

        def time_query(query):
            post_time = []
            for content in query:
                post_time.append(str(content.timestamp))
            if len(post_time) > 1:
                return post_time[-1]
            elif len(post_time) > 0:
                return post_time[0]
            else:
                return 0

        jwt_token = request.headers.get('authorization', None)
        if jwt_token:
            try:
                decoded = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms='HS256')
                iat = datetime.datetime.fromtimestamp(int(decoded['iat']))

            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return {'message': 'Token is invalid'}

        user_id = User.get(User.username == user)
        post_time_query = Post.select().where(Post.user_id == user_id)
        like_time_query = Like.select().where(Like.user_id == user_id)
        unlike_time_query = Unlike.select().where(Unlike.user_id == user_id)

        return {'login time': str(iat),
                'post time': time_query(post_time_query),
                'like time': time_query(like_time_query),
                'unlike time': time_query(unlike_time_query),
                'code': 200
                }


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def refresh(self):
        ''' Create the new access token'''
        app.logger.info(request)
        current_user = get_jwt_identity()
        print('TokenRefresh current_user',current_user)
        access_token = create_access_token(identity=current_user)
        refresh_token = create_refresh_token(identity = current_user)
        '''
        Set the JWT access cookie in the response.
        turn ON, if use the JWT access cookie:
        # app.config['JWT_TOKEN_LOCATION'] =  ["cookies"]
        '''
        # resp = jsonify({'refresh': True})
        # set_access_cookies(resp, access_token)
        # set_refresh_cookies(resp, refresh_token)
        # return #resp


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        ''' Users logout access'''
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        ''' Users logout refresh'''
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500

