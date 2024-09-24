# 如何在 host 触发 docker 里的 conda  env 执行命令

## 问题描述

我有个 docker image （名为 seedllm），里面有 py310 / py311 两个 env

![image](https://github.com/user-attachments/assets/ae93ab7b-74ce-48e3-8bc2-14cdab84b92b)

正常是手动跑命令，先 `docker run -it` 再 `conda activate py310` 最后  `python3 -m run.py`

现在要用 k8s 运行 docker，只能给一句命令

直接  `conda env list` 会报错 `conda not found`
```bash
khj@rg-X299X-AORUS-MASTER:~$ sudo docker run  -it seedllm /bin/bash -c "conda env list "
..
```

反复调试会发现 `$SHELL` `$env` 和手动 login 的都不一样。
         
