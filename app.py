import sys
from PyQt6.QtWidgets import QApplication
from ui import ImageClassifierApp

def main():
    app = QApplication(sys.argv)
    ex = ImageClassifierApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
