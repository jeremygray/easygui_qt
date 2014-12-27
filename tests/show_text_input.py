import os
import sys
sys.path.insert(0, os.getcwd())

try:
    from easygui_qt import easygui_qt
except ImportError:
    print("problem with import")

name = easygui_qt.get_string(message="What is your name?",
                            title="Mine is Reeborg.")

if sys.version_info < (3,):
    print name,
#else:
#    print(name, end='')
