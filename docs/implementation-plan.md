# krFTP 实施方案

## 1. 目标与范围

krFTP 是一个面向桌面部署的 FTP/SFTP 服务管理工具。首个正式版本必须提供登录验证、10 种语言、可配置监听、按用户授权、账号有效期、审计、IP 黑名单、实时会话和软件打开时自动启动服务。

以 SFTP 作为默认安全传输方式；FTP 在用户启用后提供，并应优先支持 FTPS。压缩和解压属于正式权限能力，但只能在用户已授权根目录内以受限任务方式执行。

## 2. 技术决策

| 领域 | 选择 | 实施要点 |
| --- | --- | --- |
| 桌面界面 | PySide6 | UI 线程只处理显示和用户操作；服务状态通过 Signal/Slot 回传。 |
| FTP | pyftpdlib | 运行在专用工作线程，使用自定义 authorizer 和 handler。 |
| SFTP | asyncssh | 运行在专用 asyncio 事件循环线程；每个请求通过统一策略层授权。 |
| 数据存储 | SQLite + Peewee | 启用 WAL、外键和合理的 busy timeout；每个线程使用独立数据库连接。 |
| 密码 | Argon2id（首选）或 bcrypt | 只保存带盐哈希；绝不使用 SHA-256 直接保存口令。 |
| 配置 | JSON/INI 文件 + 数据库设置表 | 支持 `0.0.0.0`、自定义端口和 `auto_start_services`；默认端口为 FTP `21`、SFTP `22`。 |

## 3. 分层与边界

```text
PySide6 UI
  -> Application services（用例、状态、事件）
     -> Domain（用户、权限、路径与会话策略）
        -> Adapters（FTP、SFTP、SQLite、日志）
```

协议适配器不能直接操作窗口控件。FTP 与 SFTP 必须共享同一套 `AuthService`、`PermissionService`、`PathPolicy` 和 `AuditService`，避免两个协议产生不同的授权结果。

服务状态采用显式状态机：`STOPPED -> STARTING -> RUNNING -> STOPPING -> STOPPED/FAILED`。启动失败必须保留失败原因，停止操作必须有超时和资源清理。

网络设置允许输入单个本机 IP 或 `0.0.0.0`；后者绑定所有可用网络链路。FTP 默认监听 `21`，SFTP 默认监听 `22`，均可修改。`auto_start_services` 默认开启，应用完成数据库和配置加载后自动启动已启用的 FTP 与 SFTP 服务；任一服务失败不阻止 UI 打开，并在概览页显示错误原因。

## 4. 安全基线

- 首次运行创建默认管理员 `admin`，初始密码为 `admin123`，以 Argon2id/bcrypt 哈希保存；该账户首次成功登录后必须修改密码，且未修改前不能启用服务或创建其他用户。
- SFTP 服务器首次启动生成或导入 host key；私钥文件权限应只允许当前系统用户读取。
- FTP 明文传输默认关闭。启用 FTP 时，在设置页明确提示风险；生产场景应使用 FTPS 并配置证书。
- 所有远程路径先规范化，再验证其仍位于用户授权根目录内，拒绝 `..`、符号链接逃逸和跨根目录重命名。
- 登录失败实行按 IP 和用户名的限速/退避；黑名单同时支持 IP 与 CIDR，使用 `ipaddress` 标准库匹配。
- 审计日志记录认证、文件操作、授权拒绝、服务启停与配置修改；敏感字段不得写入口令、私钥或 token。
- 压缩与解压不调用 shell。任务使用 `zipfile`，在服务端校验 `compress` 或 `decompress`、根目录边界、文件数和解压后总大小；所有任务写入审计日志。FTP 提供受限 `SITE ZIP <source> <archive.zip>` 与 `SITE UNZIP <archive.zip> <destination>` 扩展；SFTP 通过同一 SSH 连接提供受限 `krftp-zip` 和 `krftp-unzip` exec 请求；不支持扩展的客户端仍可使用常规文件操作。

## 5. ORM 与数据库实现

ORM 框架固定采用 **Peewee**，数据库采用 SQLite。Peewee 负责模型定义、参数化查询、事务和每线程连接管理；不在 FTP/SFTP 回调中直接拼接 SQL。

```text
peewee>=3.17,<4        # ORM 框架
peewee-migrate>=1.12   # Schema 版本迁移工具
```

数据库初始化流程：启动时创建数据目录，打开 SQLite 连接并执行 `PRAGMA foreign_keys = ON`、`PRAGMA journal_mode = WAL`、`PRAGMA busy_timeout = 5000`；随后执行尚未应用的迁移。数据库 schema 的任何变更必须新增迁移文件，不能依赖 `create_tables()` 静默修改生产数据。

