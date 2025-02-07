#!/usr/bin/env python

# main.py
import sys
from PyQt5.QtWidgets import QApplication
from main_window import RubiksWindow

def main():
    app = QApplication(sys.argv)
    window = RubiksWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
