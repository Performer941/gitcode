from . import user_blu
from flask import jsonify, session, request, render_template, redirect, url_for
from models.index import User, Follow
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
    nick_name = db.session.query(User).filter(User.id == user_id).first().nick_name

    # 如果用户未登录，禁止访问用户中心
    if not nick_name:
        return redirect(url_for('index_blu.index'))

    return render_template("user.html", nick_name=nick_name)


# 显示修改用户信息视图
@user_blu.route("/user/user_base_info")
def user_base_info():
    return render_template("user_base_info.html")


# 修改用户信息功能
@user_blu.route("/user/basic", methods=["POST"])
def user_basic():
    # 获取用户的新的信息
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

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
    return render_template("user_pass_info.html")


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

    else:
        ret = {
            "errno": 4004,
            "errmsg": "原密码错误！"
        }

    # 4. 返回json
    return jsonify(ret)


# 显示修改用户头像视图
@user_blu.route("/user/user_pic_info")
def user_pic_info():
    return render_template("user_pic_info.html")


# 修改用户头像功能
@user_blu.route("/user/avatar", methods=["POST"])
def user_avatar():
    # 1.提取新头像
    new_avatar = request.files.get("avatar")
    # 获取用户id
    user_id = session.get('user_id')

    # 判断是否接收到新图片
    if new_avatar:
        # 如果存在用Image打开新图片
        img = Image.open(new_avatar)
        # 根据session获取的用户id，从数据库匹配并获取用户
        user = db.session.query(User).filter(User.id == user_id).first()
        # 添加图片路径文件夹
        img_path = './static/index/images/user_avatar/' + str(user.id)
        # 判断图片路径是否存在
        user_img = os.path.exists(img_path)
        # 如果不存在
        if not user_img:
            # 创建该路径文件夹
            os.mkdir(img_path)
        # 将该图片命名并存放到指定路径
        img.save(img_path + '/user_imgs.png')
        # 将该用户的头像路径更改为该图片路径
        user.avatar_url = img_path + '/user_imgs.png'
        # 提交到数据库
        db.session.commit()

        return jsonify({
                 "errno": 0,
                 "errmsg": "修改成功"
             })

    else:
        return jsonify({
                "errno": 4005,
                "errmsg": "修改失败"
        })


# 获取用户头像
@user_blu.route("/user/img_path", methods=["GET", "POST"])
def img_path():
    # 从session获取用户id
    user_id = session.get('user_id')
    # # 根据session获取的用户id，从数据库匹配并获取用户
    user = db.session.query(User).filter(User.id == user_id).first()
    # 如果该用户已上传头像，打开用户头像，读取
    if user.avatar_url:
        with open(user.avatar_url, 'rb') as f:
            img = f.read()
    # 如果用户未上传头像信息，返回默认头像
    else:
        with open('./static/index/images/user_pic.png', 'rb') as f:
            img = f.read()

    return img


# 显示用户查看粉丝视图
@user_blu.route("/user/user_follow")
def user_follow():
    return render_template("user_follow.html")


# 显示用户查看我的收藏视图
@user_blu.route("/user/user_collection")
def user_collection():
    return render_template("user_collection.html")


# 显示新闻发布视图
@user_blu.route("/user/user_news_release")
def user_news_release():
    return render_template("user_news_release.html")


# 显示新闻列表视图
@user_blu.route("/user/user_news_list")
def user_news_list():
    return render_template("user_news_list.html")
