#!/usr/bin/env python3

import sys
import subprocess
import os
import webbrowser
import datetime
import re
import pyperclip
import notify2

from urllib.parse import unquote, urlparse

import pandas as pd

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QFileDialog, QStyleFactory, QMessageBox, QAbstractItemView, QMainWindow, QPlainTextEdit, QAction, QShortcut, QDesktopWidget
from PySide2.QtCore import QFile, QObject, Qt
from PySide2.QtGui import QKeySequence



# import about dialog
from about import About






class CmdLib(QMainWindow):

    def __init__(self, parent=None):
        super(CmdLib, self).__init__(parent)

        # open ui file directly
        ui_file = QFile('mainwindow.ui')
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()


        # app name and version
        self.appname = "CmdLib"
        self.version = "0.1"


        # set fixed window size
        #self.window.setFixedSize(self.window.size())



        # set title and center window
        self.window.setWindowTitle(self.appname)
        self.center_window()






        # print available styles
        print(QStyleFactory.keys())




        ##### SIGNALS

        # run command
        self.window.button_run_term.clicked.connect(self.run_cmd_term)

        # load cmd
        #self.window.cmd_list.clicked.connect(self.load_cmd)
        self.window.cmd_list.itemSelectionChanged.connect(self.load_cmd)
        #self.window.cmd_list.currentRowChanged.connect(self.load_cmd)


        # add cmd to list
        self.window.button_to_list.clicked.connect(self.save_cmd)

        # delete cmd
        self.window.button_delete_cmd.clicked.connect(self.delete_cmd)


        # multi cmd mode
        self.window.multicmd_mode.clicked.connect(self.multicmd_mode)

        # is script mode
        self.window.check_script.clicked.connect(self.is_script)


        # search
        self.window.search_box.currentTextChanged.connect(self.search_cmds)

        # workdir
        self.window.set_workdir.clicked.connect(self.set_workdir)
        self.window.open_workdir.clicked.connect(self.open_workdir)
        self.window.workdir_line.editingFinished.connect(self.check_workdir)


        # show help from helpbox
        self.window.show_helpbox.clicked.connect(self.show_help)


        # new cmd
        self.window.new_button.clicked.connect(self.new_cmd)
        # copy cmd
        self.window.copy_button.clicked.connect(self.copy2clipboard)
        # add file name
        self.window.addfile_button.clicked.connect(self.on_insert_file_name)
        # open file
        self.window.openfile_button.clicked.connect(self.on_open_file_button)

        # if cmd selection is changed
        self.window.cmd_field.selectionChanged.connect(self.set_open_file_button)


        # check name
        self.window.name_field.textChanged.connect(self.check_name)
        # check command
        self.window.cmd_field.textChanged.connect(self.check_command)


        # DROP signal!!
        self.window.cmd_list.model().rowsMoved.connect(self.reorder_cmds)




        # menu/actions
        self.window.actionBackupLib.triggered.connect(self.backup)
        self.window.actionExportLib.triggered.connect(self.exportlib)
        self.window.actionImportLib.triggered.connect(self.importlib)

        self.window.actionInsert_File_Name.triggered.connect(self.on_insert_file_name)
        self.window.actionInsert_File_Path.triggered.connect(self.on_insert_file_path)
        self.window.actionExport2Script.triggered.connect(self.export2script)

        self.window.actionGet_File_Name.triggered.connect(self.on_copy_file_name)
        self.window.actionGet_File_Path.triggered.connect(self.on_copy_file_path)
        self.window.actionOpen_Scripts_Folder.triggered.connect(self.open_scriptsdir)
        self.window.actionOpen_File.triggered.connect(self.open_file)
        self.window.actionOpen_Script.triggered.connect(self.open_script)

        self.window.actionAbout.triggered.connect(self.on_about)



        # extra shortcuts
        # delete cmd from cmdlist
        QShortcut(QKeySequence(Qt.Key_Delete), self.window.cmd_list, self.delete_cmd)

        # save cmd
        QShortcut(QKeySequence("Ctrl+S"), self.window, self.on_save_cmd)

        # new cmd
        QShortcut(QKeySequence("Ctrl+N"), self.window, self.new_cmd)

        # new cmd
        QShortcut(QKeySequence("Ctrl+H"), self.window, self.show_help)

        # run in term
        QShortcut(QKeySequence("Ctrl+Return"), self.window, self.run_cmd_term)

        # focus on search
        QShortcut(QKeySequence("Ctrl+F"), self.window, self.focus_search)

        # focus on lib
        QShortcut(QKeySequence("Ctrl+L"), self.window, self.focus_lib)
        QShortcut(QKeySequence(Qt.Key_Tab), self.window, self.focus_lib)





        # trigger when quitting
        app.aboutToQuit.connect(self.on_quit)



        # update cmd list
        self.update_cmd_list()

        # select first cmd
        self.window.cmd_list.setCurrentRow(0)

        # load init command
        self.load_cmd()


        # set search box to All
        self.window.search_box.setCurrentIndex(0)

        #set focus on search box
        self.focus_search()


        # if provided, set first argument to workdir
        self.set_workdir_with_arg()


        # make start backup
        self.df.to_csv("./backups/cmds.csv", index=False)



        # show main window
        self.window.show()





    def test(self):
        print("test")


    def set_workdir_with_arg(self):
        if len(sys.argv) >= 2:
            # convert uri to path if needed (e.g. for nautilus/caja script)
            arg_path = unquote(urlparse(sys.argv[1]).path)
            print("workdir:", arg_path)
            # insert to workdir
            self.window.workdir_line.setText(arg_path)




    def focus_search(self):
        # set focus on search box
        self.window.search_box.setFocus()
        self.window.search_box.setCurrentIndex(0)


    def focus_lib(self):
        # set focus on search box
        self.window.cmd_list.setFocus()
        self.window.cmd_list.setCurrentRow(0)





    def center_window(self):
        # move main window to center of active screen
        frameGm = self.window.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.window.move(frameGm.topLeft())



    def set_open_file_button(self):
        prog = self.window.cmd_field.textCursor().selectedText()

        # enable / disable open file button
        if prog != "":
            self.window.openfile_button.setEnabled(True)
            self.window.actionOpen_File.setEnabled(True)

        elif self.window.check_script. isChecked() == True:
            self.window.openfile_button.setEnabled(True)

        else:
            self.window.openfile_button.setEnabled(False)
            self.window.actionOpen_File.setEnabled(False)



    def on_open_file_button(self):
        # get selection or cmd
        prog = self.window.cmd_field.textCursor().selectedText()

        if prog != "":
            self.open_file()

        if self.window.check_script.isChecked() == True:
            self.open_script()



    def open_file(self):
        # get selection or cmd
        prog = self.window.cmd_field.textCursor().selectedText()

        # remove space before and after
        prog = prog.strip()
        #print(prog)

        self.workdir = self.window.workdir_line.text()
        file = os.path.join(self.workdir, prog)
        #print(file)

        # open file if possible
        webbrowser.open(file)




    def open_script(self):
        cmd = self.window.cmd_field.toPlainText()
        prog = cmd.split(" ")[-1]
        #print(prog)
        file = os.path.join("./scripts", prog)
        print("open", file)

        # open file if possible
        webbrowser.open(file)







    def on_about(self):
        # show about dialog
        self.aboutDialog = About(self, self. appname, self.version)




    def on_quit(self):
        print("Quit " + self.appname)
        self.reorder_cmds()

        # save cmd list
        self.save_cmd_list()
        #self.backup()



    def notify(self, text):
        icon_path = os.getcwd() + "/logo.png"

        notify2.init('MyApp')
        n = notify2.Notification(self.appname, text, icon_path)
        n.show()



    def msgbox_warning(self,title, message):
        msgBox = QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.exec_()





    def multicmd_mode(self):
        if self.window.multicmd_mode.isChecked() == True:
            self.window.cmd_field.setLineWrapMode(QPlainTextEdit.NoWrap)
            self.window.cmd_label.setText("Commands:")
            self.window.ps_check.setEnabled(True)

        else:
            self.window.cmd_field.setLineWrapMode(QPlainTextEdit.WidgetWidth)
            self.window.cmd_label.setText("Command:")
            self.window.ps_check.setEnabled(False)




    def is_script(self):
        if self.window.check_script.isChecked() == True:
            pass
        #    self.workdir = self.window.workdir_line.text()
        #    self.window.workdir_line.clear()
        #    self.window.workdir_line.setText("./scripts")

            self.window.actionOpen_Script.setEnabled(True)

        else:
            pass
        #    self.window.workdir_line.clear()
        #    self.window.workdir_line.setText(self.workdir)

            self.window.actionOpen_Script.setEnabled(False)






    def new_cmd(self):
        self.window.cmd_list.clearSelection()


        #clear and reset all fields
        self.window.name_field.clear()
        self.window.description_field.clear()
        self.window.cmd_field.clear()
        self.window.category_box.setCurrentIndex(0)
        #self.window.cmd_list.clearSelection()

        # disable buttons
        self.window.button_delete_cmd.setEnabled(False)

        #resets checkboxes
        self.window.check_hold.setChecked(False)
        self.window.check_script.setChecked(False)
        self.window.multicmd_mode.setChecked(False)
        self.window.ps_check.setChecked(False)


        # set focus on cmd
        self.window.cmd_field.setFocus()







    def copy2clipboard(self):
        # get cmd
        cmd = self.window.cmd_field.toPlainText()

        # copy command to clipboard
        pyperclip.copy(str(cmd))

        self.notify("Command copied to clipboard!")






    def show_help(self):
        # get selection or cmd
        prog = self.window.cmd_field.textCursor().selectedText()

        if prog == "":
            # get first word of command
            cmd = self.window.cmd_field.toPlainText()
            prog = cmd.split(" ")[0]


        # get helpbox text
        helpboxtext = self.window.helpbox.currentText()
        print("show:", prog, helpboxtext)


        if helpboxtext == "manpage":
            # man cmd redirect to text file
            mancmd = "man " + prog + " > stdout.txt"
            subprocess.Popen(mancmd, shell=True)

        else:
            # man cmd redirect to text file
            hcmd = prog + " " + helpboxtext + " > stdout.txt"
            subprocess.Popen(hcmd, shell=True)

        # open text file with standard text editor
        webbrowser.open("stdout.txt")






    def set_workdir(self):
        #self.workdir = QFileDialog.getExistingDirectory(None, "Open Working Directory", "/home", QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog)
        self.workdir = QFileDialog.getExistingDirectory(None, "Open Working Directory", "/home", QFileDialog.ShowDirsOnly)

        if self.workdir != "":
            self.window.workdir_line.setText(self.workdir)
            self.window.check_script.setChecked(False)

        self.workdir = self.window.workdir_line.text()

        print("workdir:", self.workdir)




    def open_workdir(self):
        # get workdir
        workdir = self.window.workdir_line.text()

        # change to absolute path if needed
        if workdir == "./":
            workdir = os.getcwd()

        if workdir == "./scripts":
            workdir = os.getcwd() + "/scripts"

        print("show", workdir)
        webbrowser.open('file:///' + workdir)



    def open_scriptsdir(self):
        workdir = os.getcwd() + "/scripts"
        print("show", workdir)
        webbrowser.open('file:///' + workdir)



    def check_workdir(self):
        print("check workdir")

        if len(self.window.workdir_line.text()) <= 2:
            self.window.workdir_line.setText("./")







    def export2script(self):
        print("export")

        # get workdir and commands
        workdir = self.window.workdir_line.text()
        cmd = self.window.cmd_field.toPlainText()

        # un-hold commands
        cmd = cmd.replace("HOLD ","")

        # ask for file to save
        #savefile = QFileDialog.getSaveFileName(None, "Export as Bash Script", self.window.workdir_line.text(), "Bash Script .sh (*.sh)")
        savefile = QFileDialog.getSaveFileName(None, "Export as Bash Script", "./scripts", "Bash Script .sh (*.sh)")

        print(savefile)

        if savefile[0] == '':
            print("Export canceled")

        else:
            # get file path
            savefile = savefile[0]
            print(savefile)

            # generate script text
            script_text ="#!/bin/bash\n\ncd " + workdir +"\n\n" + cmd
            print(script_text)

            # save script to file path
            with open(savefile, 'w') as file:
                file.write(script_text)

            self.notify("Bash Script exported to\n" + savefile)

            # open script
            webbrowser.open(savefile)





    def on_insert_file_name(self):
        #print("insert filename")
        self.get_filepath(type="insert_name")



    def on_insert_file_path(self):
        #print("insert filepath")
        self.get_filepath(type="insert_path")



    def on_copy_file_name(self):
        #print("copy filename")
        self.get_filepath(type="copy_name")


    def on_copy_file_path(self):
        #print("copy filepath")
        self.get_filepath(type="copy_path")



    def get_filepath(self, type):
        #print("filepath action")

        file = QFileDialog.getOpenFileName(None, "Add File", self.window.workdir_line.text())
        file_path = file[0]
        print(file_path)

        if file_path != "":
            if type == "insert_name":
                # insert to cmd_field at cursor
                self.window.cmd_field.insertPlainText(os.path.basename(file_path))
                self.notify("File name inserted to command!\n" + os.path.basename(file_path))

            if type == "insert_path":
                # insert to cmd_field at cursor
                self.window.cmd_field.insertPlainText(file_path)
                self.notify("File path inserted to command!\n" + file_path)

            if type == "copy_name":
                # copy to clipboard
                pyperclip.copy(str(os.path.basename(file_path)))
                self.notify("File name copied to clipboard!\n" + os.path.basename(file_path))

            if type == "copy_path":
                # copy to clipboard
                pyperclip.copy(str(file_path))
                self.notify("File path copied to clipboard!\n" + file_path)







    def run_cmd_term(self):
        print("run")

        # set workdir
        workdir = self.window.workdir_line.text()


        # create list of commands
        cmd = self.window.cmd_field.toPlainText()
        cmds = cmd.split("\n")
        cmds = list(filter(None, cmds))
        #print(cmds)

        # get hold state from hold checkbox
        hold_state = self.window.check_hold.isChecked()


        # remove commented lines
        cmds = [s for s in cmds if not s.startswith('#')]
        print(cmds)


        # run each command
        for i in cmds:

            # check if HOLD written before command, if yes, remove it
            if i.split(" ")[0] == "HOLD":
                print(i)
                i = i[5:]
                print(i)
                hold_state = True


            if self.window.check_script.isChecked() == True:
                workdir = "./scripts"


            # create command depending if hold False or not
            if hold_state == False:
                cmd = "cd " + workdir + " ; xterm -e " + i
            else:
                cmd = "cd " + workdir + " ; xterm -hold -e " + i


            # to set up font size, use
            # xterm -fa 'Monospace' -fs 10

            # run cmd
            print(cmd)

            if self.window.ps_check.isChecked() == False:
                subprocess.Popen(cmd, shell=True) # parallel run
            else:
                subprocess.Popen(cmd, shell=True).wait() # serial run (but blocks main thread)


            # reset hold state
            hold_state = False







    def load_cmd(self):
        # get selected index of list
        self.itemrow = self.window.cmd_list.currentRow()

        # get item name from cmd list
        item = self.window.cmd_list.selectedItems()

        # workaround if item out of range, re-select current item
        if len(item) == 0:
            self.window.cmd_list.setCurrentRow(self.itemrow)
            item = self.window.cmd_list.selectedItems()


        # get row
        cmdrow = self.df.loc[self.df["name"] == item[0].text()]



        # clear fields
        self.window.cmd_field.clear()
        self.window.name_field.clear()
        self.window.description_field.clear()

        # insert items
        self.window.cmd_field.insertPlainText(cmdrow["command"].iloc[0])
        self.window.name_field.insert(cmdrow["name"].iloc[0])
        self.window.description_field.insertPlainText(cmdrow["description"].iloc[0])

        # set category
        index = self.window.category_box.findText(cmdrow["category"].iloc[0])
        self.window.category_box.setCurrentIndex(index)


        # set hold checkbox
        if cmdrow["hold"].iloc[0] == True:
            self.window.check_hold.setChecked(True)
        else:
            self.window.check_hold.setChecked(False)


        # set multi-cmd checkbox and check
        if cmdrow["multicmd"].iloc[0] == True:
            self.window.multicmd_mode.setChecked(True)
        else:
            self.window.multicmd_mode.setChecked(False)
        self.multicmd_mode()


        # set ps checkbox and check
        if cmdrow["ps"].iloc[0] == True:
            self.window.ps_check.setChecked(True)
        else:
            self.window.ps_check.setChecked(False)



        # set is_script checkbox
        if cmdrow["script"].iloc[0] == True:
            self.window.check_script.setChecked(True)
        else:
            self.window.check_script.setChecked(False)
        self.is_script()



        # enable delete button
        self.window.button_delete_cmd.setEnabled(True)


        # set open file button state
        self.set_open_file_button()







    def check_name(self):
        # check if name field is empty or not, then enables od disables buttons
        if self.window.name_field.text() == "" or self.window.cmd_field.toPlainText() == "":
            self.window.button_to_list.setEnabled(False)
        else:
            self.window.button_to_list.setEnabled(True)
        pass



    def check_command(self):
        # check if command field is empty or not, then enables od disables buttons
        if self.window.cmd_field.toPlainText() == "" :#or self.window.name_field.text() == "":
            #self.window.button_to_list.setEnabled(False)
            self.window.copy_button.setEnabled(False)
            self.window.show_helpbox.setEnabled(False)
            self.window.button_run_term.setEnabled(False)
            self.window.helpbox.setEnabled(False)

        else:
            #self.window.button_to_list.setEnabled(True)
            self.window.copy_button.setEnabled(True)
            self.window.show_helpbox.setEnabled(True)
            self.window.button_run_term.setEnabled(True)
            self.window.helpbox.setEnabled(True)


        if self.window.name_field.text() == "" :
            self.window.button_to_list.setEnabled(False)
        else:
            self.window.button_to_list.setEnabled(True)





    def on_save_cmd(self):
        # for ctrl-s shortcut, check if button enable or not
        if self.window.button_to_list.isEnabled() == True:
            self.save_cmd()
        else:
            print("noo")


    def save_cmd(self):
        # temp search text
        list_index = self.window.search_box.currentText()

        # get select variables
        command = self.window.cmd_field.toPlainText()
        name = self.window.name_field.text()
        description = self.window.description_field.toPlainText()
        category = self.window.category_box.currentText()
        hold = self.window.check_hold.isChecked()
        multicmd = self.window.multicmd_mode.isChecked()
        ps = self.window.ps_check.isChecked()
        script = self.window.check_script.isChecked()


        # save order first
        self.reorder_cmds()

        # if description empty, insert placeholder
        if description == "":
            description = "-"

        # prepare new item
        new_item = {"command": command, "name": name, "category": category, "hold": hold, "multicmd": multicmd, "ps": ps, "script": script, "description": description}


        # get name list and command list
        namelist = list(self.df["name"])
        cmdlist = list(self.df["command"])

        # if cmds exists, save it. else, append it
        if name in namelist:
            # find row with name
            col = self.df.loc[self.df["name"] == name]
            # get index out of row
            index = col.index[0]
            # write to cells
            self.df.at[index, 'command'] = command
            self.df.at[index, 'description'] = description
            self.df.at[index, 'category'] = category
            self.df.at[index, 'hold'] = hold
            self.df.at[index, 'multicmd'] = multicmd
            self.df.at[index, 'ps'] = ps
            self.df.at[index, 'script'] = script

        else:
            self.df = self.df.append(new_item, ignore_index=True, sort=False)

            #set selected item to item count for later auto selection
            self.itemrow = self.window.cmd_list.count()


        # save cmd list
        self.save_cmd_list()

        # update list
        self.update_cmd_list()

        # re-insert search text after saving
        self.window.search_box.setCurrentText(list_index)

        # re-select item
        self.window.cmd_list.setCurrentRow(self.itemrow)

        # re-load selected command
        self.load_cmd()

        # notify
        self.notify("Command " + name + " saved!")








    def save_cmd_list(self):
        #print("save cmd list")
        # show all entries in cmd list before saving
        self.window.search_box.setCurrentIndex(0)
        #print(self.df)

        # save to file
        self.df.to_csv("cmds.csv", index=False)








    def delete_cmd(self):
        #print("delete cmd")

        # get selected item
        item = self.window.name_field.text()
        command = self.window.cmd_field.toPlainText()
        print("delete",item, command)

        choice = QMessageBox.question(None, "Delete command?", "Do you want to delete this command?\n\n" + item + "\n" + command, QMessageBox.No | QMessageBox.Yes)

        if choice == QMessageBox.Yes:
            # drop row with item
            #self.df = self.df[~self.df["name"].str.match(item)]
            self.df = self.df[~self.df["name"].isin([item])]


            # save cmd list
            self.df.to_csv("cmds.csv", index=False)


            # temp search text
            list_index = self.window.search_box.currentText()

            # set current row to 0 before updating
            self.window.cmd_list.setCurrentRow(0)

            # update list
            self.update_cmd_list()

            # re-insert search text after deleting
            self.window.search_box.setCurrentText(list_index)


            # disable delete button
            self.window.button_delete_cmd.setEnabled(False)

            #notify
            self.notify("Command " + item + " deleted!")






    def search_cmds(self):
        # get search text
        word = self.window.search_box.currentText()

        # filter
        if word != "":
            # create new df with search results
            df_found = self.df[self.df.astype(str).add('|').sum(1).str.contains(word)]
            #print(df_found)

            # clear cmd_list and repopulate
            self.window.cmd_list.clear()
            cmds = list(df_found["name"])
            self.window.cmd_list.addItems(cmds)



            # disable drag and drop
            self.window.cmd_list.setDragDropMode(QAbstractItemView.NoDragDrop)


        else:
            # enable drag and drop
            self.window.cmd_list.setDragDropMode(QAbstractItemView.InternalMove)
            # update cmd list
            self.update_cmd_list()


        # select first cmd
        #self.window.cmd_list.setCurrentRow(0)


        # disable delete button
        self.window.button_delete_cmd.setEnabled(False)





    def update_cmd_list(self):
        #items = []
        #for i in range(self.window.cmd_list.count()):
        #    items.append(self.window.cmd_list.item(i))
        #self.cmdlist = []
        #for item in items:
        #    self.cmdlist.append(item.text())
        #print(self.cmdlist)

        # get workdir
        self.workdir = self.window.workdir_line.text()


        # load from csv
        self.df = pd.read_csv("cmds.csv", header=0, index_col=False)
        #print(self.df)
        self.window.cmd_list.clear()
        cmds = list(self.df["name"])
        self.window.cmd_list.addItems(cmds)


        # raise warning if library is empty
        if len(self.df) == 0:
            QMessageBox.warning(None, "Library Error", "An error occured and the library is empty!\nPlease check your backups and replace the library file (cmds.csv).", QMessageBox.Ok)


        # categories
        categories = list(self.df["category"])
        cat2 = []
        for i in categories:
            if i not in cat2:
                cat2.append(i)
        categories = cat2
        #print(categories)

        # populate category box
        self.window.category_box.clear()
        self.window.category_box.insertItems(0, categories)

        # populate search box
        self.window.search_box.clear()
        self.window.search_box.insertItems(0, [""] + categories)


        # get cmds amount
        cmds_amount = len(self.df)
        #print("cmds:", cmds_amount)
        self.window.cmds_amount.setText(str(cmds_amount))





    def reorder_cmds(self):
        print("reorder and save command list")

        # create list out of items
        items = []
        for i in range(self.window.cmd_list.count()):
            items.append(self.window.cmd_list.item(i).text())

        #print(items)
        df2 = pd.DataFrame(columns=['name', 'command', 'category', 'hold', 'multicmd', 'ps', 'script', 'description'])

        # if item found on df, append it to df2
        for item in items:
            for index, row in self.df.iterrows():
                if row["name"] == item:
                    df2 = df2.append(row)

        self.df = df2
        self.save_cmd_list()





    def backup(self):
        self.reorder_cmds()

        backup_name = datetime.datetime.now()

        backup_name = str(backup_name)
        backup_name = re.split('[-\s:.]', backup_name)
        backup_name = "cmds_" + backup_name[0] + backup_name[1] + backup_name[2] + "_" + backup_name[3] + backup_name[4] + backup_name[5] + ".csv"

        self.df.to_csv("./backups/" + backup_name, index=False)

        self.notify("Backup saved!\n" + backup_name)




    def exportlib(self):
        print("export lib")
        # ask for file to save
        exportlib = QFileDialog.getSaveFileName(None, "Export Library", "./libraries", "CSV .csv (*.csv)")
        filepath = exportlib[0]
        print(filepath)

        if filepath == '':
            print("Export canceled")
        else:
            print("Export lib!")
            self.reorder_cmds()
            self.df.to_csv(filepath, index=False)
            self.notify("Library exported!\n" + filepath)





    def importlib(self):
        print("import lib")

        msgboxtext = "This will overwrite your actual command library!\nYou might want to do a backup or export it first.\nAre you sure you want to proceed?"
        choice = QMessageBox.question(None, "Import Library?", msgboxtext, QMessageBox.No | QMessageBox.Yes)

        if choice == QMessageBox.Yes:
            #print("yes")
            #self.backup()
            importlib = QFileDialog.getOpenFileName(None, "Import Library", "./libraries", "CSV .csv (*.csv)")
            filepath = importlib[0]
            print(filepath)

            if filepath == '':
                print("Import canceled")
            else:
                print("Import lib!")
                overwrite_lib = "cp " + filepath + " ./cmds.csv"
                subprocess.call(overwrite_lib, shell=True) #call waits until finished

                self.update_cmd_list()
                self.notify("Library imported!\n" + filepath)













if __name__ == '__main__':
    app = QApplication(sys.argv)

    #style = QStyleFactory.create('GTK+')
    #app.setStyle(style)

    myapp = CmdLib()
    sys.exit(app.exec_())
