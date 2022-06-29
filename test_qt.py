import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QWidget, QToolTip, QPushButton


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        QToolTip.setFont(QFont('SansSerif', 10))

        self.setToolTip('This is a <b>QWidget</b> widget')

        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.move(50, 50)
        btn.clicked.connect(lambda: print("asd"))

        self.setGeometry(300, 300, 600, 600)
        self.setWindowTitle('Tooltips')
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
