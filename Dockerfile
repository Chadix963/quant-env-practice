# 第一步：使用 Ubuntu 作为底座
FROM ubuntu:22.04

# 第二步：设置环境变量，防止安装过程中弹出交互选择
ENV DEBIAN_FRONTEND=noninteractive

# 第三步：安装基础工具（wget 用于下载，bzip2 是解压必备）
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 第四步：下载并安装 Miniconda
# 我们这里直接下载 Linux 64位最新版
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && /bin/bash /tmp/miniconda.sh -b -p /opt/conda \
    && rm /tmp/miniconda.sh

# 第五步：将 Conda 加入系统路径
ENV PATH=/opt/conda/bin:$PATH

# 第六步：设置工作目录
WORKDIR /app

# 验证安装
RUN conda --version