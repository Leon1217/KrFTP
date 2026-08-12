# krFTP

## 运行

```powershell
python -m pip install -r requirements.txt
python main.py
```

首次运行会创建 `data/krftp.sqlite3`，并提供默认管理员账号：`admin` / `admin123`。首次成功登录必须修改管理员密码，之后才会按设置自动启动 FTP 与 SFTP 服务。

默认服务端口为 FTP `21` 和 SFTP `22`。服务无法绑定时，应用会在服务管理卡片中显示具体原因；可通过对应服务的“配置”按钮改用高位端口。

已授予压缩权限的 FTP 用户可使用 `SITE ZIP <source> <archive.zip>`，已授予解压权限的用户可使用 `SITE UNZIP <archive.zip> <destination>`。两项操作都限制在该用户的授权根目录内，并写入审计日志。

SFTP 客户端可继续使用标准 SFTP 文件操作。需要压缩或解压时，通过已认证的 SSH 连接执行 `krftp-zip <source> <archive.zip>` 或 `krftp-unzip <archive.zip> <destination>`；服务端使用同一 SFTP 用户权限与根目录校验。

## 关于与版权

版权所有 © krFTP Contributors。

krFTP 是非商业开源项目，仅供学习、个人使用和非商业部署。未经版权持有人明确授权，不得将本软件或其衍生成果用于商业销售、商业托管或商业服务。

## 支持作者

如果觉得 krFTP 好用，欢迎请作者喝一杯咖啡。

| 微信支付 | 支付宝 |
| --- | --- |
| ![微信支付收款码](resource/images/weixin.jpg) | ![支付宝收款码](resource/images/zhifubao.jpg) |
