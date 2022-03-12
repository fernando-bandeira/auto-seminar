import sys
import requests
from datetime import datetime, timedelta
from itertools import cycle
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QLineEdit, QWidget, QGridLayout, QPlainTextEdit
from PyQt5.QtCore import QObject, QThread, pyqtSignal


class Worker(QObject):
    finished = pyqtSignal()

    def run(self):
        key = app.key_input.text().strip()
        token = app.token_input.text().strip()

        date_ini = datetime.strptime(app.ini_input.text().strip(), '%Y-%m-%d')
        date_end = datetime.strptime(app.end_input.text().strip(), '%Y-%m-%d')
        dates = []
        date_aux = date_ini
        while date_aux < date_end:
            dates.append(date_aux)
            date_aux += timedelta(days=7)

        m_list = app.members_input.toPlainText()
        members = [member.upper().strip() for member in m_list.split(',')]

        seminars = list(zip(dates, cycle(members)))

        for seminar in seminars:
            app.create_card(key, token, seminar)


class App(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('AutoSeminar')

        self.cw = QWidget()
        self.grid = QGridLayout(self.cw)

        self.auth_label = QLabel(
            'Informe a API Key do Trello e seu token de acesso:'
        )

        self.key_label = QLabel('API Key:')
        self.key_input = QLineEdit('')

        self.token_label = QLabel('Token:')
        self.token_input = QLineEdit(
            ''
        )

        self.dates_label = QLabel(
            'Informe o período dos seminários no formato YYYY-MM-DD'
        )
        self.dates_label.setStyleSheet('margin-top: 20px;')

        self.ini_label = QLabel('Data do primeiro seminário:')
        self.ini_input = QLineEdit()

        self.end_label = QLabel('Data final:')
        self.end_input = QLineEdit()

        self.members_label = QLabel(
            'Membros em ordem de apresentação, separados por vírgula:'
        )
        self.members_label.setStyleSheet('margin-top: 20px;')
        self.members_input = QPlainTextEdit('ABC, XYZ, CVP')

        self.submit = QPushButton('Enviar')
        self.submit.clicked.connect(self.fill_trello)

        self.grid.addWidget(self.auth_label, 0, 0, 1, 2)
        self.grid.addWidget(self.key_label, 1, 0, 1, 1)
        self.grid.addWidget(self.token_label, 1, 1, 1, 1)
        self.grid.addWidget(self.key_input, 2, 0, 1, 1)
        self.grid.addWidget(self.token_input, 2, 1, 1, 1)
        self.grid.addWidget(self.dates_label, 3, 0, 1, 2)
        self.grid.addWidget(self.ini_label, 4, 0, 1, 1)
        self.grid.addWidget(self.end_label, 4, 1, 1, 1)
        self.grid.addWidget(self.ini_input, 5, 0, 1, 1)
        self.grid.addWidget(self.end_input, 5, 1, 1, 1)
        self.grid.addWidget(self.members_label, 6, 0, 1, 2)
        self.grid.addWidget(self.members_input, 7, 0, 1, 2)
        self.grid.addWidget(self.submit, 8, 0, 1, 2)

        self.setCentralWidget(self.cw)

    def create_card(self, key, token, seminar):
        url = f'https://api.trello.com/1/cards'
        querystring = {
            'name': f'Seminário {seminar[1]} | {seminar[0].strftime("%d/%m")}',
            'desc': (
                '[DESCRIÇÃO]\n'
                f'Data: {seminar[0].strftime("%d/%m")}\n'
                'Horário: 12:05\n'
            ),
            'idCardSource': '622d16b832ba5b1cf8790ac6',
            'keepFromSource': ['checklists'],
            'pos': 'bottom',
            'idList': '622d09128291387a934d4df5',  # 0884e55cbd71612b1f1a2f7
            'key': key,
            'token': token
        }
        requests.request('POST', url, params=querystring)

    def fill_trello(self):
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        self.submit.setDisabled(True)
        self.thread.finished.connect(
            lambda: self.submit.setDisabled(False)
        )


if __name__ == '__main__':
    qt = QApplication(sys.argv)
    app = App()
    app.show()
    qt.exec_()
