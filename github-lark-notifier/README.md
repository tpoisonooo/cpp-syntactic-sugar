# github-lark-notifier
github - 飞书自定义消息提醒

# main.py Feature
1. issue 创建和 review request 时，给飞书发提醒
2. 仅周一至周五且 10~19 点才工作，遵守劳动法
3. 非工作期间的消息，都记入 `history.txt`，随下一条工作消息一起发
4. 非工作期间的 issue，都自动回复一句

# pr_7days.py Feature
1. 寻找所有 PR，如果发现即将 7 天逾期，发个通知。每个 PR 的通知仅发一次

# 用法
1. 打开飞书 APP，“添加机器人”、创建自定义消息机器人，得到 `lark_webhook`
2. `lark_webhook` 填入 `main.py` 的 `$WEB_HOOK` 中
3. 执行 `python3 main.py`，监听 50000 端口
4. 保证 ip+端口在公网能够访问，例如使用 `ngrok http 50000` 转发为 `robot_webhook`
5. 打开 github settings, add webhook。把 `${robot_webook}/github/lark` 填进去、消息类型选 `application/json`

# 致谢
* 感谢某网上作者提供了 `LarkBot` class 源码，然而我已找不到出处

# License
[license](LICENSE)
