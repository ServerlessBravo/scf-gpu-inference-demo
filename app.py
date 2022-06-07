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
from urllib.parse import urlparse
import tempfile

class MyRequest(BaseHTTPRequestHandler):

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

    def file_base_name(self, url):
        return os.path.basename(urlparse(url).path)

    def do_style_transfer(self, data = dict()):
        hub_model_path = data.get('hub_model_path') or 'https://web-helloworld-1307427535.cos.ap-guangzhou.myqcloud.com/gpu_demo/magenta%3Aarbitrary-image-stylization-v1-256_v2.tar'
        content_image_path = data.get('content_image_path') or 'https://web-helloworld-1307427535.cos.ap-guangzhou.myqcloud.com/gpu_demo/tiger.png'
        style_image_path = data.get('style_image_path') or 'https://web-helloworld-1307427535.cos.ap-guangzhou.myqcloud.com/gpu_demo/snow.png'
	

        mpl.rcParams['figure.figsize'] = (12,12)
        mpl.rcParams['axes.grid'] = False

        content_image_file = tf.keras.utils.get_file(self.file_base_name(content_image_path), content_image_path)
        style_image_file = tf.keras.utils.get_file(self.file_base_name(style_image_path), style_image_path)

        content_image = self.load_img(content_image_file)
        style_image = self.load_img(style_image_file)

        import tensorflow_hub as hub
        hub_model_path = hub.load(hub_model_path)
        stylized_image = hub_model_path(tf.constant(content_image), tf.constant(style_image))[0]

        ntf = tempfile.NamedTemporaryFile(delete=False, suffix = '.png')
        self.tensor_to_image(stylized_image).save(ntf.name)
        return ntf.name

    def reply(self, path):
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.send_header('Content-Length', str(os.stat(path).st_size))
        self.end_headers()

        with open(path, 'rb') as file_handle:
            self.wfile.write(file_handle.read())

        os.remove(path)

    def do_GET(self):
        file_path = self.do_style_transfer()
        self.reply(file_path)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        file_path = self.do_style_transfer(data)
        self.reply(file_path)

if __name__ == "__main__":
    host = ("0.0.0.0", 9000)
    server = HTTPServer(host, MyRequest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()

