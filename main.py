import sys
from PyQt5 import QtWidgets

from src.forms_code.main_form import MainForm


def main() -> None:
    application = QtWidgets.QApplication(sys.argv)
    application_form = MainForm()
    application_form.show()
    sys.exit(application.exec_())

    # Comment # 1

if __name__ == "__main__":
    main()