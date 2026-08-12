from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import ICON_PATH

LOGIN_TEXT = {
    "zh_CN": ["登录 krFTP", "FTP / SFTP 服务控制台", "安全管理 · 集中审计 · 实时连接", "管理员访问", "登录管理控制台", "请输入账号和密码以继续。", "账号", "输入账号", "密码", "输入密码", "界面语言", "登录", "首次使用：账号 admin，密码 admin123。登录后需要立即修改管理员密码。", "账号或密码无效，账号可能已禁用或过期。"],
    "en_US": ["Sign in to krFTP", "FTP / SFTP Service Console", "Secure management · Central audit · Live sessions", "ADMINISTRATOR ACCESS", "Sign in to the console", "Enter your credentials to continue.", "Username", "Enter username", "Password", "Enter password", "Language", "Sign in", "First use: username admin, password admin123. You must change the administrator password after signing in.", "The username or password is invalid, disabled, or expired."],
    "zh_TW": ["登入 krFTP", "FTP / SFTP 服務控制台", "安全管理 · 集中稽核 · 即時連線", "管理員存取", "登入管理控制台", "請輸入帳號與密碼以繼續。", "帳號", "輸入帳號", "密碼", "輸入密碼", "介面語言", "登入", "首次使用：帳號 admin，密碼 admin123。登入後必須立即修改管理員密碼。", "帳號或密碼無效，帳號可能已停用或過期。"],
    "ja_JP": ["krFTP にログイン", "FTP / SFTP サービスコンソール", "安全管理 · 監査 · 接続監視", "管理者アクセス", "管理コンソールにログイン", "続行するには認証情報を入力してください。", "ユーザー名", "ユーザー名を入力", "パスワード", "パスワードを入力", "言語", "ログイン", "初回使用: ユーザー名 admin、パスワード admin123。ログイン後に管理者パスワードを変更してください。", "ユーザー名またはパスワードが無効、無効化、または期限切れです。"],
    "ko_KR": ["krFTP 로그인", "FTP / SFTP 서비스 콘솔", "보안 관리 · 중앙 감사 · 실시간 연결", "관리자 액세스", "관리 콘솔 로그인", "계속하려면 자격 증명을 입력하세요.", "사용자 이름", "사용자 이름 입력", "비밀번호", "비밀번호 입력", "언어", "로그인", "처음 사용: 사용자 이름 admin, 비밀번호 admin123. 로그인 후 관리자 비밀번호를 변경해야 합니다.", "사용자 이름 또는 비밀번호가 잘못되었거나 비활성화 또는 만료되었습니다."],
    "es_ES": ["Iniciar sesión en krFTP", "Consola de servicios FTP / SFTP", "Gestión segura · Auditoría central · Sesiones en vivo", "ACCESO DE ADMINISTRADOR", "Iniciar sesión en la consola", "Introduzca sus credenciales para continuar.", "Usuario", "Introduzca el usuario", "Contraseña", "Introduzca la contraseña", "Idioma", "Iniciar sesión", "Primer uso: usuario admin, contraseña admin123. Debe cambiar la contraseña de administrador después de iniciar sesión.", "El usuario o la contraseña no son válidos, están deshabilitados o han caducado."],
    "fr_FR": ["Connexion à krFTP", "Console de services FTP / SFTP", "Gestion sécurisée · Audit central · Sessions en direct", "ACCÈS ADMINISTRATEUR", "Connexion à la console", "Saisissez vos identifiants pour continuer.", "Nom d'utilisateur", "Saisissez le nom d'utilisateur", "Mot de passe", "Saisissez le mot de passe", "Langue", "Connexion", "Première utilisation : identifiant admin, mot de passe admin123. Modifiez le mot de passe administrateur après connexion.", "Le nom d'utilisateur ou le mot de passe est invalide, désactivé ou expiré."],
    "de_DE": ["Bei krFTP anmelden", "FTP / SFTP Dienstkonsole", "Sichere Verwaltung · Zentrale Prüfung · Live-Sitzungen", "ADMINISTRATORZUGRIFF", "An der Verwaltungskonsole anmelden", "Geben Sie Ihre Zugangsdaten ein.", "Benutzername", "Benutzernamen eingeben", "Passwort", "Passwort eingeben", "Sprache", "Anmelden", "Erste Nutzung: Benutzer admin, Passwort admin123. Ändern Sie danach das Administratorpasswort.", "Benutzername oder Passwort ist ungültig, deaktiviert oder abgelaufen."],
    "pt_BR": ["Entrar no krFTP", "Console de serviços FTP / SFTP", "Gerenciamento seguro · Auditoria central · Sessões ao vivo", "ACESSO DE ADMINISTRADOR", "Entrar no console", "Informe suas credenciais para continuar.", "Usuário", "Digite o usuário", "Senha", "Digite a senha", "Idioma", "Entrar", "Primeiro uso: usuário admin, senha admin123. Altere a senha de administrador após entrar.", "O usuário ou a senha são inválidos, desativados ou expiraram."],
    "ru_RU": ["Вход в krFTP", "Консоль служб FTP / SFTP", "Безопасное управление · Централизованный аудит · Сеансы", "ДОСТУП АДМИНИСТРАТОРА", "Вход в консоль управления", "Введите учетные данные для продолжения.", "Имя пользователя", "Введите имя пользователя", "Пароль", "Введите пароль", "Язык", "Войти", "Первый запуск: имя admin, пароль admin123. После входа измените пароль администратора.", "Имя пользователя или пароль недействительны, отключены или истекли."],
}


class InitialPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置管理员密码")
        self.setModal(True)
        self.setFixedWidth(390)
        layout = QVBoxLayout(self)
        title = QLabel("首次登录，请设置新的管理员密码")
        title.setObjectName("formTitle")
        layout.addWidget(title)
        self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.Password); self.password.setPlaceholderText("至少 8 个字符")
        self.confirm = QLineEdit(); self.confirm.setEchoMode(QLineEdit.Password); self.confirm.setPlaceholderText("再次输入新密码")
        layout.addWidget(QLabel("新密码")); layout.addWidget(self.password)
        layout.addWidget(QLabel("确认密码")); layout.addWidget(self.confirm)
        self.status = QLabel(); self.status.setObjectName("status"); layout.addWidget(self.status)
        submit = QPushButton("保存并继续"); submit.setObjectName("loginButton"); submit.clicked.connect(self.validate); layout.addWidget(submit)

    def validate(self):
        if len(self.password.text()) < 8:
            self.status.setText("密码至少需要 8 个字符。")
        elif self.password.text() != self.confirm.text():
            self.status.setText("两次输入的密码不一致。")
        else:
            self.accept()


class LoginDialog(QDialog):
    def __init__(self, db, languages, parent=None):
        super().__init__(parent)
        self.db, self.languages = db, languages
        self.user = None
        self.setWindowTitle("登录 krFTP")
        self.setModal(True)
        self.setFixedSize(880, 640)
        self.setStyleSheet("""
            QDialog { background: #ffffff; font-family: 'Microsoft YaHei UI', 'Segoe UI'; }
            QFrame#brandPanel { background: #1e293b; }
            QLabel#brandName { color: #ffffff; font-size: 30px; font-weight: 700; }
            QLabel#brandCaption { color: #bfdbfe; font-size: 14px; }
            QLabel#brandFooter { color: #94a3b8; font-size: 12px; }
            QLabel#formEyebrow { color: #2563eb; font-size: 12px; font-weight: 700; }
            QLabel#formTitle { color: #17212b; font-size: 25px; font-weight: 700; }
            QLabel#formHint { color: #64748b; font-size: 13px; }
            QLabel#fieldLabel { color: #334155; font-size: 12px; font-weight: 700; }
            QLineEdit { background: #ffffff; border: 1px solid #c7d1d5; border-radius: 8px; min-height: 43px; padding: 0 12px; color: #17212b; font-size: 14px; }
            QLineEdit:focus { border: 2px solid #2563eb; }
            QComboBox { background: #ffffff; color: #17212b; border: 1px solid #c7d1d5; border-radius: 8px; min-height: 43px; padding: 0 42px 0 12px; font-size: 14px; }
            QComboBox:hover { border-color: #60a5fa; background: #f8faff; }
            QComboBox:focus, QComboBox:on { border: 2px solid #2563eb; }
            QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 38px; border: none; border-left: 1px solid #dce3e6; border-top-right-radius: 8px; border-bottom-right-radius: 8px; }
            QComboBox QAbstractItemView { background: #ffffff; color: #17212b; border: 1px solid #bfdbfe; border-radius: 8px; outline: none; padding: 5px; selection-background-color: #dbeafe; selection-color: #1e3a8a; }
            QComboBox QAbstractItemView::item { min-height: 32px; padding: 0 10px; border-radius: 5px; }
            QComboBox QAbstractItemView::item:hover { background: #eff6ff; }
            QPushButton#loginButton { background: #2563eb; color: #ffffff; border: none; border-radius: 8px; min-height: 44px; font-size: 14px; font-weight: 700; }
            QPushButton#loginButton:hover { background: #1d4ed8; }
            QLabel#status { color: #b42318; font-size: 12px; min-height: 22px; }
            QLabel#accountHint { color: #7a5b1d; background: #fff8e8; border: 1px solid #f1d99a; border-radius: 8px; padding: 10px 12px; }
        """)
        self._build_ui()
        self.center_on_screen()

    def center_on_screen(self):
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen:
            self.move(screen.availableGeometry().center() - self.rect().center())

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        brand = QFrame()
        brand.setObjectName("brandPanel")
        brand.setFixedWidth(365)
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(42, 46, 42, 38)
        brand_layout.setSpacing(12)
        logo = QLabel()
        logo.setPixmap(QIcon(str(ICON_PATH)).pixmap(76, 76))
        logo.setFixedSize(82, 82)
        logo.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(logo)
        brand_layout.addSpacing(14)
        self.brand_name = QLabel("krFTP")
        name = self.brand_name
        name.setObjectName("brandName")
        brand_layout.addWidget(name)
        self.brand_caption = QLabel()
        caption = self.brand_caption
        caption.setObjectName("brandCaption")
        brand_layout.addWidget(caption)
        brand_layout.addStretch()
        self.brand_footer = QLabel()
        footer = self.brand_footer
        footer.setObjectName("brandFooter")
        brand_layout.addWidget(footer)
        root.addWidget(brand)

        form_host = QWidget()
        form_layout = QVBoxLayout(form_host)
        form_layout.setContentsMargins(62, 50, 62, 42)
        form_layout.setSpacing(10)
        self.eyebrow = QLabel()
        eyebrow = self.eyebrow
        eyebrow.setObjectName("formEyebrow")
        self.form_title = QLabel()
        title = self.form_title
        title.setObjectName("formTitle")
        self.form_hint = QLabel()
        hint = self.form_hint
        hint.setObjectName("formHint")
        form_layout.addWidget(eyebrow)
        form_layout.addWidget(title)
        form_layout.addWidget(hint)
        form_layout.addSpacing(18)
        self.account_label = QLabel()
        account_label = self.account_label
        account_label.setObjectName("fieldLabel")
        self.username = QLineEdit("admin")
        password_label = QLabel()
        self.password_label = password_label
        password_label.setObjectName("fieldLabel")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.login)
        form_layout.addWidget(account_label)
        form_layout.addWidget(self.username)
        form_layout.addSpacing(8)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password)
        form_layout.addSpacing(8)
        self.language_label = QLabel()
        language_label = self.language_label
        language_label.setObjectName("fieldLabel")
        self.language = QComboBox()
        self.language.setMinimumHeight(45)
        self.language.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        for locale in self.languages.available_locales():
            self.language.addItem(self.languages.display_name(locale), locale)
        locale = self.db.settings().get("language", "zh_CN")
        self.language.setCurrentIndex(max(0, self.language.findData(locale)))
        self.language.currentIndexChanged.connect(self.switch_language)
        form_layout.addWidget(language_label)
        form_layout.addWidget(self.language)
        self.status = QLabel()
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        form_layout.addWidget(self.status)
        self.login_button = QPushButton()
        button = self.login_button
        button.setObjectName("loginButton")
        button.clicked.connect(self.login)
        form_layout.addWidget(button)
        form_layout.addSpacing(16)
        self.account_hint = QLabel()
        account_hint = self.account_hint
        account_hint.setObjectName("accountHint")
        account_hint.setWordWrap(True)
        account_hint.setMinimumHeight(58)
        form_layout.addWidget(account_hint)
        form_layout.addStretch()
        root.addWidget(form_host, 1)
        self.retranslate(self.language.currentData())

    def switch_language(self, _index):
        locale = self.language.currentData()
        self.languages.apply(locale)
        self.db.update_settings({"language": locale})
        self.retranslate(locale)

    def retranslate(self, locale):
        text = LOGIN_TEXT.get(locale, LOGIN_TEXT["zh_CN"])
        self.setWindowTitle(text[0])
        self.brand_caption.setText(text[1]); self.brand_footer.setText(text[2])
        self.eyebrow.setText(text[3]); self.form_title.setText(text[4]); self.form_hint.setText(text[5])
        self.account_label.setText(text[6]); self.username.setPlaceholderText(text[7])
        self.password_label.setText(text[8]); self.password.setPlaceholderText(text[9])
        self.language_label.setText(text[10]); self.login_button.setText(text[11]); self.account_hint.setText(text[12])
        if self.status.text():
            self.status.setText(text[13])

    def login(self):
        username = self.username.text().strip()
        user = self.db.authenticate_admin(username, self.password.text())
        if not user:
            self.status.setText(LOGIN_TEXT.get(self.language.currentData(), LOGIN_TEXT["zh_CN"])[13])
            self.password.setFocus()
            self.password.selectAll()
            return
        self.status.clear()
        if user.must_change_password:
            password_dialog = InitialPasswordDialog(self)
            if password_dialog.exec() != QDialog.Accepted:
                return
            self.db.change_system_password(user.id, password_dialog.password.text())
            user = self.db.authenticate_admin(username, password_dialog.password.text())
        self.user = user
        self.accept()
