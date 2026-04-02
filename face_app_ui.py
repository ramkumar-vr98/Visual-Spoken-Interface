# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'face_app.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1055, 630)
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(11)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet(u"/* ================= GLOBAL ================= */\n"
"QWidget {\n"
"    background-color: #0b1220;\n"
"    color: #e6edf7;\n"
"    font-family: Segoe UI, Arial;\n"
"    font-size: 10.5pt;\n"
"}\n"
"\n"
"/* ================= TITLE LABEL ================= */\n"
"QLabel#titleLabel {\n"
"    color: #6ee7ff;\n"
"    font-size: 22pt;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* ================= CAMERA VIEW ================= */\n"
"QLabel#camera_label {\n"
"    background-color: #050a12;\n"
"    border: 2px solid #2a3a52;\n"
"    border-radius: 12px;\n"
"    color: #6b7c93;\n"
"}\n"
"\n"
"/* ================= RESULT BANNER ================= */\n"
"QLabel#resultBanner {\n"
"    border-radius: 12px;\n"
"    padding: 12px;\n"
"    font-size: 16pt;\n"
"    font-weight: bold;\n"
"    background-color: #111a2b;\n"
"    border: 2px solid #22324a;\n"
"}\n"
"\n"
"/* ================= BUTTONS ================= */\n"
"QPushButton {\n"
"    background-color: #1e2a3a;\n"
"    border: 1px solid #2f4a6a;\n"
"    border-radius: 8px;"
                        "\n"
"    padding: 8px;\n"
"    color: #cfe8ff;\n"
"    font-weight: 600;\n"
"}\n"
"\n"
"/* Hover */\n"
"QPushButton:hover {\n"
"    background-color: #26384f;\n"
"    border: 1px solid #3b82f6;\n"
"}\n"
"\n"
"/* Pressed */\n"
"QPushButton:pressed {\n"
"    background-color: #1b2c3f;\n"
"}\n"
"\n"
"/* START BUTTON (GREEN) */\n"
"QPushButton#start_button {\n"
"    background-color: #0f9d58;\n"
"    border: 1px solid #17c96b;\n"
"    color: white;\n"
"}\n"
"\n"
"QPushButton#start_button:hover {\n"
"    background-color: #12b766;\n"
"}\n" 
"\n"
"/* STOP BUTTON (RED) */\n"
"QPushButton#stop_button {\n"
"    background-color: #b42318;\n"
"    border: 1px solid #ef4444;\n"
"    color: white;\n"
"}\n"
"\n"
"QPushButton#stop_button:hover {\n"
"    background-color: #d92d20;\n"
"}\n"
"\n"
"/* ================= PANELS ================= */\n"
"QListWidget, QTextEdit {\n"
"    background-color: #111827;\n"
"    border: 1px solid #2a3a52;\n"
"    border-radius: 8px;\n"
"    color: #d1d5db;\n"
"}\n"
"\n"
"/* ================="
                        " STATUS BAR ================= */\n"
"QStatusBar {\n"
"    background-color: #111827;\n"
"    color: #cbd5e1;\n"
"    border-top: 1px solid #2a3a52;\n"
"}")
        MainWindow.setIconSize(QSize(28, 30))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.camera_label = QLabel(self.centralwidget)
        self.camera_label.setObjectName(u"camera_label")
        self.camera_label.setGeometry(QRect(50, 110, 621, 341))
        self.start_button = QPushButton(self.centralwidget)
        self.start_button.setObjectName(u"start_button")
        self.start_button.setGeometry(QRect(680, 150, 171, 51))
        icon = QIcon()
        icon.addFile(u"../aieyes.jpg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.start_button.setIcon(icon)
        self.start_button.setIconSize(QSize(28, 29))
        self.stop_button = QPushButton(self.centralwidget)
        self.stop_button.setObjectName(u"stop_button")
        self.stop_button.setGeometry(QRect(680, 240, 171, 51))
        icon1 = QIcon()
        icon1.addFile(u"../stop_red_button_icon_227856.webp", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.stop_button.setIcon(icon1)
        self.stop_button.setIconSize(QSize(30, 33))
        self.resultBanner = QLabel(self.centralwidget)
        self.resultBanner.setObjectName(u"resultBanner")
        self.resultBanner.setGeometry(QRect(200, 40, 311, 61))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(16)
        font1.setBold(True)
        self.resultBanner.setFont(font1)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(220, 10, 331, 20))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(11)
        font2.setBold(True)
        font2.setUnderline(True)
        font2.setKerning(True)
        self.label.setFont(font2)
        self.finger_label = QLabel(self.centralwidget)
        self.finger_label.setObjectName(u"finger_label")
        self.finger_label.setGeometry(QRect(60, 510, 581, 51))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(11)
        font3.setBold(True)
        font3.setUnderline(False)
        self.finger_label.setFont(font3)
        self.name_label = QLabel(self.centralwidget)
        self.name_label.setObjectName(u"name_label")
        self.name_label.setGeometry(QRect(60, 450, 581, 51))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(11)
        font4.setBold(True)
        self.name_label.setFont(font4)
        self.left_blink_label = QLabel(self.centralwidget)
        self.left_blink_label.setObjectName(u"left_blink_label")
        self.left_blink_label.setGeometry(QRect(650, 450, 191, 51))
        self.left_blink_label.setFont(font4)
        self.right_blink_label = QLabel(self.centralwidget)
        self.right_blink_label.setObjectName(u"right_blink_label")
        self.right_blink_label.setGeometry(QRect(650, 510, 191, 51))
        self.right_blink_label.setFont(font4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1055, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.camera_label.setText(QCoreApplication.translate("MainWindow", u"camera_label", None))
        self.start_button.setText(QCoreApplication.translate("MainWindow", u"Start Camera", None))
        self.stop_button.setText(QCoreApplication.translate("MainWindow", u"Stop Button", None))
        self.resultBanner.setText(QCoreApplication.translate("MainWindow", u"SYSTEM READY", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"AIRPORT SECURITY SYSTEM", None))
        self.finger_label.setText(QCoreApplication.translate("MainWindow", u"Fingers: -", None))
        self.name_label.setText(QCoreApplication.translate("MainWindow", u"Name: -", None))
        self.left_blink_label.setText(QCoreApplication.translate("MainWindow", u"Left blink: 0", None))
        self.right_blink_label.setText(QCoreApplication.translate("MainWindow", u"Right blink: 0", None))
    # retranslateUi

