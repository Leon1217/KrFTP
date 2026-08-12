from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QDateTime, QTimer, Qt
from PySide6.QtGui import QAction, QFontMetrics, QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateTimeEdit, QDialog, QDialogButtonBox, QFileDialog, QFrame,
    QFormLayout, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QSpinBox, QStackedWidget, QTableWidget,
    QTableWidgetItem, QListWidget, QVBoxLayout, QWidget, QHeaderView,
    QAbstractItemView, QSystemTrayIcon, QMenu, QSizePolicy,
)

from database.db_manager import ALL_PERMISSIONS
from ui.theme import APP_STYLE

ACTION_LABELS = {
    "LOGIN": "登录", "UPLOAD": "上传", "DOWNLOAD": "下载", "DELETE": "删除",
    "RENAME": "重命名", "COMPRESS": "压缩", "DECOMPRESS": "解压",
    "ARCHIVE": "归档操作", "KICK_SESSION": "剔除连接", "STOP_SERVICES": "停止全部服务",
    "DELETE_SERVICE_USER": "删除服务用户",
    "START_FTP": "启动 FTP 服务", "STOP_FTP": "停止 FTP 服务",
    "START_SFTP": "启动 SFTP 服务", "STOP_SFTP": "停止 SFTP 服务",
}

ACTION_LABELS_EN = {
    "LOGIN": "Login", "UPLOAD": "Upload", "DOWNLOAD": "Download", "DELETE": "Delete",
    "RENAME": "Rename", "COMPRESS": "Compress", "DECOMPRESS": "Extract",
    "ARCHIVE": "Archive operation", "KICK_SESSION": "Disconnect session", "STOP_SERVICES": "Stop all services",
    "DELETE_SERVICE_USER": "Delete service user", "START_FTP": "Start FTP service", "STOP_FTP": "Stop FTP service",
    "START_SFTP": "Start SFTP service", "STOP_SFTP": "Stop SFTP service",
}

DIALOG_TEXT = {
    "zh_CN": {"save":"保存", "cancel":"取消", "add_user":"新增服务用户", "username":"服务用户名", "initial_password":"初始密码", "expiry":"到期时间", "never":"永不过期", "permission":"配置访问权限", "protocol":"协议范围", "root":"授权根目录", "browse":"浏览", "ftp_sftp":"FTP 和 SFTP", "ftp_only":"仅 FTP", "sftp_only":"仅 SFTP", "service_config":"配置 {name} 服务", "listen_ip":"监听 IP", "listen_port":"监听端口", "system_user":"系统账号", "new_password":"新密码", "confirm_password":"确认新密码", "leave_blank":"留空则不修改密码", "about_version":"版本 0.1.0", "copyright":"版权所有 © krFTP Contributors。\n\nkrFTP 是一个非商业开源项目，仅供学习、个人使用和非商业部署。未经版权持有人明确授权，不得将本软件或其衍生成果用于商业销售、商业托管或商业服务。", "author_contact":"作者联系方式\n微信：Leon121706\nQQ：1217067605"},
    "en_US": {"save":"Save", "cancel":"Cancel", "add_user":"Add Service User", "username":"Service username", "initial_password":"Initial password", "expiry":"Expiry date", "never":"Never expires", "permission":"Configure access permissions", "protocol":"Protocol scope", "root":"Authorized root", "browse":"Browse", "ftp_sftp":"FTP and SFTP", "ftp_only":"FTP only", "sftp_only":"SFTP only", "service_config":"Configure {name} Service", "listen_ip":"Listening IP", "listen_port":"Listening port", "system_user":"System username", "new_password":"New password", "confirm_password":"Confirm new password", "leave_blank":"Leave empty to keep the current password", "about_version":"Version 0.1.0", "copyright":"Copyright © krFTP Contributors.\n\nkrFTP is a non-commercial open-source project for learning, personal use, and non-commercial deployments. Without explicit authorization from the copyright holder, it must not be used for commercial sale, hosting, or services.", "author_contact":"Author contact\nWeChat: Leon121706\nQQ: 1217067605"},
}


def dialog_text(locale):
    return DIALOG_TEXT.get(locale, DIALOG_TEXT["zh_CN"])

MAIN_TEXT = {
    "zh_CN": ["krFTP Server Manager", "FTP / SFTP 服务控制台", "当前管理员", "服务管理", "服务用户与权限", "实时连接", "审计日志", "IP 黑名单", "系统账户", "关于 krFTP", "分别管理 FTP 与 SFTP 的监听状态、IP 地址和端口。", "服务用户", "管理账户有效期、访问根目录和协议权限。", "连接会话", "查看当前协议会话，并即时断开异常连接。", "审计日志", "追踪认证、传输、归档和服务管理操作。", "IP 黑名单", "拒绝指定 IP 地址或 CIDR 网段的访问请求。", "系统账户", "此账户仅用于登录 krFTP 管理程序，不具备 FTP/SFTP 文件服务权限。", "关于 krFTP", "版本、版权与开源使用声明。", "启动服务", "停止服务", "配置", "启动程序时自动启动", "运行中", "已停止", "监听地址", "当前在线连接", "新增用户", "启用/禁用", "配置权限", "删除用户", "剔除选中连接", "刷新日志", "添加黑名单", "保存系统账户", "退出登录"],
    "en_US": ["krFTP Server Manager", "FTP / SFTP Service Console", "Signed in as", "Service Management", "Service Users & Permissions", "Live Connections", "Audit Log", "IP Blocklist", "System Account", "About krFTP", "Manage FTP and SFTP status, listening address, and port.", "Service Users", "Manage account expiry, service roots, and protocol permissions.", "Connection Sessions", "Review active protocol sessions and disconnect them when needed.", "Audit Log", "Track authentication, transfers, archives, and service actions.", "IP Blocklist", "Block an IP address or CIDR network from connecting.", "System Account", "This account signs in to krFTP only and has no FTP/SFTP file-service access.", "About krFTP", "Version, copyright, and open-source notice.", "Start Service", "Stop Service", "Configure", "Start with application", "Running", "Stopped", "Listening", "Active connections", "Add User", "Enable / Disable", "Permissions", "Delete User", "Disconnect Selected", "Refresh Log", "Add Block Rule", "Save System Account", "Sign Out"],
}

