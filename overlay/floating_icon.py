"""The floating, cursor-hugging companion.

A small always-on-top, click-through-free glowing dot that hovers near the
mouse cursor. Click it to open a chat panel that can answer questions
by voice or text, aware of whatever window you currently have focused --
so you never have to alt-tab, screenshot, or copy-paste context in.
"""

import math

from PyQt5.QtCore import QPoint, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QCursor, QIcon, QPainter, QPixmap, QRadialGradient
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from engine.active_window import get_active_window_title
from engine.speech import listen, speak
from engine.tutor import get_response

ICON_SIZE = 46
CURSOR_OFFSET = QPoint(18, 18)


class ListenWorker(QThread):
    """Runs blocking microphone capture off the UI thread."""

    status = pyqtSignal(str)
    finished_with_text = pyqtSignal(str)

    def run(self):
        text = listen(on_status=self.status.emit)
        self.finished_with_text.emit(text)


class ChatPanel(QWidget):
    """The small conversation window that opens when the icon is clicked."""

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setWindowTitle("Jarvis")
        self.resize(340, 380)
        self.speak_replies = True
        self._listen_worker = None

        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("<b>Jarvis</b> - digital tutor")
        header.addWidget(title)
        header.addStretch()
        close_btn = QPushButton("x")
        close_btn.setFixedWidth(24)
        close_btn.clicked.connect(self.hide)
        header.addWidget(close_btn)
        layout.addLayout(header)

        self.context_label = QLabel("")
        self.context_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.context_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #4aa3ff; font-size: 11px;")
        layout.addWidget(self.status_label)

        input_row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ask about what's on your screen...")
        self.input_box.returnPressed.connect(self._on_send_clicked)
        input_row.addWidget(self.input_box)

        mic_btn = QPushButton("Mic")
        mic_btn.clicked.connect(self._on_mic_clicked)
        input_row.addWidget(mic_btn)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._on_send_clicked)
        input_row.addWidget(send_btn)

        layout.addLayout(input_row)

        self._append("Jarvis", "Hi! Click Mic or type a question about your screen.")

    def showEvent(self, event):
        super().showEvent(event)
        title = get_active_window_title()
        self.context_label.setText(f"Watching: {title}" if title else "")

    def _append(self, who, text):
        self.log.append(f"<b>{who}:</b> {text}")

    def _on_send_clicked(self):
        text = self.input_box.text().strip()
        if not text:
            return
        self.input_box.clear()
        self._handle_query(text)

    def _handle_query(self, text):
        self._append("You", text)
        window_title = get_active_window_title()
        self.context_label.setText(f"Watching: {window_title}" if window_title else "")
        reply = get_response(text, window_title)
        self._append("Jarvis", reply)
        if self.speak_replies:
            speak(reply)

    def _on_mic_clicked(self):
        if self._listen_worker and self._listen_worker.isRunning():
            return
        self._listen_worker = ListenWorker()
        self._listen_worker.status.connect(self.status_label.setText)
        self._listen_worker.finished_with_text.connect(self._on_voice_result)
        self._listen_worker.start()

    def _on_voice_result(self, text):
        self.status_label.setText("")
        if text:
            self._handle_query(text)


class FloatingIcon(QWidget):
    """The glowing dot that lives next to the mouse cursor."""

    def __init__(self):
        super().__init__(
            None,
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool,
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(ICON_SIZE, ICON_SIZE)

        self.follow_cursor = True
        self._drag_offset = None
        self._phase = 0.0

        self.chat_panel = ChatPanel()

        self._move_timer = QTimer(self)
        self._move_timer.timeout.connect(self._follow_cursor_tick)
        self._move_timer.start(16)

        self._glow_timer = QTimer(self)
        self._glow_timer.timeout.connect(self._advance_glow)
        self._glow_timer.start(33)

        self.show()

    def _follow_cursor_tick(self):
        if not self.follow_cursor:
            return
        self.move(QCursor.pos() + CURSOR_OFFSET)

    def _advance_glow(self):
        self._phase = (self._phase + 0.08) % (2 * math.pi)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pulse = 0.65 + 0.35 * math.sin(self._phase)
        center = QPoint(ICON_SIZE // 2, ICON_SIZE // 2)
        radius = ICON_SIZE / 2 - 2

        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0.0, QColor(90, 160, 255, int(230 * pulse)))
        gradient.setColorAt(0.6, QColor(40, 90, 220, int(160 * pulse)))
        gradient.setColorAt(1.0, QColor(20, 30, 80, 0))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPos() - self.pos()
        elif event.button() == Qt.RightButton:
            self.follow_cursor = not self.follow_cursor

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and not self.follow_cursor:
            self.move(event.globalPos() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None

    def mouseDoubleClickEvent(self, event):
        self.toggle_chat()

    def toggle_chat(self):
        if self.chat_panel.isVisible():
            self.chat_panel.hide()
            return
        anchor = self.pos()
        self.chat_panel.move(anchor.x() + ICON_SIZE, anchor.y())
        self.chat_panel.show()
        self.chat_panel.raise_()
        self.chat_panel.activateWindow()


def _make_tray_pixmap():
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(60, 130, 255))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 28, 28)
    painter.end()
    return pixmap


def build_tray_icon(app, icon_widget):
    tray = QSystemTrayIcon(QIcon(_make_tray_pixmap()), app)
    tray.setToolTip("Jarvis")

    menu = QMenu()

    toggle_chat_action = menu.addAction("Open / Close chat")
    toggle_chat_action.triggered.connect(icon_widget.toggle_chat)

    def _toggle_follow():
        icon_widget.follow_cursor = not icon_widget.follow_cursor

    toggle_follow_action = menu.addAction("Toggle follow cursor")
    toggle_follow_action.triggered.connect(_toggle_follow)

    def _toggle_speak():
        icon_widget.chat_panel.speak_replies = not icon_widget.chat_panel.speak_replies

    toggle_speak_action = menu.addAction("Toggle spoken replies")
    toggle_speak_action.triggered.connect(_toggle_speak)

    menu.addSeparator()
    quit_action = menu.addAction("Quit Jarvis")
    quit_action.triggered.connect(app.quit)

    tray.setContextMenu(menu)
    tray.activated.connect(
        lambda reason: icon_widget.toggle_chat() if reason == QSystemTrayIcon.Trigger else None
    )
    tray.show()
    return tray


def run():
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)

    icon_widget = FloatingIcon()
    tray = build_tray_icon(app, icon_widget)  # noqa: F841 -- keep tray alive

    app.exec_()
