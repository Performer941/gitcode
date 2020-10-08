from qiniu import Auth, put_file, etag
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'jr33-txXKmPe-vacoo47Dq-nrqscdC7TboRP4mYy'
secret_key = 'ZaC0qow_M38Jyst40Awn093TpX2EGDeQAFO86fvI'

# 构建鉴权对象
q = Auth(access_key, secret_key)

# 要上传的空间
bucket_name = 'xinjingzixun-2020'


def upload_image_to_qiniu(localfile, key):
    """
    上传图片到七牛云
    :param localfile: 要上传的文件路径
    :param key: 保存到七牛云之后的文件名
    :return: True表示成功
    """
    # 上传后保存的文件名
    # key = 'my-python-logo.png'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    # 要上传文件的本地路径
    # localfile = './bbb.png'
    ret, info = put_file(token, key, localfile)
    print(info)

    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)

    return "http://qhr7vbo1a.hn-bkt.clouddn.com/" + key


if __name__ == '__main__':
    upload_image_to_qiniu('./bbb.png', 'my-python-logo.png')
