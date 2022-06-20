# log-int-softmax

定点版 softmax，出自 [FQ-ViT](https://github.com/megvii-research/FQ-ViT)

## 编译运行
```bash
$ ./buid.sh
$ time ./main

real    0m0.642s
user    0m0.556s
sys     0m0.000s
```

naive 版计算 [192] 10w 次 0.6s 。若 ViT-B 模型 softmax 输入为 [1,12,145,145]，折合 6ms

## 如何使用

直接把 `log_int_softmax_inverse_15` C-style 函数扣走...

```c++
int log_int_softmax_inverse_15(int32_t* ptr, int64_t* buffer, int8_t *out, const int len, float scale)
```

`buffer` 是因为计算中间过程会出现 `int64_t`

`scale` 是 fp32 softmax input scale

`ptr` 是 input ptr

`out` 是 output ptr，存 `int8_t` 类型。实际上是 uint4 后面用于 shift，额外加一个负数后面表示要乘 0

`len` 就是 array length