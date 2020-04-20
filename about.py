#!/usr/bin/env python3

import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLineEdit, QFileDialog, QStyleFactory, QDialog
from PySide2.QtCore import QFile, QObject



class About(QDialog):

    def __init__(self, parent, appname, version):
        super(About, self).__init__(parent)

        ui_file = QFile('about.ui')
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.aboutwindow = loader.load(ui_file)
        ui_file.close()


        # set size
        self.aboutwindow.setFixedSize(466,317)


        # set names and versions
        self.aboutwindow.setWindowTitle("About " + appname)
        self.aboutwindow.label_name.setText(appname)
        self.aboutwindow.label_version.setText("Version: " + version)

        # signal to quit
        self.aboutwindow.ok_button.clicked.connect(self.close_about)


        # show dialog
        self.aboutwindow.show()



    def close_about(self):
        print("close about")
        self.aboutwindow.close()






#https://stackoverflow.com/questions/14309703/passing-parameter-from-main-window-to-pop-up-qdialog-window