# -*- coding: utf-8 -*-
# python2 and python3
from __future__ import print_function
from http.server import HTTPServer, BaseHTTPRequestHandler
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
import json
import sys
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import PIL
import tensorflow as tf
import pathlib
import urllib.request

class MyRequest(BaseHTTPRequestHandler):
    def upload(self, url, path):
        print("enter upload:", url)
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': os.stat(path).st_size,
        }
        req = urllib.request.Request(url, open(path, 'rb'), headers=headers, method='PUT')
        urllib.request.urlopen(req)

    def tensor_to_image(self, tensor):
        tensor = tensor*255
        tensor = np.array(tensor, dtype=np.uint8)
        if np.ndim(tensor)>3:
            assert tensor.shape[0] == 1
            tensor = tensor[0]
        return PIL.Image.fromarray(tensor)

    def load_img(self, path_to_img):
        max_dim = 512
        img = tf.io.read_file(path_to_img)
        img = tf.image.decode_image(img, channels=3)
        img = tf.image.convert_image_dtype(img, tf.float32)

        shape = tf.cast(tf.shape(img)[:-1], tf.float32)
        long_dim = max(shape)
        scale = max_dim / long_dim

        new_shape = tf.cast(shape * scale, tf.int32)

        img = tf.image.resize(img, new_shape)
        img = img[tf.newaxis, :]
        return img

    def do_style_transfer(self):
        mpl.rcParams['figure.figsize'] = (12,12)
        mpl.rcParams['axes.grid'] = False

        # 替换为个人账号下的 COS，需具备可读可写权限。
        # content_path 为内容图像的 COS 地址，style_path 为风格图像的 COS 地址。
        content_path = tf.keras.utils.get_file('tiger.jpg', 'https://*****/gpu-image/tiger.jpg')
        style_path = tf.keras.utils.get_file('snow.jpg','https://*****/gpu-image/snow.jpg')

        content_image = self.load_img(content_path)
        style_image = self.load_img(style_path)

        import tensorflow_hub as hub
        hub_model = hub.load('https://hub.tensorflow.google.cn/google/magenta/arbitrary-image-stylization-v1-256/2')
        stylized_image = hub_model(tf.constant(content_image), tf.constant(style_image))[0]
        path = "/tmp/stylized-image.png"
        self.tensor_to_image(stylized_image).save(path)

        # 替换为个人账号下的OSS，需具备可读可写的权限。
        # 此处会将合成的图片存储至指定的 COS 地址。
        self.upload("https://*****/gpu-image/stylized.png", path)

        return "transfer ok"

    def reply(self, msg):
        data = {"result": msg}
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        msg = self.do_style_transfer()
        self.reply(msg)

    def do_POST(self):
        msg = self.do_style_transfer()
        self.reply(msg)

if __name__ == "__main__":
    host = ("0.0.0.0", 9000)
    server = HTTPServer(host, MyRequest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()

