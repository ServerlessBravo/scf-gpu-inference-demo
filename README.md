# SCF GPU 推理 Demo


## 镜像构建

基于腾讯云的TCR服务：

```bash
# 登录镜像仓库，$YOUR_REGISTRY_URL请替换为您所使用的镜像仓库，$USERNAME、$PASSWORD分别替换为您的登录凭证
docker login $YOUR_REGISTRY_URL --username $USERNAME --password $PASSWORD

# 镜像构建，$YOUR_IMAGE_NAME 请替换为您所使用的镜像地址
docker build -t scf_gpu_demo:latest .

# 添加Tag
docker tag scf_gpu_demo:latest xxxx.tencentcloudcr.com/yyyy/scf_gpu_demo:latest

# 镜像推送
docker push xxx.tencentcloudcr.com/yyyy/scf_gpu_demo:latest
```

## 部署

### 函数配置

注意：需要创建 Web 函数：


```bash
函数类型	Web函数
资源类型	GPU
资源规格	NVIDIA T4 计算型 ｜ 1*T4 16GiB显存 20核 80GiB
初始化超时时间	300秒
执行超时时间	100秒

```

### 触发器配置

升级 Web 函数默认的触发器到专享版本之后，可以修改后端超时时间：


```bash
公网  https://service-xxx.sh.apigw.tencentcs.com/release/
协议支持	HTTP&HTTPS
请求方法	ANY
启用Base64编码	未启用
支持CORS	否
后端超时	330s
```

### 测试

#### 使用默认的内容图片和风格图片：

```bash
curl -X GET https://service-5fa1xyn7-1253970226.sh.apigw.tencentcs.com/release/ --output /tmp/transformed.png
open /tmp/transformed.png
```

迁移效果：

![风格迁移](https://user-images.githubusercontent.com/251222/172288034-325598e0-3c15-4feb-8668-9e708e6b6e4b.png)

#### 使用自定义的内容图片和风格图片

```bash
curl --location --request POST 'https://service-xxx.sh.apigw.tencentcs.com/release/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "content_image_path": "https://web-helloworld-1307427535.cos.ap-guangzhou.myqcloud.com/gpu_demo/woman.jpg",
    "style_image_path": "https://web-helloworld-1307427535.cos.ap-guangzhou.myqcloud.com/gpu_demo/snow.png"
}' \
--output /tmp/transformed.png

open /tmp/transformeded.png
```

迁移效果：

![风格迁移](https://user-images.githubusercontent.com/251222/172374628-3107625d-c701-4f74-b621-42b3fb0b13dd.png)


## 备注

- 由于网络原因，SCF无法从 `Tensforflow Hub` 自动下载模型，建议离线下载之后存放到COS之后，通过COS地址访问
- 可以通过 `hub_model_path` 配置事先下载的模型地址，例如 `https://xxxx.cos.ap-guangzhou.myqcloud.com/gpu_demo/magenta%3Aarbitrary-image-stylization-v1-256_v2.tar`
- 图片链接需要可以公网可以访问，如果需要额外的权限认证会导致文件下载失败
- 使用的模型：[magenta/arbitrary-image-stylization-v1-256-v2](https://hub.tensorflow.google.cn/google/magenta/arbitrary-image-stylization-v1-256/2)