# Keep the positional layout used by the existing UI in one place.  Login has
# always supported these locales; the main window must use the same locale
# instead of silently falling back to English.
MAIN_TEXT.update({
    "zh_TW": ["krFTP 伺服器管理員", "FTP / SFTP 服務控制台", "目前管理員", "服務管理", "服務使用者與權限", "即時連線", "稽核日誌", "IP 黑名單", "系統帳戶", "關於 krFTP", "分別管理 FTP 與 SFTP 的監聽狀態、IP 位址與連接埠。", "服務使用者", "管理帳戶到期日、存取根目錄與通訊協定權限。", "連線工作階段", "檢視目前通訊協定工作階段，並立即中斷異常連線。", "稽核日誌", "追蹤驗證、傳輸、封存及服務管理操作。", "IP 黑名單", "拒絕指定 IP 位址或 CIDR 網段的連線請求。", "系統帳戶", "此帳戶僅用於登入 krFTP 管理程式，沒有 FTP/SFTP 檔案服務權限。", "關於 krFTP", "版本、版權與開源使用聲明。", "啟動服務", "停止服務", "設定", "啟動程式時自動啟動", "運行中", "已停止", "監聽位址", "目前線上連線", "新增使用者", "啟用 / 停用", "設定權限", "刪除使用者", "中斷選取連線", "重新整理日誌", "新增封鎖規則", "儲存系統帳戶"],
    "ja_JP": ["krFTP サーバーマネージャー", "FTP / SFTP サービスコンソール", "ログイン中", "サービス管理", "サービスユーザーと権限", "接続状況", "監査ログ", "IP ブロックリスト", "システムアカウント", "krFTP について", "FTP と SFTP の状態、待受アドレス、ポートを個別に管理します。", "サービスユーザー", "アカウント有効期限、ルートディレクトリ、プロトコル権限を管理します。", "接続セッション", "現在のセッションを確認し、必要に応じて切断します。", "監査ログ", "認証、転送、アーカイブ、サービス操作を追跡します。", "IP ブロックリスト", "指定した IP アドレスまたは CIDR ネットワークからの接続を拒否します。", "システムアカウント", "このアカウントは krFTP 管理画面へのログイン専用で、FTP/SFTP のファイルアクセス権はありません。", "krFTP について", "バージョン、著作権、オープンソース利用に関するお知らせ。", "サービス開始", "サービス停止", "設定", "アプリ起動時に開始", "実行中", "停止", "待受アドレス", "オンライン接続数", "ユーザーを追加", "有効 / 無効", "権限", "ユーザーを削除", "選択した接続を切断", "ログを更新", "ブロックルールを追加", "システムアカウントを保存"],
    "ko_KR": ["krFTP 서버 관리자", "FTP / SFTP 서비스 콘솔", "현재 관리자", "서비스 관리", "서비스 사용자 및 권한", "실시간 연결", "감사 로그", "IP 차단 목록", "시스템 계정", "krFTP 정보", "FTP 및 SFTP 상태, 수신 주소와 포트를 각각 관리합니다.", "서비스 사용자", "계정 만료일, 루트 디렉터리 및 프로토콜 권한을 관리합니다.", "연결 세션", "현재 세션을 보고 필요하면 연결을 끊습니다.", "감사 로그", "인증, 전송, 압축 및 서비스 관리 작업을 추적합니다.", "IP 차단 목록", "지정한 IP 주소 또는 CIDR 네트워크의 연결을 차단합니다.", "시스템 계정", "이 계정은 krFTP 관리자 로그인 전용이며 FTP/SFTP 파일 서비스 권한이 없습니다.", "krFTP 정보", "버전, 저작권 및 오픈 소스 사용 안내.", "서비스 시작", "서비스 중지", "구성", "앱 시작 시 자동 실행", "실행 중", "중지됨", "수신 주소", "현재 온라인 연결", "사용자 추가", "활성화 / 비활성화", "권한 설정", "사용자 삭제", "선택한 연결 끊기", "로그 새로 고침", "차단 규칙 추가", "시스템 계정 저장"],
    "es_ES": ["Administrador del servidor krFTP", "Consola de servicios FTP / SFTP", "Sesión iniciada como", "Administración de servicios", "Usuarios y permisos del servicio", "Conexiones en tiempo real", "Registro de auditoría", "Lista de bloqueo IP", "Cuenta del sistema", "Acerca de krFTP", "Administre por separado el estado, la dirección de escucha y el puerto de FTP y SFTP.", "Usuarios del servicio", "Administre caducidad, directorios raíz y permisos de protocolo.", "Sesiones de conexión", "Revise las sesiones activas y desconéctelas cuando sea necesario.", "Registro de auditoría", "Rastree autenticación, transferencias, archivos y acciones del servicio.", "Lista de bloqueo IP", "Bloquee conexiones desde una dirección IP o red CIDR.", "Cuenta del sistema", "Esta cuenta solo inicia sesión en krFTP y no tiene acceso a archivos FTP/SFTP.", "Acerca de krFTP", "Versión, derechos de autor y aviso de código abierto.", "Iniciar servicio", "Detener servicio", "Configurar", "Iniciar con la aplicación", "En ejecución", "Detenido", "Dirección de escucha", "Conexiones activas", "Agregar usuario", "Activar / desactivar", "Permisos", "Eliminar usuario", "Desconectar selección", "Actualizar registro", "Agregar regla de bloqueo", "Guardar cuenta del sistema"],
    "fr_FR": ["Gestionnaire de serveur krFTP", "Console de services FTP / SFTP", "Connecté en tant que", "Gestion des services", "Utilisateurs et autorisations", "Connexions en direct", "Journal d'audit", "Liste de blocage IP", "Compte système", "À propos de krFTP", "Gérez séparément l'état, l'adresse d'écoute et le port FTP et SFTP.", "Utilisateurs du service", "Gérez l'expiration des comptes, les répertoires racine et les autorisations.", "Sessions de connexion", "Consultez les sessions actives et déconnectez-les si nécessaire.", "Journal d'audit", "Suivez l'authentification, les transferts, les archives et les actions de service.", "Liste de blocage IP", "Bloquez les connexions d'une adresse IP ou d'un réseau CIDR.", "Compte système", "Ce compte sert uniquement à se connecter à krFTP et n'a aucun accès FTP/SFTP.", "À propos de krFTP", "Version, droits d'auteur et avis open source.", "Démarrer le service", "Arrêter le service", "Configurer", "Démarrer avec l'application", "En cours", "Arrêté", "Adresse d'écoute", "Connexions actives", "Ajouter un utilisateur", "Activer / désactiver", "Autorisations", "Supprimer l'utilisateur", "Déconnecter la sélection", "Actualiser le journal", "Ajouter une règle de blocage", "Enregistrer le compte système"],
    "de_DE": ["krFTP Serververwaltung", "FTP / SFTP Dienstkonsole", "Angemeldet als", "Dienstverwaltung", "Dienstbenutzer und Berechtigungen", "Live-Verbindungen", "Prüfprotokoll", "IP-Sperrliste", "Systemkonto", "Über krFTP", "Verwalten Sie Status, Abhöradresse und Port von FTP und SFTP getrennt.", "Dienstbenutzer", "Verwalten Sie Kontoablauf, Stammverzeichnisse und Protokollberechtigungen.", "Verbindungssitzungen", "Prüfen Sie aktive Sitzungen und trennen Sie diese bei Bedarf.", "Prüfprotokoll", "Verfolgen Sie Anmeldung, Übertragungen, Archive und Dienstaktionen.", "IP-Sperrliste", "Sperren Sie Verbindungen von einer IP-Adresse oder einem CIDR-Netzwerk.", "Systemkonto", "Dieses Konto meldet sich nur bei krFTP an und hat keinen FTP/SFTP-Dateizugriff.", "Über krFTP", "Version, Urheberrecht und Open-Source-Hinweis.", "Dienst starten", "Dienst stoppen", "Konfigurieren", "Mit Anwendung starten", "Wird ausgeführt", "Gestoppt", "Abhöradresse", "Aktive Verbindungen", "Benutzer hinzufügen", "Aktivieren / deaktivieren", "Berechtigungen", "Benutzer löschen", "Auswahl trennen", "Protokoll aktualisieren", "Sperrregel hinzufügen", "Systemkonto speichern"],
    "pt_BR": ["Gerenciador de servidor krFTP", "Console de serviços FTP / SFTP", "Conectado como", "Gerenciamento de serviços", "Usuários e permissões", "Conexões ao vivo", "Log de auditoria", "Lista de bloqueio IP", "Conta do sistema", "Sobre o krFTP", "Gerencie separadamente o estado, endereço de escuta e porta de FTP e SFTP.", "Usuários do serviço", "Gerencie expiração da conta, diretórios raiz e permissões de protocolo.", "Sessões de conexão", "Veja as sessões ativas e desconecte-as quando necessário.", "Log de auditoria", "Acompanhe autenticação, transferências, arquivos e ações do serviço.", "Lista de bloqueio IP", "Bloqueie conexões de um endereço IP ou rede CIDR.", "Conta do sistema", "Esta conta entra somente no krFTP e não tem acesso a arquivos FTP/SFTP.", "Sobre o krFTP", "Versão, direitos autorais e aviso de código aberto.", "Iniciar serviço", "Parar serviço", "Configurar", "Iniciar com o aplicativo", "Em execução", "Parado", "Endereço de escuta", "Conexões ativas", "Adicionar usuário", "Ativar / desativar", "Permissões", "Excluir usuário", "Desconectar seleção", "Atualizar log", "Adicionar regra de bloqueio", "Salvar conta do sistema"],
    "ru_RU": ["Менеджер сервера krFTP", "Консоль служб FTP / SFTP", "Выполнен вход как", "Управление службами", "Пользователи и права служб", "Текущие подключения", "Журнал аудита", "Чёрный список IP", "Системная учётная запись", "О krFTP", "Отдельно управляйте состоянием, адресом прослушивания и портом FTP и SFTP.", "Пользователи служб", "Управляйте сроком действия, корневыми каталогами и правами протоколов.", "Сеансы подключения", "Просматривайте активные сеансы и отключайте их при необходимости.", "Журнал аудита", "Отслеживайте вход, передачи, архивы и действия со службами.", "Чёрный список IP", "Блокируйте подключения с IP-адреса или сети CIDR.", "Системная учётная запись", "Эта учётная запись используется только для входа в krFTP и не имеет доступа к FTP/SFTP.", "О krFTP", "Версия, авторские права и уведомление об открытом коде.", "Запустить службу", "Остановить службу", "Настроить", "Запускать с приложением", "Работает", "Остановлена", "Адрес прослушивания", "Активные подключения", "Добавить пользователя", "Включить / отключить", "Права", "Удалить пользователя", "Отключить выбранное", "Обновить журнал", "Добавить правило блокировки", "Сохранить системную учётную запись"],
})
for _locale, _label in {
    "zh_TW": "登出", "ja_JP": "ログアウト", "ko_KR": "로그아웃",
    "es_ES": "Cerrar sesión", "fr_FR": "Déconnexion", "de_DE": "Abmelden",
    "pt_BR": "Sair", "ru_RU": "Выйти",
}.items():
    MAIN_TEXT[_locale].append(_label)

_DIALOG_EN = DIALOG_TEXT["en_US"]
for _locale, _values in {
    "zh_TW": ["儲存", "取消", "新增服務使用者", "服務使用者名稱", "初始密碼", "到期時間", "永不到期", "設定存取權限", "通訊協定範圍", "授權根目錄", "瀏覽", "FTP 與 SFTP", "僅 FTP", "僅 SFTP", "設定 {name} 服務", "監聽 IP", "監聽連接埠", "系統帳戶", "新密碼", "確認新密碼", "留空則不變更密碼", "版本 0.1.0", "版權所有 © krFTP Contributors。\n\nkrFTP 是非商業開源專案，僅供學習、個人使用與非商業部署。未經版權持有人明確授權，不得用於商業銷售、代管或服務。"],
    "ja_JP": ["保存", "キャンセル", "サービスユーザーを追加", "サービスユーザー名", "初期パスワード", "有効期限", "期限なし", "アクセス権限を設定", "プロトコル範囲", "許可するルート", "参照", "FTP と SFTP", "FTP のみ", "SFTP のみ", "{name} サービスを設定", "待受 IP", "待受ポート", "システムアカウント", "新しいパスワード", "新しいパスワードの確認", "空欄の場合は現在のパスワードを維持", "バージョン 0.1.0", "Copyright © krFTP Contributors.\n\nkrFTP は学習、個人利用、非商用展開のための非商用オープンソースプロジェクトです。著作権者の明示的な許可なく、商用販売、ホスティング、サービス提供に利用できません。"],
    "ko_KR": ["저장", "취소", "서비스 사용자 추가", "서비스 사용자 이름", "초기 비밀번호", "만료일", "만료 안 함", "접근 권한 구성", "프로토콜 범위", "허용된 루트", "찾아보기", "FTP 및 SFTP", "FTP만", "SFTP만", "{name} 서비스 구성", "수신 IP", "수신 포트", "시스템 계정", "새 비밀번호", "새 비밀번호 확인", "비워 두면 현재 비밀번호 유지", "버전 0.1.0", "Copyright © krFTP Contributors.\n\nkrFTP는 학습, 개인 사용 및 비상업적 배포를 위한 비상업 오픈 소스 프로젝트입니다. 저작권자의 명시적 허가 없이 상업적 판매, 호스팅 또는 서비스에 사용할 수 없습니다."],
    "es_ES": ["Guardar", "Cancelar", "Agregar usuario del servicio", "Nombre de usuario", "Contraseña inicial", "Caducidad", "Nunca caduca", "Configurar permisos de acceso", "Alcance del protocolo", "Raíz autorizada", "Examinar", "FTP y SFTP", "Solo FTP", "Solo SFTP", "Configurar servicio {name}", "IP de escucha", "Puerto de escucha", "Usuario del sistema", "Nueva contraseña", "Confirmar nueva contraseña", "Déjelo vacío para mantener la contraseña", "Versión 0.1.0", "Copyright © krFTP Contributors.\n\nkrFTP es un proyecto de código abierto no comercial para aprendizaje, uso personal y despliegues no comerciales. Sin autorización expresa del titular de derechos, no puede usarse para venta, alojamiento o servicios comerciales."],
    "fr_FR": ["Enregistrer", "Annuler", "Ajouter un utilisateur", "Nom d'utilisateur", "Mot de passe initial", "Expiration", "N'expire jamais", "Configurer les autorisations", "Portée du protocole", "Racine autorisée", "Parcourir", "FTP et SFTP", "FTP uniquement", "SFTP uniquement", "Configurer le service {name}", "IP d'écoute", "Port d'écoute", "Nom système", "Nouveau mot de passe", "Confirmer le mot de passe", "Laissez vide pour conserver le mot de passe", "Version 0.1.0", "Copyright © krFTP Contributors.\n\nkrFTP est un projet open source non commercial destiné à l'apprentissage, à l'usage personnel et aux déploiements non commerciaux. Sans autorisation explicite, il ne peut être utilisé pour la vente, l'hébergement ou des services commerciaux."],
    "de_DE": ["Speichern", "Abbrechen", "Dienstbenutzer hinzufügen", "Dienstbenutzername", "Anfangspasswort", "Ablaufdatum", "Läuft nie ab", "Zugriffsrechte konfigurieren", "Protokollbereich", "Freigegebenes Stammverzeichnis", "Durchsuchen", "FTP und SFTP", "Nur FTP", "Nur SFTP", "{name}-Dienst konfigurieren", "Abhör-IP", "Abhörport", "Systembenutzername", "Neues Passwort", "Neues Passwort bestätigen", "Leer lassen, um Passwort beizubehalten", "Version 0.1.0", "Copyright © krFTP Contributors.\n\nkrFTP ist ein nicht-kommerzielles Open-Source-Projekt für Lernen, private Nutzung und nicht-kommerzielle Bereitstellungen. Ohne ausdrückliche Genehmigung darf es nicht für kommerziellen Verkauf, Hosting oder Dienste verwendet werden."],
    "pt_BR": ["Salvar", "Cancelar", "Adicionar usuário do serviço", "Nome de usuário", "Senha inicial", "Expiração", "Nunca expira", "Configurar permissões de acesso", "Escopo do protocolo", "Raiz autorizada", "Procurar", "FTP e SFTP", "Somente FTP", "Somente SFTP", "Configurar serviço {name}", "IP de escuta", "Porta de escuta", "Nome do sistema", "Nova senha", "Confirmar nova senha", "Deixe vazio para manter a senha", "Versão 0.1.0", "Copyright © krFTP Contributors.\n\nkrFTP é um projeto de código aberto não comercial para aprendizado, uso pessoal e implantações não comerciais. Sem autorização explícita, não pode ser usado para venda, hospedagem ou serviços comerciais."],
    "ru_RU": ["Сохранить", "Отмена", "Добавить пользователя службы", "Имя пользователя службы", "Начальный пароль", "Срок действия", "Без срока действия", "Настроить права доступа", "Область протоколов", "Разрешённый корневой каталог", "Обзор", "FTP и SFTP", "Только FTP", "Только SFTP", "Настроить службу {name}", "IP прослушивания", "Порт прослушивания", "Системное имя", "Новый пароль", "Подтвердите новый пароль", "Оставьте пустым, чтобы сохранить пароль", "Версия 0.1.0", "Авторские права © krFTP Contributors.\n\nkrFTP — некоммерческий проект с открытым исходным кодом для обучения, личного использования и некоммерческих развёртываний. Без явного разрешения правообладателя его нельзя использовать для коммерческой продажи, хостинга или услуг."],
}.items():
    DIALOG_TEXT[_locale] = dict(zip(_DIALOG_EN, _values))
    DIALOG_TEXT[_locale]["author_contact"] = {
        "zh_TW": "作者聯絡方式", "ja_JP": "作者連絡先", "ko_KR": "작성자 연락처",
        "es_ES": "Contacto del autor", "fr_FR": "Contact de l'auteur", "de_DE": "Kontakt zum Autor",
        "pt_BR": "Contato do autor", "ru_RU": "Контакты автора",
    }[_locale] + "\nWeChat: Leon121706\nQQ: 1217067605"

