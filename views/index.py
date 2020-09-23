from . import index_blu
from flask import render_template


@index_blu.route("/")
def index():
    return render_template("index.html")