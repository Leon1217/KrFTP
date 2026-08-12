# krFTP

krFTP 是一款用于快速配置和管理 FTP 与 SFTP 服务的跨平台桌面程序，提供服务启停、端口与监听地址配置、服务用户权限、连接监控和审计日志等能力。

## 国际化

原生支持 10 种界面语言，可在登录界面切换：简体中文、English、繁體中文、日本語、한국어、Español、Français、Deutsch、Português (Brasil) 和 Русский。

## 产品特点

- **FTP / SFTP 服务管理**：分别启动和停止 FTP、SFTP 服务；可配置监听 IP、端口与应用启动时自动运行。
- **服务用户管理**：创建、启用、停用和删除 FTP/SFTP 服务用户；管理账号有效期，到期后自动拒绝登录。
- **细粒度权限**：为每个服务用户分别配置 FTP、SFTP 或同时使用两种协议，并设置授权根目录。
- **文件与目录权限**：按用户控制列表、读取、写入、追加、文件删除、文件重命名、目录创建、目录删除、目录重命名、压缩和解压缩。
- **系统账号隔离**：管理控制台登录账号与 FTP/SFTP 服务用户独立，支持在系统账户页面修改管理账号和密码。
- **实时连接监控**：查看当前在线 FTP/SFTP 会话、用户、来源 IP 和登录时间，并可手动断开指定连接。
- **审计日志**：记录登录、上传、下载、删除、重命名、压缩、解压、服务启停等操作；支持按用户、IP、协议、操作和时间筛选，并提供分页查询。
- **IP 黑名单**：支持通过单个 IP 或 CIDR 网段阻止访问请求。
- **压缩与解压缩**：FTP 支持 `SITE ZIP` / `SITE UNZIP` 命令，SFTP 支持通过已认证 SSH 连接执行 `krftp-zip` / `krftp-unzip`，均受授权目录和权限限制。
- **系统托盘**：关闭主窗口后服务可继续在系统托盘运行；退出登录不会停止已运行的 FTP/SFTP 服务。

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
