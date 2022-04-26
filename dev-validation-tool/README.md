# 目的

辅助开发期间，两个 repo 的数值对分。

# usage
```bash
$ conda install --file requirements.txt
$ python3 main.py --confdir config.toml --datadir /tmp/ub
```

# 功能
监控 datadir 和 configpath，任一发生改变都会
* 解析 configpath，读需要对比的 list 
* 加载 list 中的 numpy 文件，print 是否相同

# 配置项
* rtol 相对误差，默认 1e-3
* atol 绝对误差，默认 1e-5

# 其他
* 文件名可以不写 .npy 后缀
* 忽视 shape 的差异，直接当作 array 对每个值

