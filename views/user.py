import hashlib
import time

from utils.image_qiniu import upload_image_to_qiniu
from . import user_blu
from flask import jsonify, session, request, render_template, redirect, url_for
from models.index import User, Follow, Category, News
from models import db
from PIL import Image
import os


# 用户关注功能
@user_blu.route("/user/follow", methods=["POST"])
def follow():
    action = request.json.get("action")
    # 提取到if前面，以便在if或者else中都可以使用
    # 1. 提取当前作者的id
    news_author_id = request.json.get("user_id")

    # 2. 提取当前登录用户的id
    user_id = session.get("user_id")

    if action == "do":
        # 实现关注的流程
        # 1. 提取当前作者的id
        # 2. 提取当前登录用户的id
        # 3. 判断之前是否已经关注过
        # 4. 如果未关注，则进行关注

        # 3. 判断之前是否已经关注过
        news_author = db.session.query(User).filter(User.id == news_author_id).first()
        if user_id in [x.id for x in news_author.followers]:
            return jsonify({
                "errno": 3001,
                "errmsg": "已经关注了，请勿重复关注..."
            })

        # 4. 如果未关注，则进行关注
        try:
            follow = Follow(followed_id=news_author_id, follower_id=user_id)
            db.session.add(follow)
            db.session.commit()

            ret = {
                "errno": 0,
                "errmsg": "关注成功"
            }

            return jsonify(ret)

        except Exception as ret:
            db.session.rollback()
            ret = {
                "errno": 3003,
                "errmsg": "关注失败..."
            }
            return jsonify(ret)
    else:
        # 取消关注
        try:
            follow = db.session.query(Follow).filter(Follow.followed_id == news_author_id,
                                                     Follow.follower_id == user_id).first()
            db.session.delete(follow)
            db.session.commit()

            ret = {
                "errno": 0,
                "errmsg": "取消关注成功"
            }

            return jsonify(ret)

        except Exception as ret:
            db.session.rollback()
            ret = {
                "errno": 3004,
                "errmsg": "取消关注失败..."
            }

            return jsonify(ret)

    return jsonify(ret)


# 防止未登录用户查看信息
@user_blu.route("/user/center")
def user_center():
    user_id = session.get("user_id")
    user = db.session.query(User).filter(User.id == user_id).first()
    nick_name = session.get("nick_name")

    # 如果用户未登录，禁止访问用户中心
    if not nick_name:
        return redirect(url_for('index_blu.index'))

    return render_template("index/user.html", nick_name=nick_name, user=user)


# 显示修改用户信息视图
@user_blu.route("/user/user_base_info")
def user_base_info():
    return render_template("index/user_base_info.html")


# 修改用户信息功能
@user_blu.route("/user/basic", methods=["POST"])
def user_basic():
    # 获取用户的新的信息
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")
    user_info = db.session.query(User).all()

    for i in user_info:
        if i.nick_name == nick_name:
            ret = {
                'errno': 4399,
                'errmsg': '昵称以存在'
            }
            return ret

    # 获取当前用户的信息
    user_id = session.get("user_id")
    # 存储到数据库
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        ret = {
            "errno": 4002,
            "errmsg": "没有此用户"
        }

        return jsonify(ret)

    # 如果查询到此用户就修改数据
    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender

    db.session.commit()

    ret = {
        "errno": 0,
        "errmsg": "修改成功..."
    }

    return jsonify(ret)


# 显示修改用户密码视图
@user_blu.route("/user/user_pass_info")
def user_pass_info():
    return render_template("index/user_pass_info.html")


# 显示修改用户密码功能
@user_blu.route("/user/password", methods=["POST"])
def user_password():
    # 1. 提取旧密码以及新密码
    new_password = request.json.get("new_password")
    old_password = request.json.get("old_password")

    # 2. 提取当前用户的id
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "errno": 4001,
            "errmsg": "请先登录"
        })

    # 2. 判断旧密码与数据中的当前存储的密码是否相同
    user = db.session.query(User).filter(User.id == user_id, User.password_hash == old_password).first()

    # 3. 如果相同，则修改
    if user:
        user.password_hash = new_password
        db.session.commit()
        ret = {
            "errno": 0,
            "errmsg": "修改成功"
        }
        session.clear()

    else:
        ret = {
            "errno": 4004,
            "errmsg": "原密码错误！"
        }

    # 4. 返回json
    return jsonify(ret)


@user_blu.route("/user/user_pic_info.html")
def user_pic_info():
    user_id = session.get("user_id")
    user = db.session.query(User).filter(User.id == user_id).first()
    return render_template("index/user_pic_info.html", user=user)


@user_blu.route("/user/avatar", methods=["POST"])
def user_avatar():
    f = request.files.get("avatar")
    if f:
        # print(f.filename)
        # 为了防止多个用户上传的图片名字相同，需要将用户的图片计算出一个随机的用户名，防止冲突
        file_hash = hashlib.md5()
        file_hash.update((f.filename + time.ctime()).encode("utf-8"))
        file_name = file_hash.hexdigest() + f.filename[f.filename.rfind("."):]
        # 将路径改为static/upload下
        # path_file_name = file_name
        path_file_name = 'static/upload' + file_name
        # 用新的随机的名字当做图片的名字
        f.save(path_file_name)
        # 将这个图片上传到七牛云
        img = upload_image_to_qiniu(path_file_name, file_name)

        # 修改数据库中用户的头像链接（注意，图片时不放在数据库中的，数据库中存放的图片的名字或者路径加图片名）
        user_id = session.get("user_id")
        user = db.session.query(User).filter(User.id == user_id).first()
        user.avatar_url = img

        db.session.commit()
        ret = {
            "errno": 0,
            "errmsg": "成功",
            "avatar_url": img
        }
    else:
        ret = {
            "errno": 4003,
            "errmsg": "上传失败"
        }

    return jsonify(ret)


