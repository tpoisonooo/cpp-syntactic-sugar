# 如何在 host 触发 docker 里的 conda  env 执行命令

## 问题描述

我有个 docker image （名为 seedllm），里面有 py310 / py311 两个 env

![image](https://github.com/user-attachments/assets/ae93ab7b-74ce-48e3-8bc2-14cdab84b92b)

正常是: 手动跑命令，先 `docker run -it` 再 `conda activate py310` 最后  `python3 -m run.py`

现在要用 k8s 运行 docker，只能给一句命令

直接 `conda env list` 会报错 `conda not found`

```bash
$ sudo docker run  -it seedllm /bin/bash -c "conda env list "
..
/bin/bash: line 1: conda: command not found
```

### 一、不同 login 方法， env 不同
反复调试会发现 `sudo docker run -it seedllm /bin/bash -c "env | grep PATH"` ，和手动登录的 env 不一样。

![image](https://github.com/user-attachments/assets/bdc069b1-ae16-4a25-a1c2-841efffa3b3b)

而手动登进去 `env | grep PATH` 是有 conda 的

![image](https://github.com/user-attachments/assets/a4729505-2257-4fb1-8596-5aecdac16ba8)

### 二、`source ~/.bashrc` 不生效

在 host 里 `bash -c "source ~/.bashrc"` 不生效
```bash
$ sudo docker run  -it seedllm /bin/bash -c "source ~/.bashrc && conda env list"
..
/bin/bash: line 1: conda: command not found
```

直接 `export PATH=/root/miniconda3/bin:PATH && conda init bash` 也没有效果
```bash
$ sudo docker run  -it seedllm /bin/bash -c "source ~/.bashrc && export PATH=/root/miniconda3/bin:$PATH && conda activate py310" 
..
CondaError: Run 'conda init' before 'conda activate'
```

```bash
$ sudo docker run  -it seedllm /bin/bash -c "source ~/.bashrc && export PATH=/root/miniconda3/bin:$PATH && conda init bash &&  conda activate py310"
..
CondaError: Run 'conda init' before 'conda activate
```

### 目前的苟法

不用 `conda activate` 了，直接运行时指定 env，即 `conda run -n py310 python3 --version` 

```bash
$ sudo docker run  -it seedllm /bin/bash -c "source ~/.bashrc && export PATH=/root/miniconda3/bin:$PATH && conda run -n py310 python3 --version"

Python 3.10.14
```