EXTRA_TEXT = {
    "zh_CN": {"service":"服务", "user_headers":["服务用户名", "状态", "有效期", "协议范围", "授权根目录"], "session_headers":["会话 ID", "用户", "协议", "客户端 IP", "登录时间"], "log_headers":["时间", "用户", "协议", "IP", "操作", "路径", "结果"], "rule_headers":["IP/CIDR", "原因", "创建时间"], "enabled":"已启用", "disabled":"已禁用", "not_configured":"未配置", "success":"成功", "failed":"失败"},
    "en_US": {"service":"Service", "user_headers":["Service user", "Status", "Expiry", "Protocols", "Authorized root"], "session_headers":["Session ID", "User", "Protocol", "Client IP", "Login time"], "log_headers":["Time", "User", "Protocol", "IP", "Action", "Path", "Result"], "rule_headers":["IP/CIDR", "Reason", "Created"], "enabled":"Enabled", "disabled":"Disabled", "not_configured":"Not configured", "success":"Success", "failed":"Failed"},
    "zh_TW": {"service":"服務", "user_headers":["服務使用者", "狀態", "有效期", "通訊協定", "授權根目錄"], "session_headers":["工作階段 ID", "使用者", "通訊協定", "用戶端 IP", "登入時間"], "log_headers":["時間", "使用者", "通訊協定", "IP", "操作", "路徑", "結果"], "rule_headers":["IP/CIDR", "原因", "建立時間"], "enabled":"已啟用", "disabled":"已停用", "not_configured":"未設定", "success":"成功", "failed":"失敗"},
    "ja_JP": {"service":"サービス", "user_headers":["サービスユーザー", "状態", "有効期限", "プロトコル", "許可するルート"], "session_headers":["セッション ID", "ユーザー", "プロトコル", "クライアント IP", "ログイン時刻"], "log_headers":["時刻", "ユーザー", "プロトコル", "IP", "操作", "パス", "結果"], "rule_headers":["IP/CIDR", "理由", "作成日時"], "enabled":"有効", "disabled":"無効", "not_configured":"未設定", "success":"成功", "failed":"失敗"},
    "ko_KR": {"service":"서비스", "user_headers":["서비스 사용자", "상태", "만료일", "프로토콜", "허용된 루트"], "session_headers":["세션 ID", "사용자", "프로토콜", "클라이언트 IP", "로그인 시간"], "log_headers":["시간", "사용자", "프로토콜", "IP", "작업", "경로", "결과"], "rule_headers":["IP/CIDR", "사유", "생성 시간"], "enabled":"활성화됨", "disabled":"비활성화됨", "not_configured":"구성 안 됨", "success":"성공", "failed":"실패"},
    "es_ES": {"service":"Servicio", "user_headers":["Usuario", "Estado", "Caducidad", "Protocolos", "Raíz autorizada"], "session_headers":["ID de sesión", "Usuario", "Protocolo", "IP de cliente", "Hora de acceso"], "log_headers":["Hora", "Usuario", "Protocolo", "IP", "Acción", "Ruta", "Resultado"], "rule_headers":["IP/CIDR", "Motivo", "Creado"], "enabled":"Activo", "disabled":"Desactivado", "not_configured":"Sin configurar", "success":"Correcto", "failed":"Error"},
    "fr_FR": {"service":"Service", "user_headers":["Utilisateur", "État", "Expiration", "Protocoles", "Racine autorisée"], "session_headers":["ID de session", "Utilisateur", "Protocole", "IP cliente", "Heure de connexion"], "log_headers":["Heure", "Utilisateur", "Protocole", "IP", "Action", "Chemin", "Résultat"], "rule_headers":["IP/CIDR", "Motif", "Créé"], "enabled":"Activé", "disabled":"Désactivé", "not_configured":"Non configuré", "success":"Réussi", "failed":"Échec"},
    "de_DE": {"service":"Dienst", "user_headers":["Dienstbenutzer", "Status", "Ablauf", "Protokolle", "Stammverzeichnis"], "session_headers":["Sitzungs-ID", "Benutzer", "Protokoll", "Client-IP", "Anmeldezeit"], "log_headers":["Zeit", "Benutzer", "Protokoll", "IP", "Aktion", "Pfad", "Ergebnis"], "rule_headers":["IP/CIDR", "Grund", "Erstellt"], "enabled":"Aktiviert", "disabled":"Deaktiviert", "not_configured":"Nicht konfiguriert", "success":"Erfolgreich", "failed":"Fehlgeschlagen"},
    "pt_BR": {"service":"Serviço", "user_headers":["Usuário", "Status", "Expiração", "Protocolos", "Raiz autorizada"], "session_headers":["ID da sessão", "Usuário", "Protocolo", "IP do cliente", "Hora do login"], "log_headers":["Hora", "Usuário", "Protocolo", "IP", "Ação", "Caminho", "Resultado"], "rule_headers":["IP/CIDR", "Motivo", "Criado"], "enabled":"Ativado", "disabled":"Desativado", "not_configured":"Não configurado", "success":"Sucesso", "failed":"Falha"},
    "ru_RU": {"service":"Служба", "user_headers":["Пользователь службы", "Статус", "Срок действия", "Протоколы", "Корневой каталог"], "session_headers":["ID сеанса", "Пользователь", "Протокол", "IP клиента", "Время входа"], "log_headers":["Время", "Пользователь", "Протокол", "IP", "Действие", "Путь", "Результат"], "rule_headers":["IP/CIDR", "Причина", "Создано"], "enabled":"Включён", "disabled":"Отключён", "not_configured":"Не настроено", "success":"Успешно", "failed":"Ошибка"},
}

ACTION_LABELS_BY_LOCALE = {
    "zh_CN": ACTION_LABELS, "en_US": ACTION_LABELS_EN,
    "zh_TW": {"LOGIN":"登入", "UPLOAD":"上傳", "DOWNLOAD":"下載", "DELETE":"刪除", "RENAME":"重新命名", "COMPRESS":"壓縮", "DECOMPRESS":"解壓縮", "ARCHIVE":"封存操作", "KICK_SESSION":"中斷連線", "STOP_SERVICES":"停止所有服務", "DELETE_SERVICE_USER":"刪除服務使用者", "START_FTP":"啟動 FTP 服務", "STOP_FTP":"停止 FTP 服務", "START_SFTP":"啟動 SFTP 服務", "STOP_SFTP":"停止 SFTP 服務"},
    "ja_JP": {"LOGIN":"ログイン", "UPLOAD":"アップロード", "DOWNLOAD":"ダウンロード", "DELETE":"削除", "RENAME":"名前を変更", "COMPRESS":"圧縮", "DECOMPRESS":"展開", "ARCHIVE":"アーカイブ操作", "KICK_SESSION":"接続を切断", "STOP_SERVICES":"すべてのサービスを停止", "DELETE_SERVICE_USER":"サービスユーザーを削除", "START_FTP":"FTP サービスを開始", "STOP_FTP":"FTP サービスを停止", "START_SFTP":"SFTP サービスを開始", "STOP_SFTP":"SFTP サービスを停止"},
    "ko_KR": {"LOGIN":"로그인", "UPLOAD":"업로드", "DOWNLOAD":"다운로드", "DELETE":"삭제", "RENAME":"이름 바꾸기", "COMPRESS":"압축", "DECOMPRESS":"압축 풀기", "ARCHIVE":"보관 작업", "KICK_SESSION":"연결 끊기", "STOP_SERVICES":"모든 서비스 중지", "DELETE_SERVICE_USER":"서비스 사용자 삭제", "START_FTP":"FTP 서비스 시작", "STOP_FTP":"FTP 서비스 중지", "START_SFTP":"SFTP 서비스 시작", "STOP_SFTP":"SFTP 서비스 중지"},
}
for _locale in ("es_ES", "fr_FR", "de_DE", "pt_BR", "ru_RU"):
    ACTION_LABELS_BY_LOCALE[_locale] = ACTION_LABELS_EN

