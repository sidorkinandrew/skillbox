# todo https
# todo encryption
# pyuic5 messenger.ui -o clientui.py
import time
from datetime import datetime

import requests
from PyQt5 import QtWidgets, QtCore, QtGui
import clientui
from threading import Timer


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='./' + __name__ + '-debug.log')
#                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
debug_file = logging.FileHandler('./' + __name__ + '-info.log')
debug_file.setFormatter(formatter)
debug_file.setLevel(logging.INFO)
logging.getLogger('').addHandler(debug_file)


class MessengerApp(QtWidgets.QMainWindow, clientui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.last_time = 0
        self.pushButton.pressed.connect(self.button_clicked)
        self.textEdit.installEventFilter(self)
        self.plainTextEdit.setFocus()
        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.textBrowser.repaint)
        # self.timer.start()
        self.logger = logging.getLogger("messenger")
        self.refresh_timer = RepeatTimer(1, self.update_messages)
        self.refresh_timer.start()
        self.textBrowser.setReadOnly(True)
        # self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollbar = self.textBrowser.verticalScrollBar()

    def eventFilter(self, widget, event):
        if (event.type() == QtCore.QEvent.KeyPress and widget is self.textEdit):
            key = event.key()
            if key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                event.ignore()
                self.button_clicked()
                self.textEdit.clear()
                return True
        return super(MessengerApp, self).eventFilter(widget, event)

    def log_info(self, alist, symbol='; '):
        aline = symbol.join(map(str, alist))
        print(aline)
        self.logger.info(aline)

    def log_debug(self, alist, symbol='; '):
        aline = symbol.join(map(str, alist))
        print(aline)
        self.logger.debug(aline)

    def send_message(self, username, password, text):
        response = requests.post(
            "http://127.0.0.1:5000/auth",
            json={"username": username, "password": password}
        )
        if not response.json()['ok']:
            self.add_to_chat('Сообщение не отправлено - authentification issue')
            return False

        response = requests.post(
            "http://127.0.0.1:5000/send",
            json={"username": username, "password": password, "text": text}
        )
        if not response.json()['ok']:
            self.add_to_chat('Сообщение не отправлено - send error')
            return False

    def update_messages(self):
        response = requests.get("http://127.0.0.1:5000/messages",
                                params={'after': self.last_time})
        messages = response.json()
        self.log_info(messages)

        for message in messages:
            beauty_time = datetime.fromtimestamp(message["time"])
            beauty_time = beauty_time.strftime('%d/%m/%Y %H:%M:%S')
            self.add_to_chat(message["username"] + ' ' + beauty_time)
            self.add_to_chat(message["text"])
            self.add_to_chat('')

            self.last_time = message["time"]

        time.sleep(0.1)
        self.scrollbar.setValue(self.scrollbar.maximum())

    def button_clicked(self):
        send_params = {'username': self.plainTextEdit.toPlainText(),
                       'password': self.plainTextEdit_2.toPlainText(),
                       'message': self.textEdit.toPlainText()}
        try:
            self.send_message(send_params['username'], send_params['password'], send_params['message'])
            # self.log_info(['button_clicked', send_params['username'],send_params['password'],send_params['message']])
        except:
            self.add_to_chat('button_clicked: Произошла ошибка отправки')

        # self.textEdit.setText('')
        # self.textEdit.repaint()

    def add_to_chat(self, text):
        self.log_info([text])
        self.textBrowser.append(text)


app = QtWidgets.QApplication([])
window = MessengerApp()
window.show()
app.exec_()
window.refresh_timer.cancel()
