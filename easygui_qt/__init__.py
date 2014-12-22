# -*- coding: utf-8 -*-
__author__ = 'André Roberge'
__email__ = 'andre.roberge@gmail.com'
__version__ = '0.1.0'
"""easygui_qt: procedural gui based on PyQt

easygui_qt is inspired by easygui and contains a number
of different basic graphical user interface components
"""



import os
import collections
import functools
import inspect
from PyQt4 import QtGui, QtCore

__all__ = [
    'get_choice',
    'get_float',
    'get_int',
    'get_integer',
    'get_string',
    'set_global_font',
    'set_locale',
    'show_message',
]



CONFIG = {'font': QtGui.QFont(),
          'translator': QtCore.QTranslator(),
          'locale': 'default'}
QM_FILES = None


def with_app(func):
    """Intended to be used as a decorator to ensure that a single app
       is running before the function is called, and stopped afterwords
    """

    def _decorator(*args, **kwargs):
        """A single decorator would be enough to start an app before the
           function is called. By using an inner decorator, we can quit
           the app after the function is done.
        """
        app = SimpleApp()
        kwargs['app'] = app
        try:
            response = func(*args, **kwargs)
        except TypeError:  # perhaps 'app' was not a keyword argument for func
            sig = inspect.signature(func)
            if 'app' in sig.parameters.values():
                raise
            else:
                del kwargs['app']
                response = func(*args, **kwargs)
        app.quit()
        return response

    return functools.wraps(func)(_decorator)


def find_qm_files():
    """looking for files with names == qt_locale.qm"""
    all_files = collections.OrderedDict()
    for root, _, files in os.walk(os.path.join(QtGui.__file__, "..")):
        for fname in files:
            if (fname.endswith('.qm') and fname.startswith("qt_")
                    and not fname.startswith("qt_help")):
                locale = fname[3:-3]
                all_files[locale] = root
    return all_files


class SimpleApp(QtGui.QApplication):
    """A simple extention of the basic QApplication
       with added methods useful for working with dialogs
       that are not class based.
    """

    def __init__(self):
        super().__init__([])
        self.setFont(CONFIG['font'])
        self.set_locale(None)  # recover locale set by previous run, if any ...

    def set_locale(self, locale):
        """Sets the language of the basic controls for PyQt
           from a locale - provided that the corresponding qm files
           are present in the PyQt distribution.
        """
        global QM_FILES
        if QM_FILES is None:
            QM_FILES = find_qm_files()

        if locale in QM_FILES:
            if CONFIG['translator'].load("qt_" + locale, QM_FILES[locale]):
                self.installTranslator(CONFIG['translator'])
                CONFIG['locale'] = locale
            else:
                print("language not available")
        elif locale is "default" and CONFIG['locale'] != 'default':
            self.removeTranslator(CONFIG['translator'])
            CONFIG['translator'] = QtCore.QTranslator()
            CONFIG['locale'] = 'default'
        elif CONFIG['locale'] in QM_FILES:
            if CONFIG['translator'].load("qt_" + CONFIG['locale'],
                                         QM_FILES[CONFIG['locale']]):
                self.installTranslator(CONFIG['translator'])


class _LanguageSelector(QtGui.QDialog):
    """A specially constructed dialog which uses informations about
       available language (qm) files which can be used to change the
       default language of the basic PyQt ui components.
    """

    def __init__(self, parent, title="Language selection",
                 name="Language codes",
                 instruction="Click button when you are done"):
        super().__init__(None, QtCore.Qt.WindowSystemMenuHint |
                         QtCore.Qt.WindowTitleHint)

        self.qm_files_choices = {}
        self.parent = parent

        # ========= check boxes ==============
        group_box = QtGui.QGroupBox(name)
        group_box_layout = QtGui.QGridLayout()
        for i, locale in enumerate(QM_FILES):
            check_box = QtGui.QCheckBox(locale)
            check_box.setAutoExclusive(True)
            self.qm_files_choices[check_box] = locale
            check_box.toggled.connect(self.check_box_toggled)
            group_box_layout.addWidget(check_box, i / 4, i % 4)
        # adding default language option. When using the PyQt distribution
        # no "en" files were found and yet "en" was the obvious default.
        # We need this option in case we want to revert a change.
        check_box = QtGui.QCheckBox("Default")
        check_box.setAutoExclusive(True)
        self.qm_files_choices[check_box] = "default"
        check_box.toggled.connect(self.check_box_toggled)
        i = len(QM_FILES)
        group_box_layout.addWidget(check_box, i / 4, i % 4)
        group_box.setLayout(group_box_layout)

        # ========= buttons ==============
        button_box = QtGui.QDialogButtonBox()
        confirm_button = button_box.addButton(QtGui.QDialogButtonBox.Ok)
        confirm_button.clicked.connect(self.confirm)

        # ========= finalizing layout ====
        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(group_box)
        main_layout.addWidget(QtGui.QLabel(instruction))
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)
        self.setWindowTitle(title)

    def check_box_toggled(self):
        """Callback when a checkbox is toggled"""
        self.locale = self.qm_files_choices[self.sender()]

    def confirm(self):
        """Callback from confirm_button used to set the locale"""
        if self.locale != CONFIG['locale']:
            self.parent.set_locale(self.locale)
        self.close()