PERMISSION_TEXT = {
    "zh_CN": {"list":"列表查看", "read":"读取", "write":"写入", "append":"追加", "delete_file":"删除文件", "rename_file":"重命名文件", "create_dir":"创建目录", "delete_dir":"删除目录", "rename_dir":"重命名目录", "compress":"压缩", "decompress":"解压"},
    "en_US": {"list":"List", "read":"Read", "write":"Write", "append":"Append", "delete_file":"Delete files", "rename_file":"Rename files", "create_dir":"Create folders", "delete_dir":"Delete folders", "rename_dir":"Rename folders", "compress":"Compress", "decompress":"Extract"},
    "zh_TW": {"list":"列表檢視", "read":"讀取", "write":"寫入", "append":"附加", "delete_file":"刪除檔案", "rename_file":"重新命名檔案", "create_dir":"建立目錄", "delete_dir":"刪除目錄", "rename_dir":"重新命名目錄", "compress":"壓縮", "decompress":"解壓縮"},
    "ja_JP": {"list":"一覧", "read":"読み取り", "write":"書き込み", "append":"追記", "delete_file":"ファイル削除", "rename_file":"ファイル名変更", "create_dir":"フォルダー作成", "delete_dir":"フォルダー削除", "rename_dir":"フォルダー名変更", "compress":"圧縮", "decompress":"展開"},
    "ko_KR": {"list":"목록", "read":"읽기", "write":"쓰기", "append":"추가", "delete_file":"파일 삭제", "rename_file":"파일 이름 변경", "create_dir":"폴더 만들기", "delete_dir":"폴더 삭제", "rename_dir":"폴더 이름 변경", "compress":"압축", "decompress":"압축 풀기"},
    "es_ES": {"list":"Listar", "read":"Leer", "write":"Escribir", "append":"Anexar", "delete_file":"Eliminar archivos", "rename_file":"Renombrar archivos", "create_dir":"Crear carpetas", "delete_dir":"Eliminar carpetas", "rename_dir":"Renombrar carpetas", "compress":"Comprimir", "decompress":"Extraer"},
    "fr_FR": {"list":"Lister", "read":"Lire", "write":"Écrire", "append":"Ajouter", "delete_file":"Supprimer les fichiers", "rename_file":"Renommer les fichiers", "create_dir":"Créer les dossiers", "delete_dir":"Supprimer les dossiers", "rename_dir":"Renommer les dossiers", "compress":"Compresser", "decompress":"Extraire"},
    "de_DE": {"list":"Auflisten", "read":"Lesen", "write":"Schreiben", "append":"Anhängen", "delete_file":"Dateien löschen", "rename_file":"Dateien umbenennen", "create_dir":"Ordner erstellen", "delete_dir":"Ordner löschen", "rename_dir":"Ordner umbenennen", "compress":"Komprimieren", "decompress":"Entpacken"},
    "pt_BR": {"list":"Listar", "read":"Ler", "write":"Gravar", "append":"Anexar", "delete_file":"Excluir arquivos", "rename_file":"Renomear arquivos", "create_dir":"Criar pastas", "delete_dir":"Excluir pastas", "rename_dir":"Renomear pastas", "compress":"Compactar", "decompress":"Extrair"},
    "ru_RU": {"list":"Просмотр", "read":"Чтение", "write":"Запись", "append":"Добавление", "delete_file":"Удаление файлов", "rename_file":"Переименование файлов", "create_dir":"Создание папок", "delete_dir":"Удаление папок", "rename_dir":"Переименование папок", "compress":"Сжатие", "decompress":"Распаковка"},
}

PERMISSION_COLUMN_TEXT = {
    "zh_CN": "权限", "en_US": "Permissions", "zh_TW": "權限", "ja_JP": "権限", "ko_KR": "권한",
    "es_ES": "Permisos", "fr_FR": "Autorisations", "de_DE": "Berechtigungen", "pt_BR": "Permissões", "ru_RU": "Права",
}

USER_PASSWORD_TEXT = {
    "zh_CN": ["修改服务用户密码", "新密码", "确认新密码", "至少 8 个字符", "再次输入新密码", "保存", "取消", "两次输入的密码不一致。", "密码已更新。", "全选"],
    "en_US": ["Change Service User Password", "New password", "Confirm new password", "At least 8 characters", "Enter the new password again", "Save", "Cancel", "The two passwords do not match.", "Password updated.", "Select all"],
    "zh_TW": ["修改服務使用者密碼", "新密碼", "確認新密碼", "至少 8 個字元", "再次輸入新密碼", "儲存", "取消", "兩次輸入的密碼不一致。", "密碼已更新。", "全選"],
    "ja_JP": ["サービスユーザーのパスワードを変更", "新しいパスワード", "新しいパスワードの確認", "8 文字以上", "新しいパスワードをもう一度入力", "保存", "キャンセル", "2 回入力したパスワードが一致しません。", "パスワードを更新しました。", "すべて選択"],
    "ko_KR": ["서비스 사용자 비밀번호 변경", "새 비밀번호", "새 비밀번호 확인", "8자 이상", "새 비밀번호를 다시 입력", "저장", "취소", "두 비밀번호가 일치하지 않습니다.", "비밀번호가 업데이트되었습니다.", "모두 선택"],
    "es_ES": ["Cambiar contraseña de usuario", "Nueva contraseña", "Confirmar nueva contraseña", "Al menos 8 caracteres", "Vuelva a introducir la nueva contraseña", "Guardar", "Cancelar", "Las dos contraseñas no coinciden.", "Contraseña actualizada.", "Seleccionar todo"],
    "fr_FR": ["Modifier le mot de passe utilisateur", "Nouveau mot de passe", "Confirmer le mot de passe", "Au moins 8 caractères", "Saisissez à nouveau le nouveau mot de passe", "Enregistrer", "Annuler", "Les deux mots de passe ne correspondent pas.", "Mot de passe mis à jour.", "Tout sélectionner"],
    "de_DE": ["Dienstbenutzerkennwort ändern", "Neues Kennwort", "Neues Kennwort bestätigen", "Mindestens 8 Zeichen", "Neues Kennwort erneut eingeben", "Speichern", "Abbrechen", "Die beiden Kennwörter stimmen nicht überein.", "Kennwort aktualisiert.", "Alle auswählen"],
    "pt_BR": ["Alterar senha do usuário", "Nova senha", "Confirmar nova senha", "Pelo menos 8 caracteres", "Digite a nova senha novamente", "Salvar", "Cancelar", "As duas senhas não coincidem.", "Senha atualizada.", "Selecionar tudo"],
    "ru_RU": ["Изменить пароль пользователя", "Новый пароль", "Подтвердите новый пароль", "Не менее 8 символов", "Введите новый пароль ещё раз", "Сохранить", "Отмена", "Пароли не совпадают.", "Пароль обновлён.", "Выбрать все"],
}

PERMISSION_DIALOG_TEXT = {
    "zh_CN": ["选择授权根目录", "无法保存", "授权根目录不存在或不是目录。", "请至少选择一项操作权限。", "请先选择服务用户。", "权限已保存。"],
    "en_US": ["Select authorized root", "Unable to save", "The authorized root does not exist or is not a directory.", "Select at least one permission.", "Select a service user first.", "Permissions saved."],
    "zh_TW": ["選擇授權根目錄", "無法儲存", "授權根目錄不存在或不是目錄。", "請至少選擇一項操作權限。", "請先選擇服務使用者。", "權限已儲存。"],
    "ja_JP": ["許可するルートを選択", "保存できません", "許可するルートが存在しないか、ディレクトリではありません。", "少なくとも 1 つの権限を選択してください。", "サービスユーザーを選択してください。", "権限を保存しました。"],
    "ko_KR": ["허용된 루트 선택", "저장할 수 없음", "허용된 루트가 없거나 폴더가 아닙니다.", "권한을 하나 이상 선택하세요.", "서비스 사용자를 먼저 선택하세요.", "권한이 저장되었습니다."],
    "es_ES": ["Seleccionar raíz autorizada", "No se puede guardar", "La raíz autorizada no existe o no es una carpeta.", "Seleccione al menos un permiso.", "Seleccione primero un usuario del servicio.", "Permisos guardados."],
    "fr_FR": ["Sélectionner la racine autorisée", "Impossible d'enregistrer", "La racine autorisée n'existe pas ou n'est pas un dossier.", "Sélectionnez au moins une autorisation.", "Sélectionnez d'abord un utilisateur.", "Autorisations enregistrées."],
    "de_DE": ["Freigegebenes Stammverzeichnis auswählen", "Speichern nicht möglich", "Das freigegebene Stammverzeichnis existiert nicht oder ist kein Ordner.", "Wählen Sie mindestens eine Berechtigung aus.", "Wählen Sie zuerst einen Dienstbenutzer aus.", "Berechtigungen gespeichert."],
    "pt_BR": ["Selecionar raiz autorizada", "Não foi possível salvar", "A raiz autorizada não existe ou não é uma pasta.", "Selecione pelo menos uma permissão.", "Selecione primeiro um usuário do serviço.", "Permissões salvas."],
    "ru_RU": ["Выберите корневой каталог", "Не удалось сохранить", "Разрешённый корневой каталог не существует или не является папкой.", "Выберите хотя бы одно право.", "Сначала выберите пользователя службы.", "Права сохранены."],
}

LOG_FILTER_TEXT = {
    "zh_CN": ["全部用户", "全部协议", "全部操作", "IP 地址", "时间范围", "开始时间", "结束时间", "查询", "重置", "每页", "上一页", "下一页", "第 {page} / {pages} 页，共 {total} 条"],
    "en_US": ["All users", "All protocols", "All actions", "IP address", "Time range", "Start time", "End time", "Search", "Reset", "Per page", "Previous", "Next", "Page {page} / {pages}, {total} total"],
    "zh_TW": ["所有使用者", "所有通訊協定", "所有操作", "IP 位址", "時間範圍", "開始時間", "結束時間", "查詢", "重設", "每頁", "上一頁", "下一頁", "第 {page} / {pages} 頁，共 {total} 筆"],
    "ja_JP": ["すべてのユーザー", "すべてのプロトコル", "すべての操作", "IP アドレス", "期間", "開始時刻", "終了時刻", "検索", "リセット", "件/ページ", "前へ", "次へ", "{page} / {pages} ページ、全 {total} 件"],
    "ko_KR": ["모든 사용자", "모든 프로토콜", "모든 작업", "IP 주소", "기간", "시작 시간", "종료 시간", "조회", "초기화", "페이지당", "이전", "다음", "{page} / {pages}페이지, 총 {total}건"],
    "es_ES": ["Todos los usuarios", "Todos los protocolos", "Todas las acciones", "Dirección IP", "Rango de tiempo", "Hora inicial", "Hora final", "Buscar", "Restablecer", "Por página", "Anterior", "Siguiente", "Página {page} / {pages}, {total} en total"],
    "fr_FR": ["Tous les utilisateurs", "Tous les protocoles", "Toutes les actions", "Adresse IP", "Plage horaire", "Début", "Fin", "Rechercher", "Réinitialiser", "Par page", "Précédent", "Suivant", "Page {page} / {pages}, {total} au total"],
    "de_DE": ["Alle Benutzer", "Alle Protokolle", "Alle Aktionen", "IP-Adresse", "Zeitraum", "Startzeit", "Endzeit", "Suchen", "Zurücksetzen", "Pro Seite", "Zurück", "Weiter", "Seite {page} / {pages}, {total} insgesamt"],
    "pt_BR": ["Todos os usuários", "Todos os protocolos", "Todas as ações", "Endereço IP", "Período", "Hora inicial", "Hora final", "Pesquisar", "Redefinir", "Por página", "Anterior", "Próxima", "Página {page} / {pages}, {total} no total"],
    "ru_RU": ["Все пользователи", "Все протоколы", "Все действия", "IP-адрес", "Период", "Начало", "Окончание", "Поиск", "Сброс", "На странице", "Назад", "Далее", "Страница {page} / {pages}, всего {total}"],
}

