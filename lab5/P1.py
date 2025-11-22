# importa modulele necesare
import os
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from PyQt5.uic import loadUi
from PyQt5 import QtCore
import sysv_ipc

# functie pentru debug
def debug_trace(ui=None):
    from pdb import set_trace
    QtCore.pyqtRemoveInputHook()
    set_trace()
    QtCore.pyqtRestoreInputHook()

# clasa principala pentru conversia html
class HTMLConverter(QWidget):
    # seteaza directorul radacina
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        super(HTMLConverter, self).__init__()
        # initializeaza variabila pentru continutul html
        self.html_content = None
        # incarca interfata grafica din fisierul ui
        ui_path = os.path.join(self.ROOT_DIR, 'html_converter.ui')
        loadUi(ui_path, self)
        # conecteaza butoanele la functiile corespunzatoare
        self.browse_btn.clicked.connect(self.browse)
        self.convert_HTML_btn.clicked.connect(self.convert_to_html)
        self.send_to_C_btn.clicked.connect(self.send_to_c_program)
        # initializeaza calea fisierului
        self.file_path = None
        # creeaza coada de mesaje
        self.message_queue = sysv_ipc.MessageQueue(-402570804)

    # functie pentru selectarea fisierului
    def browse(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        # deschide dialogul pentru selectarea fisierului
        file, _ = QFileDialog.getOpenFileName(self, caption='Select file', directory='', filter="Text Files (*.txt)", options=options)
        if file:
            # salveaza calea fisierului selectat
            self.file_path = file
            # afiseaza calea in interfata
            self.path_line_edit.setText(file)
            print(file)

    # functie pentru conversia in html
    def convert_to_html(self):
        if self.file_path:
            # citeste liniile din fisier
            with open(self.file_path, 'r') as file:
                lines = file.readlines()

            # extrage titlul si paragrafele
            title = lines[0].strip()
            paragraphs = [line.strip() for line in lines[1:] if line.strip()]

            # construieste continutul html
            html_content = f"<html>\n<head>\n<title>{title}</title>\n</head>\n<body>\n\n\n"
            for paragraph in paragraphs:
                html_content += f"<p>{paragraph}</p>\n"
            html_content += "\n</body>\n</html>"

            # salveaza continutul html
            self.html_content = html_content

    # functie pentru trimiterea continutului la programul c
    def send_to_c_program(self):
            if hasattr(self, 'html_content'):
                # trimite continutul html prin coada de mesaje
                self.message_queue.send(self.html_content.encode('utf-8'))


# punctul de intrare in program
if __name__ == '__main__':
    # creeaza aplicatia qt
    app = QApplication(sys.argv)
    # creeaza fereastra principala
    window = HTMLConverter()
    # afiseaza fereastra
    window.show()
    # ruleaza bucla principala a aplicatiei
    sys.exit(app.exec_())