| 模块 | 职责 |
| --- | --- |
| `database/models.py` | 定义 `BaseModel`、用户、授权根目录、IP 规则、审计和设置等 Peewee 模型。 |
| `database/db_manager.py` | 创建和关闭 `SqliteDatabase`、管理每线程连接、执行迁移，并封装用户、权限与审计 CRUD。 |
| `database/migrations/` | 按版本保存可重放的数据库迁移脚本。 |

SQLite 适用于单机、低到中等写入量的部署。审计量持续较高或要让多台机器共用用户库时，保留 Repository 接口并迁移到 PostgreSQL，UI 与协议服务不需要改动。

## 6. 数据模型

### 核心表

| 表 | 关键字段 | 约束/索引 |
| --- | --- | --- |
| `users` | `id`, `username`, `password_hash`, `is_active`, `expires_at`, `created_at`, `updated_at` | `username` 唯一；`expires_at` 可为空。 |
| `user_roots` | `id`, `user_id`, `protocol`, `root_path`, `permissions` | `(user_id, protocol, root_path)` 唯一；权限存为受校验的位集合或 JSON。 |
| `ip_rules` | `id`, `network`, `action`, `reason`, `created_at` | `action` 仅允许 `deny`；网络以规范 CIDR 保存。 |
| `audit_logs` | `id`, `occurred_at`, `username`, `protocol`, `client_ip`, `action`, `path`, `result`, `detail` | 为 `occurred_at`、`username`、`client_ip` 建索引；支持按日期清理。 |
| `settings` | `key`, `value`, `updated_at` | 保存 `bind_ip`、`ftp_port`、`sftp_port`、`auto_start_services`、`language` 等非敏感设置；密钥路径等敏感内容由系统凭据存储或受限文件保存。 |

权限集合为 `list`、`read`、`write`、`append`、`delete_file`、`rename_file`、`create_dir`、`delete_dir`、`rename_dir`、`compress` 和 `decompress`。每个 `user_roots` 记录同时保存适用协议（`FTP`、`SFTP`、`BOTH`）与该根目录权限；服务端对每次请求都根据目标路径重新求值。

## 7. 会话、审计与并发

会话管理器在内存中维护不可变快照，包含会话 ID、协议、用户名、客户端 IP、登录时间、最后活动时间和当前传输统计。UI 每秒读取快照或接收变更信号，不直接访问服务线程内部对象。

审计写入使用有界队列和单独写入器，避免网络回调被 SQLite I/O 阻塞。记录登录、上传、下载、追加、删除、重命名、压缩、解压、授权拒绝、服务启停和配置修改；队列满时优先保留认证失败、权限拒绝、删除和配置变更等安全事件，并向 UI 报告降级状态。用户禁用、过期或被拉黑时，服务通过会话 ID 主动断开已登录连接。

## 8. UI 与国际化

主窗口使用侧栏加 `QStackedWidget`，页面包含：概览、服务、用户、访问规则、会话、审计日志和设置。长表格采用 `QTableView` 加模型，不使用 `QTableWidget` 承载持续刷新的会话和日志数据。

所有可见文本使用 `self.tr()`。语言切换时保留一个长期存活的 `QTranslator` 实例，先移除旧翻译器后安装新翻译器，并触发各页面重新翻译。

### 支持语言清单

| 优先级 | 语言 | Qt locale | 翻译文件 |
| --- | --- | --- | --- |
| P0 | 简体中文 | `zh_CN` | `krftp_zh_CN.ts/.qm` |
| P0 | English (United States) | `en_US` | `krftp_en_US.ts/.qm` |
| P1 | 繁体中文 | `zh_TW` | `krftp_zh_TW.ts/.qm` |
| P1 | 日本语 | `ja_JP` | `krftp_ja_JP.ts/.qm` |
| P1 | 한국어 | `ko_KR` | `krftp_ko_KR.ts/.qm` |
| P1 | Espanol | `es_ES` | `krftp_es_ES.ts/.qm` |
| P1 | Francais | `fr_FR` | `krftp_fr_FR.ts/.qm` |
| P1 | Deutsch | `de_DE` | `krftp_de_DE.ts/.qm` |
| P1 | Portugues (Brasil) | `pt_BR` | `krftp_pt_BR.ts/.qm` |
| P1 | Русский | `ru_RU` | `krftp_ru_RU.ts/.qm` |

