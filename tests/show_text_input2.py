"""
Almost identical to show_text_input.py except that we specify a default
response for the textbox. This argument should be returned when
the ok button is pressed without entering text before.
"""

import os
import sys
sys.path.insert(0, os.getcwd())

try:
    from easygui_qt import easygui_qt
except ImportError:
    print("problem with import")

name = easygui_qt.get_string(message="What is your name?",
                            title="Mine is Reeborg.",
                            default_response="Hello")

if sys.version_info < (3,):
    print name,
#else:
#    print(name, end='')
