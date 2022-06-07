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

## 推理效果