@with_app
def set_global_font():
    """GUI component to set default font"""
    font, ok = QtGui.QFontDialog.getFont(CONFIG['font'], None)
    if ok:
        CONFIG['font'] = font



@with_app
def yes_no_question(question="Answer this question", title="Title"):
    """Simple yes or no question; returns True for "Yes", False for "No"
       and None for "Cancel".
    """
    flags = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
    flags |= QtGui.QMessageBox.Cancel

    reply = QtGui.QMessageBox.question(None, title, question, flags)
    if reply == QtGui.QMessageBox.Yes:
        return True
    elif reply == QtGui.QMessageBox.No:
        return False


@with_app
def select_language(title="Select language", name="Language codes",
                    instruction="Click button when you are done", app=None):
    """Dialog to choose language based on some locale code for
       files found on default path
       """
    selector = _LanguageSelector(app, title=title, name=name,
                                 instruction=instruction)
    selector.exec_()


@with_app
def set_locale(locale, app=None):
    """Sets the locale, if available"""
    app.set_locale(locale)


@with_app
def show_message(message="Message", title="Title"):
    """Simple message box."""
    box = QtGui.QMessageBox(None)
    box.setWindowTitle(title)
    box.setText(message)
    box.show()
    box.exec_()


@with_app
def get_int(message="Choose a number", title="Title",
                  default_value=1, min_=0, max_=100, step=1):
    """Simple dialog to ask a user to select an integer within a certain range.

       **Note**: **get_int()** and **get_integer()** are identical.

       :param message: Message displayed to the user, inviting a response
       :param title: Window title
       :param default_value: Default value for integer appearing in the text
                             box; set to the closest of ``min_`` or ``max_``
                             if outside of allowed range.
       :param min_: Minimum integer value allowed
       :param max_: Maximum integer value allowed
       :param step: Indicate the change in integer value when clicking on
                    arrows on the right hand side

       :return: an integer, or ``None`` if "cancel" is clicked or window
                is closed.

       >>> import easygui_qt as eg
       >>> number = eg.get_int()

       .. image:: ../docs/images/get_int.png


       If ``default_value`` is larger than ``max_``, it is set to ``max_``;
       if it is smaller than ``min_``, it is set to ``min_``.

       >>> number = eg.get_integer("Enter a number", default_value=125)

       .. image:: ../docs/images/get_int2.png

    """
    flags = QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint
    number, ok = QtGui.QInputDialog.getInteger(None,
                                               title, message,
                                               default_value, min_, max_, step,
                                               flags)
    if ok:
        return number
get_integer = get_int


@with_app
def get_float(message="Choose a number", title="Title",
                  default_value=0., min_=-10000, max_=10000, step=1):
    """Simple dialog to ask a user to select a floating point number
       within a certain range.

       :param message: Message displayed to the user, inviting a response
       :param title: Window title
       :param default_value: Default value for integer appearing in the text
                             box; set to the closest of ``min_`` or ``max_``
                             if outside of allowed range.
       :param min_: Minimum integer value allowed
       :param max_: Maximum integer value allowed
       :param step: Indicate the change in integer value when clicking on
                    arrows on the right hand side

       :return: an integer, or ``None`` if "cancel" is clicked or window
                is closed.

       >>> import easygui_qt as eg
       >>> number = eg.get_float()

       .. image:: ../docs/images/get_float.png


    """
    flags = QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint
    number, ok = QtGui.QInputDialog.getDouble(None,
                                              title, message,
                                              default_value, min_, max_, step,
                                              flags)
    if ok:
        return number

@with_app
def get_string(message="Enter your response", title="Title",
               default_response=""):
    """Simple text input box.  Used to query the user and get a string back.

       :param message: Message displayed to the user, inviting a response
       :param title: Window title
       :param default_response: default response appearing in the text box

       :return: a string, or ``None`` if "cancel" is clicked or window
                is closed.

       >>> import easygui_qt as eg
       >>> reply = eg.get_string()

       .. image:: ../docs/images/get_string.png

       >>> reply = eg.get_string("new message", default_response="ready")


       .. image:: ../docs/images/get_string2.png
    """
    flags = QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint
    text, ok = QtGui.QInputDialog.getText(None, title, message,
                                          QtGui.QLineEdit.Normal,
                                          default_response, flags)
    if ok:
        return text

@with_app
def get_choice(message="Choices", title="Title", choices=None):
    """Simple dialog to ask a user to select an item within a list"""
    if choices is None:
        choices = ["Item 1", "Item 2", "Item 3"]
    flags = QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint
    choice, ok = QtGui.QInputDialog.getItem(None, title,
            message, choices, 0, False, flags)
    if ok:
        return choice


def set_font_size(font_size):
    """Simple method to set font size.
    """
    try:
        CONFIG['font'].setPointSize(font_size)
    except TypeError:
        print("font_size must be an integer")


if __name__ == '__main__':
    try:
        import sys
        sys.path.insert(0, os.path.join(os.getcwd(), '../demos/'))
        import guessing_game

        guessing_game.guessing_game()
    except ImportError:
        print("Could not find demo.")