上述 10 种语言均为正式版本交付范围。语言设置值使用对应 locale，未找到翻译时回退至 `en_US`，再回退至内置 `zh_CN`。自定义语言以导入已编译的 Qt `.qm` 文件实现：文件复制到 `i18n/custom/`，在设置页校验后立即显示为可选语言，不覆盖内置翻译。将来添加阿拉伯语时，需额外验证 Qt 的 RTL（从右到左）布局和数字、日期显示。

## 9. 图标资源

指定图标为 `resource/images/logo.ico`，已在 `resource/krftp.qrc` 注册为 `:/images/logo.ico`。构建资源后，应用入口应在创建窗口前设置图标：

```python
from PySide6.QtGui import QIcon

app.setWindowIcon(QIcon(":/images/logo.ico"))
window.setWindowIcon(QIcon(":/images/logo.ico"))
```

开发环境可执行 `pyside6-rcc resource/krftp.qrc -o resource/krftp_rc.py`，并在入口中导入 `resource.krftp_rc`。打包时还要将同一 `logo.ico` 指定为 Windows 可执行文件图标，保证任务栏、窗口和 exe 图标一致。

## 10. 推荐目录

```text
krFTP/
  main.py                    # 应用入口：初始化 App、数据库、登录窗口
  config.py                  # 全局配置与路径常量
  database/                  # Peewee ORM 数据层
    models.py                # 模型定义
    db_manager.py            # 数据库初始化、迁移与 CRUD
    migrations/              # Schema 迁移脚本
  servers/                   # 协议服务层
    ftp_server.py            # pyftpdlib 适配器和鉴权
    sftp_server.py           # asyncssh 适配器和鉴权
    session_manager.py       # 在线会话、黑名单和过期扫描
  ui/                        # PySide6 视图层
    login_dialog.py          # 登录窗口
    main_window.py           # 主窗口
    views/                   # Dashboard、Users、Logs、Settings 等页面
    resources/               # QSS 等 UI 资源
  resource/
    images/logo.ico          # 程序图标
    krftp.qrc                # Qt 图标资源清单
  i18n/                      # 10 种内置语言的 .ts/.qm 文件
    custom/                  # 用户导入的自定义 .qm 文件
  utils/
    crypto.py                # 口令哈希与验证
    path_policy.py           # 根目录和路径逃逸校验
    zip_utils.py             # 受权限和资源限制的压缩/解压任务
  docs/                      # 设计与部署文档
  tests/                     # 单元与集成测试
```

## 11. 交付顺序与验收

1. 搭建项目骨架、资源编译、配置加载、数据库迁移和管理员初始化流程。
2. 完成 SFTP 的用户认证、单根目录读写授权、路径逃逸防护、审计和会话管理。
3. 完成服务控制页、用户与权限页、黑名单、日志筛选和连接剔除。
4. 增加 FTP/FTPS 适配器，并以同一组授权与审计测试验证协议一致性。
5. 补齐 i18n、备份/迁移、打包与跨平台冒烟测试。

验收至少覆盖：错误口令限速、过期用户被拒绝并断开、CIDR 黑名单拦截、越权与符号链接逃逸被拒绝、上传/下载/重命名/删除均被审计、服务可以重复启停且 UI 不冻结、`logo.ico` 出现在窗口和打包后的 Windows 程序中。

## 12. 需求验收矩阵

| 需求 | 必须达到的验收结果 |
| --- | --- |
| 登录验证 | 主窗口在登录成功前不可进入；首次数据库初始化可用 `admin` / `admin123` 登录，并强制改密。 |
| 国际化与网络监听 | 10 个内置 locale 都可切换；可导入自定义 `.qm`；`0.0.0.0`、FTP `21`、SFTP `22` 及自定义端口均可保存和生效。 |
| 细粒度权限 | 能按用户、协议和根目录分别授予全部文件、目录、压缩及解压权限；未授权操作被协议层拒绝。 |
| 账号有效期 | 过期账户不能建立新会话；到期后的在线会话在扫描周期内被断开。 |
| 操作审计 | UI 可实时查看登录、上传、下载、删除、重命名、压缩和解压记录，并按用户、IP、时间和动作筛选。 |
| IP 黑名单 | 单 IP 与 CIDR 网段均能拦截 FTP 和 SFTP 新连接；拉黑在线 IP 后会话被断开。 |
| 实时连接监控 | 主界面展示在线数量和协议、用户、IP、登录时间；管理员可按会话 ID 手动剔除连接。 |
| 自动启动服务 | 默认设置下打开软件后 FTP 与 SFTP 自动启动；关闭设置后不启动，启动失败显示具体原因。 |
