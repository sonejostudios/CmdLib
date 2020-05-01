# CmdLib
A Command Library GUI for GNU/Linux.



__Description:__

CmdLib is a small library app for your favorite commands. The idea started because I was so tired to look up all the time for commands I already used once... With CmdLib, you can collect them all in one place, and you'll have them for the future. You can search your commands, put them in categories with names and descriptions, create command lists and even export them to bash scripts.


![screenshot](https://github.com/sonejostudios/CmdLib/blob/master/CmdLib.png "CmdLib")


__Main Features:__

* Add a name, a description at set a category to each command
* Set a working directory to use in the selected command
* Search across the whole commands entries (name category, commands)
* Add/Delete commands
* Backup/Export/Import libraries
* One-click help button for Manpage, help, version, and what you like
* File and path picker to insert files easily into a command
* File picker to clipboard
* Copy the command to clipboard 
* Hold the terminal after running a commands
* Create command lists
* Run lists in parallel or as a sequence
* Export commands to bash scripts
* Insert you scripts directly into the library
* Open scripts and selected files directly
* Integrate it to Caja/Nautilus via a script
* The library is a simple csv file (easily editable with LibreOffice)


  

__Installation:__

1. copy the whole CmdLib folder on your system
```
git clone https://github.com/sonejostudios/CmdLib.git
```

2. from this folder start CmdLib with:
```
CmdLib.sh
```
or
```
python3 BookerDB.py
```

__Requirements:__

* GNU/Linux
* Python3

__Required libraries:__

* PySide2
* pyperclip
* notify2
* pandas

(use sudo pip install to install tem)


__Caja/Nautilus Integration:__

1. Open CmdLibWorkdir.sh
2. Change cd to the installation path of CmdLib
3. If you use Nautilus, change $CAJA_SCRIPT_CURRENT_URI with $NAUTILUS_SCRIPT_CURRENT_URI
4. Save
5. Copy CmdLibWorkdir.sh to your Caja/Nautilus Script directory (e.g. ~.config/caja/scripts)

Now, when you go to a directory, start CmdLibWorkdir.sh with the context menu. It will insert the actual directory as workdir automatically


__Shortcuts:__

* Ctrl+F = Focus on Find/Search
* Ctrl+L or Tab = Focus on Library
* Ctrl+Return = Run Command 
* Ctrl+N = Create new commands
* Delete = Delete selected command from library
* Ctrl+S = Save command to library
* Ctrl+H = Show Help (Manpage/Help/Verion/Whatever)






