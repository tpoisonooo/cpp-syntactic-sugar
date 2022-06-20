# Description

`.ini` file parser and serializer, developed for ncnn int8 quant config.

You can also treat it as partial `.toml` format +_+

before:

```shell
conv_param_0 1.1 2.2 3.3
fire_param_0 1.2 3.4
conv 100.2
fire 100.2
```

after:

```shell
[conv]
type = "Conv"
weight = [ 1.1, 2.2, 3.3 ]
input_scale = 100.2

[fire]
type = "Conv"
weight = [ 1.2, 3.4 ]
input_scale = 100.2
```
