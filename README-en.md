# krFTP

[中文说明](README.md)

krFTP is a cross-platform desktop application for quickly configuring and managing FTP and SFTP services. It provides service control, listening address and port configuration, service-user permissions, connection monitoring, and audit logging.

## Internationalization

krFTP natively supports 10 interface languages, selectable on the sign-in screen: Simplified Chinese, English, Traditional Chinese, Japanese, Korean, Spanish, French, German, Portuguese (Brazil), and Russian.

## Features

- **FTP / SFTP service management**: Start and stop FTP and SFTP independently. Configure the listening IP address, port, and application-start behavior.
- **Service-user management**: Create, enable, disable, and delete FTP/SFTP service users. Set account expiry so expired accounts are denied access automatically.
- **Fine-grained permissions**: Configure FTP, SFTP, or both protocols for each service user and assign an authorized root directory.
- **File and directory permissions**: Control listing, reading, writing, appending, file deletion, file renaming, directory creation, directory deletion, directory renaming, compression, and extraction per user.
- **Separate system account**: The management-console account is isolated from FTP/SFTP service users. Update the management account and password from the System Account page.
- **Live connection monitoring**: View online FTP/SFTP sessions, users, source IP addresses, and sign-in times. Disconnect a selected session when required.
- **Audit log**: Records sign-ins, uploads, downloads, deletes, renames, compression, extraction, and service operations. Filter by user, IP, protocol, action, and time, with pagination.
- **IP blocklist**: Block access from a single IP address or a CIDR network.
- **Compression and extraction**: FTP supports `SITE ZIP` / `SITE UNZIP`. SFTP supports `krftp-zip` / `krftp-unzip` through an authenticated SSH connection. Both are restricted by the user's permissions and authorized root directory.
- **System tray**: Services continue running after the main window is closed to the system tray. Signing out does not stop running FTP/SFTP services.

## System Support

- Supports 64-bit Windows systems.
- Windows 7 is not supported.
- 32-bit Windows devices are not supported.

## Run From Source

```powershell
python -m pip install -r requirements.txt
python main.py
```

On first run, krFTP creates `data/krftp.sqlite3` and provides the default administrator account: `admin` / `admin123`. You must change the administrator password after the first successful sign-in. FTP and SFTP services can then start automatically according to the configured settings.

The default service ports are FTP `21` and SFTP `22`. If a service cannot bind to a port, krFTP displays the reason on the Service Management card. Use the corresponding Configure button to select a higher port when necessary.

FTP users with compression permission can use `SITE ZIP <source> <archive.zip>`. Users with extraction permission can use `SITE UNZIP <archive.zip> <destination>`. Both operations are restricted to the authorized root directory and are written to the audit log.

SFTP clients continue to use standard SFTP file operations. For compression or extraction, execute `krftp-zip <source> <archive.zip>` or `krftp-unzip <archive.zip> <destination>` through an authenticated SSH connection. The server applies the same SFTP user permissions and root-directory validation.

## Copyright and License

Copyright (C) 2026 Leon1217 and krFTP Contributors.

krFTP is free software distributed under the GNU General Public License, version 3 or later. See [LICENSE](LICENSE) for the complete license text and [NOTICE.txt](NOTICE.txt) for copyright and contact information.

## Support the Author

If you find krFTP useful, you can support the author with a cup of coffee.

You can also give the project a [GitHub Star](https://github.com/Leon1217/KrFTP) to help more people discover krFTP.

| WeChat Pay | Alipay |
| --- | --- |
| ![WeChat Pay QR code](resource/images/weixin.jpg) | ![Alipay QR code](resource/images/zhifubao.jpg) |
