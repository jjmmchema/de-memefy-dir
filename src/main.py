import sys

from window import Window

from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    App = QApplication(sys.argv)
    Window = Window()
    sys.exit(App.exec())