# # 方法二
# # 修改用户头像功能
# @user_blu.route("/user/avatar", methods=["POST"])
# def user_avatar():
#     # 1.提取新头像
#     new_avatar = request.files.get("avatar")
#     # 获取用户id
#     user_id = session.get('user_id')
#
#     # 判断是否接收到新图片
#     if new_avatar:
#         # 如果存在用Image打开新图片
#         img = Image.open(new_avatar)
#         # 根据session获取的用户id，从数据库匹配并获取用户
#         user = db.session.query(User).filter(User.id == user_id).first()
#         # 添加图片路径文件夹
#         img_path = '/static/index/images/user_avatar/' + str(user.id)
#         # 判断图片路径是否存在
#         user_img = os.path.exists(img_path)
#         # 如果不存在
#         if not user_img:
#             # 创建该路径文件夹
#             os.mkdir(img_path)
#         # 将该图片命名并存放到指定路径
#         img.save(img_path + '/user_imgs.png')
#         # 将该用户的头像路径更改为该图片路径
#         user.avatar_url = img_path + '/user_imgs.png'
#
#         # 提交到数据库
#         db.session.commit()
#         session['avatar_url'] = img_path
#
#         return jsonify({
#             "errno": 0,
#             "avatar_url": "/user/img_path",
#             "errmsg": "修改成功"
#         })
#
#     else:
#         return jsonify({
#             "errno": 4005,
#             "errmsg": "修改失败"
#         })
#
#
# # 获取用户头像
# @user_blu.route("/user/img_path", methods=["GET", "POST"])
# def img_path():
#     # 从session获取用户id
#     user_id = session.get('user_id')
#     # 根据session获取的用户id，从数据库匹配并获取用户
#     user = db.session.query(User).filter(User.id == user_id).first()
#     # 如果该用户已上传头像，打开用户头像，读取
#     if user.avatar_url:
#         with open(user.avatar_url, 'rb') as f:
#             img = f.read()
#     # 如果用户未上传头像信息，返回默认头像
#     else:
#         with open('./static/index/images/user_pic.png', 'rb') as f:
#             img = f.read()
#
#     return img


# 显示用户查看粉丝及功能
@user_blu.route("/user/user_follow")
def user_follow():
    # 获取用户id
    user_id = session.get("user_id")
    # 根据session获取的用户id，从数据库匹配并获取用户
    user = db.session.query(User).filter(User.id == user_id).first()
    # 获取当前需要的页数
    page = int(request.args.get("page", 1))
    # 创建分页器对象
    paginate = user.followers.paginate(page, 2, False)
    # 创建一个关注我的人的列表
    user_followed = []

    for followed in user.followed:
        user_followed.append(followed.id)

    return render_template("index/user_follow.html", paginate=paginate, user_followed=user_followed)


# 显示用户查看我的收藏视图
@user_blu.route("/user/user_collection")
def user_collection():
    # 查询用户
    user_id = session.get("user_id")
    user = db.session.query(User).filter(User.id == user_id).first()
    # 查询用户收藏的文章
    collection_news = user.collection_news
    # 获取页码
    page = int(request.args.get("page", 1))
    # 查询用户收藏的文章
    paginate = user.collection_news.paginate(page, 5, False)

    return render_template("index/user_collection.html", collection_news=collection_news, paginate=paginate)


# 显示新闻发布视图
@user_blu.route("/user/user_news_release.html")
def user_news_release():
    # 查询出分类name，但不包括最新新闻
    category_list = db.session.query(Category).filter(Category.id != 1).all()
    return render_template("index/user_news_release.html", category_list=category_list)


# 新闻发布功能
@user_blu.route("/user/release", methods=["POST"])
def new_release():
    # 获取news表中数据
    title = request.form.get("title")
    category = request.form.get("category")
    digest = request.form.get("digest")
    content = request.form.get("content")
    # 获取上传图片地址
    f = request.files.get("index_image")

    news = News()
    news.title = title
    news.category_id = category
    news.source = "个人发布"
    news.digest = digest
    news.content = content
    news.user_id = session.get("user_id")
    news.status = 1  # 1表示正在审核

    if f:
        # 哈希加密
        file_hash = hashlib.md5()
        file_hash.update((f.filename + time.ctime()).encode("utf-8"))
        # 保存用户上传图片
        file_name = file_hash.hexdigest() + f.filename[f.filename.rfind("."):]

        # 将路径改为static/upload下
        path_file_name = "./static/upload/" + file_name

        # 用新的随机的名字当做图片的名字
        f.save(path_file_name)

        # 将这个图片上传到七牛云
        qiniu_image_url = upload_image_to_qiniu(path_file_name, file_name)
        news.index_image_url = qiniu_image_url

    db.session.add(news)
    db.session.commit()

    ret = {
        "errno": 0,
        "errmsg": "成功"
    }

    return jsonify(ret)


# 显示新闻列表视图
@user_blu.route("/user/user_news_list.html")
def user_news_list():
    # 查询当前用户
    user_id = session.get("user_id")
    user = db.session.query(User).filter(User.id == user_id).first()
    # 获取当前用户的所有新闻
    # news = user.news
    # 提取页码
    page = int(request.args.get("page", 1))
    # 获取当前用户的所有新闻
    news_paginate = user.news.paginate(page, 3, False)

    return render_template("index/user_news_list.html", news_paginate=news_paginate)