TRAY_TEXT = {
    "zh_CN": ["显示管理控制台", "启动 FTP/SFTP 服务", "停止 FTP/SFTP 服务", "退出 krFTP", "服务继续在系统托盘中运行。"],
    "en_US": ["Show Management Console", "Start FTP/SFTP Services", "Stop FTP/SFTP Services", "Exit krFTP", "Services continue running in the system tray."],
    "zh_TW": ["顯示管理控制台", "啟動 FTP/SFTP 服務", "停止 FTP/SFTP 服務", "結束 krFTP", "服務會繼續在系統匣中運行。"],
    "ja_JP": ["管理コンソールを表示", "FTP/SFTP サービスを開始", "FTP/SFTP サービスを停止", "krFTP を終了", "サービスはシステムトレイで引き続き実行されます。"],
    "ko_KR": ["관리 콘솔 표시", "FTP/SFTP 서비스 시작", "FTP/SFTP 서비스 중지", "krFTP 종료", "서비스는 시스템 트레이에서 계속 실행됩니다."],
    "es_ES": ["Mostrar consola de administración", "Iniciar servicios FTP/SFTP", "Detener servicios FTP/SFTP", "Salir de krFTP", "Los servicios continúan ejecutándose en la bandeja del sistema."],
    "fr_FR": ["Afficher la console d'administration", "Démarrer les services FTP/SFTP", "Arrêter les services FTP/SFTP", "Quitter krFTP", "Les services continuent de s'exécuter dans la zone de notification."],
    "de_DE": ["Verwaltungskonsole anzeigen", "FTP/SFTP-Dienste starten", "FTP/SFTP-Dienste stoppen", "krFTP beenden", "Die Dienste werden weiterhin im Infobereich ausgeführt."],
    "pt_BR": ["Mostrar console de gerenciamento", "Iniciar serviços FTP/SFTP", "Parar serviços FTP/SFTP", "Sair do krFTP", "Os serviços continuam em execução na bandeja do sistema."],
    "ru_RU": ["Показать консоль управления", "Запустить службы FTP/SFTP", "Остановить службы FTP/SFTP", "Выйти из krFTP", "Службы продолжают работать в системном трее."],
}


class PasswordChangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改初始管理员密码")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.Password)
        form.addRow("新密码", self.password)
        form.addRow("确认密码", self.confirm)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def accept(self):
        if len(self.password.text()) < 8 or self.password.text() != self.confirm.text():
            QMessageBox.warning(self, "无法保存", "密码至少 8 个字符，且两次输入必须一致。")
            return
        super().accept()


class UserDialog(QDialog):
    def __init__(self, locale, parent=None):
        super().__init__(parent)
        text = dialog_text(locale); self.setWindowTitle(text["add_user"])
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.expiry = QDateTimeEdit(QDateTime.currentDateTime().addDays(30))
        self.expiry.setCalendarPopup(True)
        self.no_expiry = QCheckBox(text["never"])
        form.addRow(text["username"], self.username)
        form.addRow(text["initial_password"], self.password)
        form.addRow(text["expiry"], self.expiry)
        form.addRow("", self.no_expiry)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        expiry = None if self.no_expiry.isChecked() else self.expiry.dateTime().toPython()
        return self.username.text().strip(), self.password.text(), expiry


class ServiceUserPasswordDialog(QDialog):
    def __init__(self, username, locale, parent=None):
        super().__init__(parent)
        self.text = USER_PASSWORD_TEXT.get(locale, USER_PASSWORD_TEXT["zh_CN"])
        self.setWindowTitle(f"{self.text[0]}: {username}")
        self.setMinimumWidth(460)
        layout = QVBoxLayout(self); layout.setContentsMargins(26, 24, 26, 22); layout.setSpacing(10)
        form = QFormLayout(); form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.Password); self.password.setPlaceholderText(self.text[3])
        self.confirm = QLineEdit(); self.confirm.setEchoMode(QLineEdit.Password); self.confirm.setPlaceholderText(self.text[4]); self.confirm.returnPressed.connect(self.validate)
        form.addRow(self.text[1], self.password); form.addRow(self.text[2], self.confirm); layout.addLayout(form)
        self.status = QLabel(); self.status.setObjectName("status"); self.status.setWordWrap(True); self.status.setMinimumHeight(28); layout.addWidget(self.status)
        buttons = QDialogButtonBox(); save = buttons.addButton(self.text[5], QDialogButtonBox.AcceptRole); buttons.addButton(self.text[6], QDialogButtonBox.RejectRole)
        save.clicked.connect(self.validate); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def validate(self):
        if len(self.password.text()) < 8:
            self.status.setText(self.text[3])
        elif self.password.text() != self.confirm.text():
            self.status.setText(self.text[7])
        else:
            self.accept()


class RootPermissionDialog(QDialog):
    def __init__(self, db, user, locale, parent=None):
        super().__init__(parent)
        self.db, self.user, self.locale = db, user, locale
        self.roots = db.user_roots(user.id)
        text = dialog_text(locale); self.setWindowTitle(f"{text['permission']}: {user.username}")
        self.setMinimumSize(760, 510)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(14)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.protocol = QComboBox()
        self.protocol.addItem(text["ftp_sftp"], "BOTH")
        self.protocol.addItem(text["ftp_only"], "FTP")
        self.protocol.addItem(text["sftp_only"], "SFTP")
        self.protocol.currentIndexChanged.connect(self._load_saved_permission)
        self.root_path = QLineEdit(str(Path.cwd()))
        browse = QPushButton(text["browse"])
        browse.clicked.connect(self.choose_folder)
        path_row = QHBoxLayout()
        path_row.addWidget(self.root_path)
        path_row.addWidget(browse)
        form.addRow(text["protocol"], self.protocol)
        layout.addLayout(form)
        root_label = QLabel(text["root"]); root_label.setObjectName("fieldLabel")
        layout.addWidget(root_label); layout.addLayout(path_row)
        divider = QFrame(); divider.setFrameShape(QFrame.HLine); divider.setFrameShadow(QFrame.Sunken); layout.addWidget(divider)
        self.checks = {}
        permission_header = QHBoxLayout()
        permission_header.addWidget(QLabel(text["permission"]))
        permission_header.addStretch()
        self.select_all = QCheckBox(USER_PASSWORD_TEXT.get(locale, USER_PASSWORD_TEXT["zh_CN"])[9])
        self.select_all.toggled.connect(self._set_all_permissions)
        permission_header.addWidget(self.select_all)
        layout.addLayout(permission_header)
        grid = QGridLayout()
        grid.setHorizontalSpacing(28); grid.setVerticalSpacing(12)
        labels = PERMISSION_TEXT.get(locale, PERMISSION_TEXT["zh_CN"])
        for index, permission in enumerate(sorted(ALL_PERMISSIONS)):
            check = QCheckBox(labels[permission])
            check.toggled.connect(self._sync_select_all)
            self.checks[permission] = check
            grid.addWidget(check, index // 3, index % 3)
        layout.addLayout(grid)
        layout.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept_if_valid)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._load_saved_permission()

    def _load_saved_permission(self):
        protocol = self.protocol.currentData()
        root = next((item for item in self.roots if item.protocol == protocol), None)
        if root is None and protocol in {"FTP", "SFTP"}:
            root = next((item for item in self.roots if item.protocol == "BOTH"), None)
        if root is None:
            self.root_path.setText(str(Path.cwd()))
            selected = {"list", "read"} if not self.roots else set()
        else:
            self.root_path.setText(root.root_path)
            try:
                selected = set(json.loads(root.permissions))
            except (TypeError, json.JSONDecodeError):
                selected = set()
        for permission, check in self.checks.items():
            check.setChecked(permission in selected)
        self._sync_select_all()

    def _set_all_permissions(self, checked):
        for check in self.checks.values():
            check.blockSignals(True)
            check.setChecked(checked)
            check.blockSignals(False)

    def _sync_select_all(self):
        checked = bool(self.checks) and all(check.isChecked() for check in self.checks.values())
        self.select_all.blockSignals(True)
        self.select_all.setChecked(checked)
        self.select_all.blockSignals(False)

    def choose_folder(self):
        labels = PERMISSION_DIALOG_TEXT.get(self.locale, PERMISSION_DIALOG_TEXT["zh_CN"])
        folder = QFileDialog.getExistingDirectory(self, labels[0], self.root_path.text())
        if folder:
            self.root_path.setText(folder)

    def _accept_if_valid(self):
        if not Path(self.root_path.text()).is_dir():
            labels = PERMISSION_DIALOG_TEXT.get(self.locale, PERMISSION_DIALOG_TEXT["zh_CN"])
            QMessageBox.warning(self, labels[1], labels[2])
            return
        if not any(check.isChecked() for check in self.checks.values()):
            labels = PERMISSION_DIALOG_TEXT.get(self.locale, PERMISSION_DIALOG_TEXT["zh_CN"])
            QMessageBox.warning(self, labels[1], labels[3])
            return
        self.accept()

    def save(self):
        if self.exec() == QDialog.Accepted:
            selected = [key for key, check in self.checks.items() if check.isChecked()]
            root_path = Path(self.root_path.text())
            try:
                self.db.save_root(self.user.id, self.protocol.currentData(), str(root_path), selected)
                return True
            except Exception as exc:
                QMessageBox.warning(self, "无法保存", str(exc))
        return False


class ServiceConfigDialog(QDialog):
    def __init__(self, db, service_name, locale, parent=None):
        super().__init__(parent)
        self.db, self.service_name = db, service_name
        text = dialog_text(locale); self.setWindowTitle(text["service_config"].format(name=service_name))
        self.setFixedWidth(420)
        settings = db.settings()
        layout = QVBoxLayout(self); form = QFormLayout()
        self.bind_ip = QComboBox(); self.bind_ip.setEditable(True); self.bind_ip.addItems(["0.0.0.0", "127.0.0.1", "::"]); self.bind_ip.setCurrentText(settings["bind_ip"])
        self.port = QSpinBox(); self.port.setRange(1, 65535); self.port.setValue(int(settings["ftp_port" if service_name == "FTP" else "sftp_port"]))
        form.addRow(text["listen_ip"], self.bind_ip); form.addRow(text["listen_port"], self.port); layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def save(self):
        if self.exec() == QDialog.Accepted:
            key = "ftp_port" if self.service_name == "FTP" else "sftp_port"
            self.db.update_settings({"bind_ip": self.bind_ip.currentText().strip(), key: str(self.port.value())})


