"""A small login/signup dialog shown before the floating companion
appears, sharing the same account store as the browser hood UI (so
logging in on one remembers you on the other)."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from engine import auth


class LoginTab(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self._on_success = on_success

        layout = QVBoxLayout(self)
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self._submit)

        submit = QPushButton("Log in")
        submit.clicked.connect(self._submit)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff6b6b;")
        self.error_label.setWordWrap(True)

        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(submit)
        layout.addWidget(self.error_label)

    def _submit(self):
        try:
            session = auth.login(self.email.text().strip(), self.password.text())
            self._on_success(session)
        except auth.AuthError as exc:
            self.error_label.setText(str(exc))


class SignupTab(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self._on_success = on_success

        layout = QVBoxLayout(self)
        self.name = QLineEdit()
        self.name.setPlaceholderText("Your name")
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password (min 6 characters)")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self._submit)

        submit = QPushButton("Sign up")
        submit.clicked.connect(self._submit)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff6b6b;")
        self.error_label.setWordWrap(True)

        layout.addWidget(self.name)
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(submit)
        layout.addWidget(self.error_label)

    def _submit(self):
        try:
            session = auth.signup(
                self.name.text().strip(), self.email.text().strip(), self.password.text()
            )
            self._on_success(session)
        except auth.AuthError as exc:
            self.error_label.setText(str(exc))


class AuthDialog(QDialog):
    def __init__(self):
        super().__init__(None, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Jarvis - Sign in")
        self.setFixedSize(320, 280)
        self.session = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h3>Welcome to Jarvis</h3>"))

        tabs = QTabWidget()
        tabs.addTab(LoginTab(self._on_success), "Log in")
        tabs.addTab(SignupTab(self._on_success), "Sign up")
        layout.addWidget(tabs)

    def _on_success(self, session):
        self.session = session
        self.accept()


def ensure_logged_in():
    """Return a session dict {name, email}, using a remembered session if
    one exists, otherwise blocking on a login/signup dialog. Returns None
    if the user closes the dialog without signing in."""
    remembered = auth.get_remembered_session()
    if remembered:
        return remembered

    dialog = AuthDialog()
    if dialog.exec_() == QDialog.Accepted:
        return dialog.session
    return None
