from . import admin_blu
from flask import render_template


@admin_blu.route('/index.html')
def admin_index():
    return render_template("admin/index.html")


@admin_blu.route('/user_count.html')
def user_count():
    return render_template("admin//user_count.html")


@admin_blu.route('/user_list.html')
def user_list():
    return render_template("admin/user_list.html")


@admin_blu.route('/news_review.html')
def news_review():
    return render_template("admin/news_review.html")


@admin_blu.route('/news_edit.html')
def news_edit():
    return render_template("admin/news_edit.html")


@admin_blu.route('/news_type.html')
def news_type():
    return render_template("admin/news_type.html")
