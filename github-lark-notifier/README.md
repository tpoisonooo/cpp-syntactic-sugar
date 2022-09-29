# github-lark-notifier
往飞书群发 issue 和 PR 相关提醒

# 一、功能介绍
## issue 相关
1. 创建 issue 时提醒
2. 其他同事 assign issue 给你会提醒；自己 assign 给自己不会
3. 非工作时间自动回复 issue，回复内容在配置文件里；1 个 issue 只回复 1 次

## PR 相关
1. PR 增加 reviewer 时提醒
2. 扫描即将 7 天到期的 PR，提醒 1 次

## 其他
1. 非工作时间（周一至周五且 10~19 点）不发消息，保存到 `history.txt`
2. 工作时间的任意动作（如 issue close/issue reopen），会抽取所有 `history.txt`


# 二、如何使用
## 配置参数
打开 `config.json`，有三条需要配置

1. lark_webhook

这是飞书的回调地址。打开飞书 APP，群聊 “添加自机器人”、创建**自定义消息机器人**，得到 `lark_webhook`，填入

2. issue_comment

非工作时间，issue 回复固定内容，例如 "@ 领导的 github id"

3. github_token

就是你 github 的 token，需要这个来给 api.github.com 发请求。

一个填好的 config.json 大约长这个样子：
```bash
{
"lark_webhook":"https://open.feishu.cn/open-apis/bot/v2/hook/7a5d3d98-xxxx-40f8-b8de-xxxxxxxxxx",
"issue_comment":"xxxxxx",
"github_token":"ghp_UyxxxxxxxxxxxxxxxCjWa"
}
```

## 运行
### 1. 绑定个人 ngrok
打开 ngrok 官网 https://dashboard.ngrok.com/get-started/setup ，github 登录，注册一下。
```bash
$ ngrok config add-authtoken 296eIVNTMih9ZVA7SAqVnfJPamF_xxxxxxxxxxxxxxxxxxxxxxxxx  # 每个人都不一样
```
不注册的话，ngrok 只能用 2 个小时

### 2. 监听 issue 和 PR
开一个 tmux 
```bash
$ python3 -m pip install flask
$ python3 main.py
```
再开个 window
```bash
$ python3 pr_7days.py
```

### 3. 转发 http 端口
再开个 window
```bash
$ ./ngrok http 50000
..
```
然后会得到 ngrok 的地址，例如 https://123-456-789-182-51.ap.ngrok.io

### 4. 设置github webhook
打开 github repo，settings -> webhook，新增一个 webhook

* URL 填 ngork 的地址，再拼接一个 "/github/lark"，例如 https://123-456-789-182-51.ap.ngrok.io/github/lark
* content-type 选择 `application/json`

### 5. 测试
自己创建一个 issue
* main.py 应该至少有 1 行日志
* 工作时间，飞书群里应该有消息

# 三、致谢
* 感谢某网上作者提供了 `LarkBot` class 源码，然而我已找不到出处

# License
[license](../LICENSE)
