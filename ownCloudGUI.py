import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QMessageBox, QProgressBar
from PyQt5.QtCore import pyqtSlot
import os
from shutil import rmtree
from time import sleep
import threading
import psutil

# owncloudcmd -u testGUI -p mexmatIT C:\Users\tosha\Desktop\ownCloud\ http://disk.mmcs.sfedu.ru
class ownCloudGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'ownCloudGUI'
        self.left = 250
        self.top = 250
        self.width = 400
        self.height = 200
        self.initUI()

        self.dir_user = 'C:\\Users\\' + os.getlogin() + '\\Desktop\\ownCloud\\'
        self.dir_tmp  = 'C:\\Users\\' + os.getlogin() + '\\Documents\\ownCloud\\'
        self.dir_ownCloud = 'owncloudcmd'

        self.name_tmp = '~ownCloud.TMP'
        self.name_lock = '~lock_ownCloud.TMP'
        self.serv_url = 'http://disk.mmcs.sfedu.ru '

        if not (os.path.exists(self.dir_tmp)):
            os.mkdir(self.dir_tmp)

        this_pid = (os.getpid())
        if not (os.path.exists(self.dir_tmp + self.name_lock)):
            owncloud_pid = open(self.dir_tmp + self.name_lock, 'w')
            owncloud_pid.write(str(this_pid) + '\n')
            owncloud_pid.close()
        else:
            owncloud_pid = open(self.dir_tmp + self.name_lock)
            pid = owncloud_pid.read().strip()
            owncloud_pid.close()
            for proc in psutil.process_iter():
                if proc.name() == 'python.exe' and str(proc.pid) == pid:
                    QMessageBox.question(self, 'Message','ownCloudGUI уже открыт',QMessageBox.Yes)
                    exit()
            owncloud_pid = open(self.dir_tmp + self.name_lock, 'w')
            owncloud_pid.write(str(this_pid) + '\n')
            owncloud_pid.close()

        self.del_old_tmp()
        self.thread = threading.Thread(target=self.del_old_tmp())
        self.thread.start()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.user_label = QLabel(self)
        self.user_label.move(20, 25)
        self.user_label.setText('user')
        self.passwd_label = QLabel(self)
        self.passwd_label.move(20, 75)
        self.passwd_label.setText('passwd')

        self.user = QLineEdit(self)
        self.user.move(60, 25)
        self.user.resize(320, 30)

        self.passwd = QLineEdit(self)
        self.passwd.setEchoMode(QLineEdit.Password)
        self.passwd.move(60, 75)
        self.passwd.resize(320, 30)

        self.connect = QPushButton('Connect', self)
        self.connect.move(20, 130)
        self.connect.clicked.connect(self.connect_click)

        self.synchronized = QPushButton('Synchronized', self)
        self.synchronized.move(150, 130)
        self.synchronized.setDisabled(True)
        self.synchronized.clicked.connect(self.synchronized_click)

        self.disconnect = QPushButton('Disconnect', self)
        self.disconnect.move(280, 130)
        self.disconnect.setDisabled(True)
        self.disconnect.clicked.connect(self.disconnect_click)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(21, 170, 393, 20)

        self.show()

    def closeEvent(self, event):
        self.del_trace()

    @pyqtSlot()
    def disconnect_click(self):
        self.del_trace()
        self.passwd.setDisabled(False)
        self.user.setDisabled(False)
        self.connect.setDisabled(False)

        self.synchronized.setDisabled(True)
        self.disconnect.setDisabled(True)

    @pyqtSlot()
    def synchronized_click(self):
        if self.synch(self.comm) == 1:
            QMessageBox.question(self, 'Message', 'Ошибка синхронизации. Перенисите файлы из расширенной папки и нажмите "ОК"', QMessageBox.Yes)
            self.synch(self.comm)
            self.passwd.setDisabled(False)
            self.user.setDisabled(False)
            self.connect.setDisabled(False)
            self.disconnect.setDisabled(True)
            self.synchronized.setDisabled(True)
            self.del_trace()

    @pyqtSlot()
    def connect_click(self):
        try:
            self.passwd.setDisabled(True)
            self.user.setDisabled(True)
            self.connect.setDisabled(True)
            self.disconnect.setDisabled(False)
            self.synchronized.setDisabled(False)
            self.del_trace()

            user_c = '-u ' + self.user.text() + ' '
            passwd_c = '-p ' + self.passwd.text() + ' '

            self.thread.join()

            owncloud_tmp = open(self.dir_tmp + self.name_tmp, 'w')
            owncloud_tmp.write(user_c + '\n')
            owncloud_tmp.write(passwd_c + '\n')
            owncloud_tmp.close()

            os.mkdir(self.dir_user)
            self.comm = self.dir_ownCloud + ' ' + user_c + passwd_c + self.dir_user + ' ' + self.serv_url
            if  self.synch(self.comm) == 1:
                QMessageBox.question(self, 'Message', 'Не удалось подключиться, возможно вы ввели неправильные данные', QMessageBox.Yes)
                self.passwd.setDisabled(False)
                self.user.setDisabled(False)
                self.connect.setDisabled(False)
                self.disconnect.setDisabled(True)
                self.synchronized.setDisabled(True)
                self.del_trace()
        except:
            print('err')

    def synch(self, comm):
        self.disconnect.setDisabled(True)
        self.synchronized.setDisabled(True)
        self.progress.setValue(1)

        res = os.system(self.comm)
        self.progress.setValue(100)

        self.disconnect.setDisabled(False)
        self.synchronized.setDisabled(False)
        return res;

    def del_trace(self):
        try:
            if os.path.exists(self.dir_user):
                rmtree(self.dir_user)
            if os.path.exists(self.dir_user + self.name_tmp):
                os.remove(self.dir_user + self.name_tmp)
            if os.path.exists(self.dir_user + self.name_lock):
                os.remove(self.dir_user + self.name_lock)
        except PermissionError:
            reply = QMessageBox.question(self, 'Message', 'Не получается удалить файлы', QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                sleep(1)
                self.del_trace()


    def del_old_tmp(self):
        if os.path.exists(self.name_tmp):
            owncloud_tmp = open(self.name_tmp)
            tmp_text = owncloud_tmp.read()
            tmp_text = tmp_text.split('\n')
            owncloud_tmp.close()

            if os.path.exists(self.dir_user):
                self.synch(self.comm)

            self.del_trace()

if __name__ == '__main__':
    owncloud = QApplication(sys.argv)
    ex = ownCloudGUI()
    sys.exit(owncloud.exec_())