class MainWindow(QMainWindow):
    def __init__(self, db, services, login_user, icon, languages, parent=None):
        super().__init__(parent)
        self.db, self.services, self.login_user, self.languages = db, services, login_user, languages
        self.app_icon = icon
        self.locale = self.db.settings().get("language", "zh_CN")
        self.setWindowTitle("krFTP Server Manager")
        self.setWindowIcon(icon)
        self.resize(1240, 760)
        self.setMinimumSize(980, 640)
        self._center_on_screen()
        self.setStyleSheet(APP_STYLE)
        self._build_ui()
        self.retranslate_ui()
        self.refresh_live_data()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_live_data)
        self.timer.start(1000)
        self.start_if_configured()

    def _build_ui(self):
        root = QWidget(); root_layout = QVBoxLayout(root); root_layout.setContentsMargins(0, 0, 0, 0); root_layout.setSpacing(0)
        top_bar = QFrame(); top_bar.setObjectName("topBar"); top_bar.setFixedHeight(66); top_layout = QHBoxLayout(top_bar); top_layout.setContentsMargins(24, 0, 24, 0)
        titles = QVBoxLayout(); title = QLabel("krFTP"); title.setObjectName("appTitle"); self.top_subtitle = QLabel(); self.top_subtitle.setObjectName("appSubtitle"); titles.addWidget(title); titles.addWidget(self.top_subtitle); top_layout.addLayout(titles); top_layout.addStretch()
        self.user_label = QLabel(); self.user_label.setObjectName("userLabel"); top_layout.addWidget(self.user_label)
        self.sign_out_button = QPushButton(); self.sign_out_button.setObjectName("signOutButton"); self.sign_out_button.clicked.connect(self.sign_out)
        top_layout.addWidget(self.sign_out_button)
        root_layout.addWidget(top_bar)
        body = QHBoxLayout(); body.setContentsMargins(0, 0, 0, 0); body.setSpacing(0)
        self.navigation = QListWidget(); self.navigation.setObjectName("navigation")
        self.navigation.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.navigation.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.navigation.setTextElideMode(Qt.ElideNone)
        self.navigation.setMinimumWidth(196)
        self.navigation.addItems(["", "", "", "", "", "", ""])
        self.navigation.setCurrentRow(0)
        body.addWidget(self.navigation)
        content = QWidget(); content_layout = QVBoxLayout(content); content_layout.setContentsMargins(22, 22, 22, 22)
        self.pages = QStackedWidget(); content_layout.addWidget(self.pages); body.addWidget(content, 1)
        root_layout.addLayout(body, 1); self.setCentralWidget(root)
        self.pages.addWidget(self._dashboard_page())
        self.pages.addWidget(self._users_page())
        self.pages.addWidget(self._sessions_page())
        self.pages.addWidget(self._logs_page())
        self.pages.addWidget(self._blacklist_page())
        self.pages.addWidget(self._system_account_page())
        self.pages.addWidget(self._about_page())
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)

    def _center_on_screen(self):
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen:
            frame = self.frameGeometry()
            frame.moveCenter(screen.availableGeometry().center())
            self.move(frame.topLeft())

    def _text(self):
        return MAIN_TEXT.get(self.locale, MAIN_TEXT["zh_CN"])

    def _extra(self):
        return EXTRA_TEXT.get(self.locale, EXTRA_TEXT["zh_CN"])

    def retranslate_ui(self):
        text = self._text()
        self.setWindowTitle(text[0]); self.top_subtitle.setText(text[1]); self.user_label.setText(f"{text[2]}  {self.login_user.username}")
        self.sign_out_button.setText(text[39])
        for index, label in enumerate(text[3:10]): self.navigation.item(index).setText(label)
        self._resize_navigation()
        for (title, hint), values in zip(self.page_headers, ((text[3], text[10]), (text[11], text[12]), (text[13], text[14]), (text[15], text[16]), (text[17], text[18]), (text[19], text[20]), (text[21], text[22]))):
            title.setText(values[0]); hint.setText(values[1])
        extra = self._extra()
        self.ftp_title.setText(f"FTP {extra['service']}"); self.sftp_title.setText(f"SFTP {extra['service']}")
        self.ftp_config.setText(text[25]); self.sftp_config.setText(text[25]); self.ftp_autostart.setText(text[26]); self.sftp_autostart.setText(text[26])
        self.users_table.setHorizontalHeaderLabels(extra["user_headers"] + [PERMISSION_COLUMN_TEXT.get(self.locale, PERMISSION_COLUMN_TEXT["zh_CN"])])
        self.sessions_table.setHorizontalHeaderLabels(extra["session_headers"])
        self.logs_table.setHorizontalHeaderLabels(extra["log_headers"])
        self.rules_table.setHorizontalHeaderLabels(extra["rule_headers"])
        password_text = USER_PASSWORD_TEXT.get(self.locale, USER_PASSWORD_TEXT["zh_CN"])
        for widget, value in ((self.add_user_button, text[31]), (self.toggle_user_button, text[32]), (self.permission_button, text[33]), (self.change_user_password_button, password_text[0]), (self.delete_user_button, text[34]), (self.kick_button, text[35]), (self.add_rule_button, text[37]), (self.save_system_button, text[38])):
            widget.setText(value)
        self._retranslate_log_filters()
        dialog = dialog_text(self.locale)
        self.system_user_row.setText(dialog["system_user"])
        self.system_new_password_row.setText(dialog["new_password"])
        self.system_confirm_password_row.setText(dialog["confirm_password"])
        self.system_password.setPlaceholderText(dialog["leave_blank"])
        self.system_password_confirm.setPlaceholderText(dialog["confirm_password"])
        self.about_version.setText(dialog["about_version"])
        self.about_copyright.setText(dialog["copyright"])
        self.about_author_contact.setText(dialog["author_contact"])
        self._retranslate_tray()
        self.refresh_live_data(); self.refresh_logs(); self.refresh_users()

    def _resize_navigation(self):
        """Fit the sidebar to translated labels without exposing scrollbars."""
        metrics = QFontMetrics(self.navigation.font())
        labels = [self.navigation.item(index).text() for index in range(self.navigation.count())]
        width = max((metrics.horizontalAdvance(label) for label in labels), default=0) + 48
        self.navigation.setFixedWidth(max(196, min(width, 360)))

    def showEvent(self, event):
        super().showEvent(event)
        if not getattr(self, "_positioned", False):
            self._positioned = True
            self._center_on_screen()
        if not getattr(self, "_tray_initialized", False):
            self._tray_initialized = True
            # Register only after the native window is visible. Windows can
            # ignore tray registration performed before the event loop owns a
            # visible top-level window, especially after Explorer restarts.
            QTimer.singleShot(0, self._create_tray)

    def _page_shell(self, title, subtitle, expand=True):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(16)
        heading = QVBoxLayout(); heading.setSpacing(2); title_label = QLabel(title); title_label.setObjectName("pageTitle"); hint = QLabel(subtitle); hint.setObjectName("appSubtitle"); heading.addWidget(title_label); heading.addWidget(hint); layout.addLayout(heading)
        if not hasattr(self, "page_headers"): self.page_headers = []
        self.page_headers.append((title_label, hint))
        panel = QFrame(); panel.setObjectName("contentPanel"); panel_layout = QVBoxLayout(panel); panel_layout.setContentsMargins(18, 18, 18, 18); panel_layout.setSpacing(14)
        if expand:
            layout.addWidget(panel, 1)
        else:
            panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            layout.addWidget(panel, 0, Qt.AlignTop)
            layout.addStretch()
        return page, panel_layout

    @staticmethod
    def _configure_table(table):
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setWordWrap(False)
        table.setTextElideMode(Qt.ElideRight)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(38)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

    @staticmethod
    def _resize_table_columns(table, maximums=None):
        """Size columns from their visible content while capping long text columns."""
        maximums = maximums or {}
        metrics = QFontMetrics(table.font())
        for column in range(table.columnCount()):
            header = table.horizontalHeaderItem(column)
            width = metrics.horizontalAdvance(header.text() if header else "") + 34
            for row in range(table.rowCount()):
                item = table.item(row, column)
                if item:
                    width = max(width, metrics.horizontalAdvance(item.text()) + 34)
            table.setColumnWidth(column, min(max(width, 88), maximums.get(column, 240)))

    @staticmethod
    def _table_item(value):
        text = str(value)
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        item.setToolTip(text)
        return item

    def _dashboard_page(self):
        page, layout = self._page_shell("服务管理", "分别管理 FTP 与 SFTP 的监听状态、IP 地址和端口。", expand=False)
        cards = QHBoxLayout()
        self.ftp_status, self.ftp_endpoint, self.ftp_action = self._service_card(cards, "FTP")
        self.sftp_status, self.sftp_endpoint, self.sftp_action = self._service_card(cards, "SFTP")
        layout.addLayout(cards)
        self.online_status = QLabel(); self.online_status.setObjectName("metricCaption"); layout.addWidget(self.online_status)
        layout.addStretch()
        return page

    def _service_card(self, parent_layout, name):
        card = QFrame(); card.setObjectName("metricCard"); card.setFixedHeight(250); card_layout = QVBoxLayout(card); card_layout.setContentsMargins(22, 20, 22, 20); card_layout.setSpacing(8)
        title = QLabel(f"{name} 服务"); title.setObjectName("pageTitle"); setattr(self, f"{name.lower()}_title", title)
        status = QLabel(); status.setObjectName("metricValue")
        endpoint = QLabel(); endpoint.setObjectName("metricCaption")
        error = QLabel(); error.setObjectName("serviceError"); error.setWordWrap(True)
        auto_start = QCheckBox("启动程序时自动启动")
        auto_start.setObjectName("autoStartToggle")
        settings = self.db.settings(); auto_start.setChecked(settings.get(f"auto_start_{name.lower()}", "true") == "true")
        auto_start.toggled.connect(lambda checked: self.set_service_autostart(name, checked))
        action = QPushButton(); action.setObjectName("primaryButton"); action.clicked.connect(lambda: self.toggle_service(name))
        config = QPushButton("配置"); config.clicked.connect(lambda: self.configure_service(name))
        buttons = QHBoxLayout(); buttons.addWidget(action); buttons.addWidget(config)
        card_layout.addWidget(title); card_layout.addWidget(status); card_layout.addWidget(endpoint); card_layout.addWidget(auto_start); card_layout.addWidget(error); card_layout.addLayout(buttons)
        parent_layout.addWidget(card)
        setattr(self, f"{name.lower()}_error", error)
        setattr(self, f"{name.lower()}_autostart", auto_start); setattr(self, f"{name.lower()}_config", config)
        return status, endpoint, action

    def _users_page(self):
        page, layout = self._page_shell("用户与权限", "管理账户有效期、访问根目录和协议权限。")
        self.users_table = QTableWidget(0, 6)
        self.users_table.setHorizontalHeaderLabels(["服务用户名", "状态", "有效期", "协议范围", "授权根目录", "权限"])
        self._configure_table(self.users_table)
        layout.addWidget(self.users_table)
        buttons = QHBoxLayout()
        self.add_user_button = QPushButton("新增用户"); add = self.add_user_button; add.setObjectName("primaryButton"); add.clicked.connect(self.add_user)
        self.toggle_user_button = QPushButton("启用/禁用"); toggle = self.toggle_user_button; toggle.clicked.connect(self.toggle_user)
        self.permission_button = QPushButton("配置权限"); permission = self.permission_button; permission.clicked.connect(self.configure_permissions)
        self.change_user_password_button = QPushButton("修改密码"); change_password = self.change_user_password_button; change_password.clicked.connect(self.change_service_user_password)
        self.delete_user_button = QPushButton("删除用户"); delete = self.delete_user_button; delete.setObjectName("dangerButton"); delete.clicked.connect(self.delete_user)
        for button in (add, toggle, permission, change_password, delete): buttons.addWidget(button)
        buttons.addStretch(); layout.addLayout(buttons)
        self.refresh_users()
        return page

    def _sessions_page(self):
        page, layout = self._page_shell("实时连接", "查看当前协议会话，并即时断开异常连接。")
        self.sessions_table = QTableWidget(0, 5)
        self.sessions_table.setHorizontalHeaderLabels(["会话 ID", "用户", "协议", "客户端 IP", "登录时间"])
        self._configure_table(self.sessions_table)
        layout.addWidget(self.sessions_table)
        self.kick_button = QPushButton("剔除选中连接"); kick = self.kick_button; kick.clicked.connect(self.kick_session)
        layout.addWidget(kick, alignment=Qt.AlignLeft)
        return page

    def _logs_page(self):
        page, layout = self._page_shell("审计日志", "追踪认证、传输、归档和服务管理操作。")
        self.log_page = 1
        self.log_page_size = 20
        filters = QGridLayout(); filters.setHorizontalSpacing(10); filters.setVerticalSpacing(8)
        self.log_user_filter = QComboBox(); self.log_protocol_filter = QComboBox(); self.log_action_filter = QComboBox()
        self.log_ip_filter = QLineEdit()
        self.log_use_time = QCheckBox()
        self.log_start_filter = QDateTimeEdit(QDateTime.currentDateTime().addDays(-30)); self.log_start_filter.setCalendarPopup(True)
        self.log_end_filter = QDateTimeEdit(QDateTime.currentDateTime()); self.log_end_filter.setCalendarPopup(True)
        self.log_start_filter.setEnabled(False); self.log_end_filter.setEnabled(False)
        self.log_use_time.toggled.connect(self.log_start_filter.setEnabled); self.log_use_time.toggled.connect(self.log_end_filter.setEnabled)
        self.log_search_button = QPushButton(); self.log_search_button.setObjectName("primaryButton"); self.log_search_button.clicked.connect(self.search_logs)
        self.log_reset_button = QPushButton(); self.log_reset_button.clicked.connect(self.reset_log_filters)
        for column, widget in enumerate((self.log_user_filter, self.log_ip_filter, self.log_protocol_filter, self.log_action_filter)):
            filters.addWidget(widget, 0, column)
        filters.addWidget(self.log_use_time, 1, 0); filters.addWidget(self.log_start_filter, 1, 1); filters.addWidget(self.log_end_filter, 1, 2)
        action_row = QHBoxLayout(); action_row.addWidget(self.log_search_button); action_row.addWidget(self.log_reset_button); action_row.addStretch()
        filters.addLayout(action_row, 1, 3)
        layout.addLayout(filters)
        self.logs_table = QTableWidget(0, 7)
        self.logs_table.setHorizontalHeaderLabels(["时间", "用户", "协议", "IP", "操作", "路径", "结果"])
        self._configure_table(self.logs_table)
        layout.addWidget(self.logs_table)
        pagination = QHBoxLayout()
        self.log_page_size_label = QLabel(); self.log_page_size_combo = QComboBox(); self.log_page_size_combo.addItems(["20", "50", "100"]); self.log_page_size_combo.setCurrentText("20"); self.log_page_size_combo.currentTextChanged.connect(self.change_log_page_size)
        self.log_previous_button = QPushButton(); self.log_previous_button.clicked.connect(lambda: self.change_log_page(-1))
        self.log_page_label = QLabel(); self.log_page_label.setObjectName("metricCaption")
        self.log_next_button = QPushButton(); self.log_next_button.clicked.connect(lambda: self.change_log_page(1))
        pagination.addWidget(self.log_page_size_label); pagination.addWidget(self.log_page_size_combo); pagination.addStretch(); pagination.addWidget(self.log_previous_button); pagination.addWidget(self.log_page_label); pagination.addWidget(self.log_next_button)
        layout.addLayout(pagination)
        self.refresh_logs()
        return page

    def _blacklist_page(self):
        page, layout = self._page_shell("IP 黑名单", "拒绝指定 IP 地址或 CIDR 网段的访问请求。")
        self.rules_table = QTableWidget(0, 3)
        self.rules_table.setHorizontalHeaderLabels(["IP/CIDR", "原因", "创建时间"])
        self._configure_table(self.rules_table)
        layout.addWidget(self.rules_table)
        form = QHBoxLayout(); self.rule_network = QLineEdit(); self.rule_network.setPlaceholderText("例如 192.168.1.0/24")
        self.rule_reason = QLineEdit(); self.rule_reason.setPlaceholderText("原因")
        self.add_rule_button = QPushButton("添加黑名单"); add = self.add_rule_button; add.setObjectName("primaryButton"); add.clicked.connect(self.add_blacklist)
        form.addWidget(self.rule_network); form.addWidget(self.rule_reason); form.addWidget(add); layout.addLayout(form)
        self.refresh_rules(); return page

    def _system_account_page(self):
        page, panel_layout = self._page_shell("系统账户", "此账户仅用于登录 krFTP 管理程序，不具备 FTP/SFTP 文件服务权限。")
        form = QFormLayout(); form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.system_username = QLineEdit(self.login_user.username)
        self.system_user_row = QLabel(); self.system_new_password_row = QLabel(); self.system_confirm_password_row = QLabel()
        self.system_password = QLineEdit(); self.system_password.setEchoMode(QLineEdit.Password)
        self.system_password_confirm = QLineEdit(); self.system_password_confirm.setEchoMode(QLineEdit.Password)
        self.save_system_button = QPushButton("保存系统账户"); save = self.save_system_button; save.setObjectName("primaryButton"); save.clicked.connect(self.save_system_account)
        form.addRow(self.system_user_row, self.system_username); form.addRow(self.system_new_password_row, self.system_password); form.addRow(self.system_confirm_password_row, self.system_password_confirm); form.addRow("", save)
        panel_layout.addLayout(form); panel_layout.addStretch()
        return page

    def _about_page(self):
        page, panel_layout = self._page_shell("关于 krFTP", "版本、版权与开源使用声明。", expand=False)
        logo = QLabel(); logo.setPixmap(self.app_icon.pixmap(56, 56)); logo.setAlignment(Qt.AlignLeft)
        self.about_product = QLabel("krFTP Server Manager")
        product = self.about_product
        product.setObjectName("pageTitle")
        self.about_version = QLabel()
        version = self.about_version
        version.setObjectName("appSubtitle")
        self.about_copyright = QLabel()
        copyright_text = self.about_copyright
        copyright_text.setWordWrap(True)
        copyright_text.setStyleSheet("color: #425466; line-height: 1.6;")
        self.about_author_contact = QLabel()
        self.about_author_contact.setWordWrap(True)
        self.about_author_contact.setStyleSheet("color: #1f4f49; font-weight: 600; line-height: 1.6;")
        panel_layout.addWidget(logo); panel_layout.addWidget(product); panel_layout.addWidget(version); panel_layout.addSpacing(10); panel_layout.addWidget(copyright_text); panel_layout.addSpacing(8); panel_layout.addWidget(self.about_author_contact)
        return page

    def force_password_change(self):
        dialog = PasswordChangeDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.db.change_system_password(self.login_user.id, dialog.password.text())
            self.login_user.must_change_password = False
            self.start_if_configured()
        else:
            self.close()

    def start_if_configured(self):
        if self.db.settings().get("auto_start_services") == "true": self.start_services()

    def start_services(self):
        results = self.services.start_configured()
        for name, result in results.items(): self.db.audit(self.login_user.username, "LOCAL", "127.0.0.1", f"START_{name}", "", "SUCCESS" if result == "RUNNING" else "FAIL", result)
        self.refresh_live_data()

    def stop_services(self):
        self.services.stop_all(); self.db.audit(self.login_user.username, "LOCAL", "127.0.0.1", "STOP_SERVICES", "")
        self.refresh_live_data()

    def toggle_service(self, name):
        service = self.services.ftp if name == "FTP" else self.services.sftp
        if service.running:
            self.services.stop_service(name)
            self.db.audit(self.login_user.username, "LOCAL", "127.0.0.1", f"STOP_{name}", "")
        else:
            result = self.services.start_service(name)
            self.db.audit(self.login_user.username, "LOCAL", "127.0.0.1", f"START_{name}", "", "SUCCESS" if result == "RUNNING" else "FAIL", result)
            if result != "RUNNING":
                message = f"{name} 服务启动失败：{result}。请检查端口是否被占用，或通过“配置”修改端口。"
                getattr(self, f"{name.lower()}_error").setText(message)
                QMessageBox.warning(self, "服务启动失败", message)
            else:
                getattr(self, f"{name.lower()}_error").clear()
        self.refresh_live_data()

    def configure_service(self, name):
        dialog = ServiceConfigDialog(self.db, name, self.locale, self)
        dialog.save()
        self.refresh_live_data()

    def set_service_autostart(self, name, enabled):
        self.db.update_settings({f"auto_start_{name.lower()}": "true" if enabled else "false"})

    def refresh_live_data(self):
        self.services.enforce_access_rules()
        settings = self.db.settings()
        text = self._text()
        self.ftp_status.setText(text[27] if self.services.ftp.running else text[28])
        self.sftp_status.setText(text[27] if self.services.sftp.running else text[28])
        self.ftp_endpoint.setText(f"{text[29]}  {settings['bind_ip']} : {settings['ftp_port']}")
        self.sftp_endpoint.setText(f"{text[29]}  {settings['bind_ip']} : {settings['sftp_port']}")
        self.ftp_action.setText(text[24] if self.services.ftp.running else text[23])
        self.sftp_action.setText(text[24] if self.services.sftp.running else text[23])
        sessions = self.services.sessions.snapshot(); self.online_status.setText(f"{text[30]}: {len(sessions)}")
        self.sessions_table.setRowCount(len(sessions))
        for row, session in enumerate(sessions):
            for col, value in enumerate((session.session_id, session.username, session.protocol, session.client_ip, session.connected_at.strftime('%F %T'))):
                self.sessions_table.setItem(row, col, self._table_item(value))
        self._resize_table_columns(self.sessions_table, {0: 210, 1: 160, 2: 110, 3: 180, 4: 180})

    def refresh_users(self):
        self._service_users = self.db.users(); self.users_table.setRowCount(len(self._service_users))
        for row, user in enumerate(self._service_users):
            user_roots = self.db.user_roots(user.id)
            roots = ', '.join(root.root_path for root in user_roots)
            words = dialog_text(self.locale)
            protocol_names = {"BOTH": words["ftp_sftp"], "FTP": words["ftp_only"], "SFTP": words["sftp_only"]}
            protocols = ', '.join(sorted({protocol_names.get(root.protocol, root.protocol) for root in user_roots})) or self._extra()["not_configured"]
            permissions = set()
            for root in user_roots:
                try:
                    permissions.update(json.loads(root.permissions))
                except (TypeError, json.JSONDecodeError):
                    continue
            labels = PERMISSION_TEXT.get(self.locale, PERMISSION_TEXT["zh_CN"])
            permission_summary = ', '.join(labels[key] for key in sorted(permissions) if key in labels) or self._extra()["not_configured"]
            values = (user.username, self._extra()["enabled"] if user.is_active else self._extra()["disabled"], user.expires_at.strftime('%F %T') if user.expires_at else words["never"], protocols, roots or self._extra()["not_configured"], permission_summary)
            for col, value in enumerate(values):
                self.users_table.setItem(row, col, self._table_item(value))
        self._resize_table_columns(self.users_table, {0: 180, 1: 140, 2: 185, 3: 180, 4: 320, 5: 330})

    def selected_user(self):
        row = self.users_table.currentRow()
        return self._service_users[row] if row >= 0 and row < len(self._service_users) else None

    def add_user(self):
        dialog = UserDialog(self.locale, self)
        if dialog.exec() == QDialog.Accepted:
            username, password, expiry = dialog.values()
            try:
                if len(password) < 8: raise ValueError("密码至少 8 个字符")
                self.db.create_user(username, password, expiry); self.refresh_users()
            except Exception as exc: QMessageBox.warning(self, "无法创建", str(exc))

    def toggle_user(self):
        user = self.selected_user()
        if user: self.db.set_user_active(user.id, not user.is_active); self.refresh_users()

    def configure_permissions(self):
        user = self.selected_user()
        if not user:
            labels = PERMISSION_DIALOG_TEXT.get(self.locale, PERMISSION_DIALOG_TEXT["zh_CN"])
            QMessageBox.information(self, "krFTP", labels[4])
            return
        if RootPermissionDialog(self.db, user, self.locale, self).save():
            self.refresh_users()
            labels = PERMISSION_DIALOG_TEXT.get(self.locale, PERMISSION_DIALOG_TEXT["zh_CN"])
            QMessageBox.information(self, "krFTP", labels[5])

    def change_service_user_password(self):
        user = self.selected_user()
        if not user:
            labels = PERMISSION_DIALOG_TEXT.get(self.locale, PERMISSION_DIALOG_TEXT["zh_CN"])
            QMessageBox.information(self, "krFTP", labels[4])
            return
        dialog = ServiceUserPasswordDialog(user.username, self.locale, self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self.db.change_service_user_password(user.id, dialog.password.text())
                text = USER_PASSWORD_TEXT.get(self.locale, USER_PASSWORD_TEXT["zh_CN"])
                QMessageBox.information(self, "krFTP", text[8])
            except Exception as exc:
                QMessageBox.warning(self, "krFTP", str(exc))

    def delete_user(self):
        user = self.selected_user()
        if not user:
            QMessageBox.information(self, "请选择用户", "请先选中要删除的服务用户。")
            return
        answer = QMessageBox.question(self, "删除服务用户", f"确定删除服务用户“{user.username}”及其全部授权吗？此操作不可恢复。")
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.services.disconnect_user(user.username)
        self.db.delete_user(user.id)
        self.db.audit(self.login_user.username, "LOCAL", "127.0.0.1", "DELETE_SERVICE_USER", user.username)
        self.refresh_users()
        self.refresh_live_data()

    def kick_session(self):
        row = self.sessions_table.currentRow()
        if row >= 0:
            session_id = self.sessions_table.item(row, 0).text()
            if self.services.disconnect(session_id):
                self.db.audit(self.login_user.username, "LOCAL", "127.0.0.1", "KICK_SESSION", session_id)
                self.refresh_live_data()

    def _retranslate_log_filters(self):
        labels = LOG_FILTER_TEXT.get(self.locale, LOG_FILTER_TEXT["zh_CN"])
        previous_user = self.log_user_filter.currentData()
        previous_protocol = self.log_protocol_filter.currentData()
        previous_action = self.log_action_filter.currentData()
        usernames, protocols, actions = self.db.audit_filter_values()
        self.log_user_filter.blockSignals(True); self.log_user_filter.clear(); self.log_user_filter.addItem(labels[0], "")
        for username in usernames: self.log_user_filter.addItem(username, username)
        self.log_protocol_filter.blockSignals(True); self.log_protocol_filter.clear(); self.log_protocol_filter.addItem(labels[1], "")
        for protocol in protocols: self.log_protocol_filter.addItem(protocol, protocol)
        self.log_action_filter.blockSignals(True); self.log_action_filter.clear(); self.log_action_filter.addItem(labels[2], "")
        action_labels = ACTION_LABELS_BY_LOCALE.get(self.locale, ACTION_LABELS)
        for action in actions: self.log_action_filter.addItem(action_labels.get(action, action), action)
        for combo, selected in ((self.log_user_filter, previous_user), (self.log_protocol_filter, previous_protocol), (self.log_action_filter, previous_action)):
            combo.setCurrentIndex(max(0, combo.findData(selected)))
            combo.blockSignals(False)
        self.log_ip_filter.setPlaceholderText(labels[3]); self.log_use_time.setText(labels[4])
        self.log_start_filter.setToolTip(labels[5]); self.log_end_filter.setToolTip(labels[6])
        self.log_search_button.setText(labels[7]); self.log_reset_button.setText(labels[8])
        self.log_page_size_label.setText(labels[9]); self.log_previous_button.setText(labels[10]); self.log_next_button.setText(labels[11])

    def search_logs(self):
        self.log_page = 1
        self.refresh_logs()

    def reset_log_filters(self):
        self.log_user_filter.setCurrentIndex(0); self.log_ip_filter.clear(); self.log_protocol_filter.setCurrentIndex(0); self.log_action_filter.setCurrentIndex(0)
        self.log_use_time.setChecked(False); self.log_page = 1
        self.refresh_logs()

    def change_log_page_size(self, value):
        self.log_page_size = int(value); self.log_page = 1
        self.refresh_logs()

    def change_log_page(self, delta):
        target = self.log_page + delta
        if target >= 1 and target <= getattr(self, "log_pages", 1):
            self.log_page = target
            self.refresh_logs()

    def refresh_logs(self):
        start_at = self.log_start_filter.dateTime().toPython() if self.log_use_time.isChecked() else None
        end_at = self.log_end_filter.dateTime().toPython() if self.log_use_time.isChecked() else None
        logs, total = self.db.audit_logs(
            username=self.log_user_filter.currentData() or "", client_ip=self.log_ip_filter.text().strip(),
            protocol=self.log_protocol_filter.currentData() or "", action=self.log_action_filter.currentData() or "",
            start_at=start_at, end_at=end_at, page=self.log_page, page_size=self.log_page_size,
        )
        self.log_pages = max(1, (total + self.log_page_size - 1) // self.log_page_size)
        if self.log_page > self.log_pages:
            self.log_page = self.log_pages
            return self.refresh_logs()
        labels = LOG_FILTER_TEXT.get(self.locale, LOG_FILTER_TEXT["zh_CN"])
        self.log_page_label.setText(labels[12].format(page=self.log_page, pages=self.log_pages, total=total))
        self.log_previous_button.setEnabled(self.log_page > 1); self.log_next_button.setEnabled(self.log_page < self.log_pages)
        self.logs_table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            action = ACTION_LABELS_BY_LOCALE.get(self.locale, ACTION_LABELS).get(log.action, log.action)
            extra = self._extra()
            result = extra["success"] if log.result == "SUCCESS" else extra["failed"] if log.result == "FAIL" else log.result
            values = (log.occurred_at.strftime('%F %T'), log.username, log.protocol, log.client_ip, action, log.path, result)
            for col, value in enumerate(values):
                self.logs_table.setItem(row, col, self._table_item(value))
        self._resize_table_columns(self.logs_table, {0: 180, 1: 150, 2: 105, 3: 170, 4: 220, 5: 380, 6: 120})

    def refresh_rules(self):
        rules = self.db.ip_rules(); self.rules_table.setRowCount(len(rules))
        for row, rule in enumerate(rules):
            for col, value in enumerate((rule.network, rule.reason, rule.created_at.strftime('%F %T'))):
                self.rules_table.setItem(row, col, self._table_item(value))
        self._resize_table_columns(self.rules_table, {0: 230, 1: 420, 2: 190})

    def add_blacklist(self):
        try:
            self.db.add_ip_rule(self.rule_network.text().strip(), self.rule_reason.text().strip()); self.services.enforce_access_rules(); self.rule_network.clear(); self.rule_reason.clear(); self.refresh_rules()
        except ValueError as exc: QMessageBox.warning(self, "无效 IP", str(exc))

    def save_system_account(self):
        password = self.system_password.text()
        if password != self.system_password_confirm.text():
            QMessageBox.warning(self, "无法保存", "两次输入的新密码不一致。")
            return
        try:
            self.login_user = self.db.update_system_account(self.login_user.id, self.system_username.text(), password or None)
            self.user_label.setText(f"当前管理员  {self.login_user.username}")
            self.system_password.clear(); self.system_password_confirm.clear()
            QMessageBox.information(self, "已保存", "系统账户已更新。")
        except Exception as exc:
            QMessageBox.warning(self, "无法保存", str(exc))

    def _create_tray(self):
        if hasattr(self, "tray"):
            self.tray.show()
            return
        self.tray = QSystemTrayIcon(self.app_icon, self)
        self.tray_menu = QMenu(self)
        self.tray_show_action = QAction(self); self.tray_show_action.triggered.connect(self.restore_window)
        self.tray_start_action = QAction(self); self.tray_start_action.triggered.connect(self.start_services)
        self.tray_stop_action = QAction(self); self.tray_stop_action.triggered.connect(self.stop_services)
        self.tray_quit_action = QAction(self); self.tray_quit_action.triggered.connect(self.quit_application)
        self.tray_menu.addAction(self.tray_show_action); self.tray_menu.addSeparator(); self.tray_menu.addAction(self.tray_start_action); self.tray_menu.addAction(self.tray_stop_action); self.tray_menu.addSeparator(); self.tray_menu.addAction(self.tray_quit_action)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(self._handle_tray_activation)
        self._retranslate_tray()
        self.tray.show()
        self.tray_available = QSystemTrayIcon.isSystemTrayAvailable()
        if not self.tray_available:
            QTimer.singleShot(1200, self._retry_tray_registration)

    def _retry_tray_registration(self):
        """Retry once after Explorer finishes restoring its notification area."""
        if not hasattr(self, "tray"):
            return
        self.tray_available = QSystemTrayIcon.isSystemTrayAvailable()
        self.tray.show()

    def _handle_tray_activation(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.restore_window()

    def _retranslate_tray(self):
        if not hasattr(self, "tray"):
            return
        text = TRAY_TEXT.get(self.locale, TRAY_TEXT["zh_CN"])
        self.tray_show_action.setText(text[0]); self.tray_start_action.setText(text[1]); self.tray_stop_action.setText(text[2]); self.tray_quit_action.setText(text[3])
        self.tray_tooltip_message = text[4]

    def restore_window(self):
        self.showNormal(); self.raise_(); self.activateWindow()

    def sign_out(self):
        """End the console session while keeping the managed services alive."""
        from ui.login_dialog import LoginDialog

        self.hide()
        login = LoginDialog(self.db, self.languages, self)
        login.setWindowIcon(self.app_icon)
        if login.exec() == QDialog.Accepted:
            self.login_user = login.user
            self.locale = self.db.settings().get("language", "zh_CN")
            self.retranslate_ui()
        self.restore_window()

    def quit_application(self):
        if hasattr(self, "tray"):
            self.tray.hide()
        self.services.stop_all(); self._quit_requested = True; self.close()

    def closeEvent(self, event):
        if getattr(self, "_quit_requested", False):
            self.services.stop_all(); event.accept()
        elif not hasattr(self, "tray") or not self.tray_available or not self.tray.isVisible():
            self.showNormal(); event.ignore()
        else:
            self.hide(); self.tray.showMessage("krFTP", self.tray_tooltip_message, QSystemTrayIcon.Information, 2500); event.ignore()
