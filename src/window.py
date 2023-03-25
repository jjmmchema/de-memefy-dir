from model import Model

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.model: Model = Model('trained_model_3.onnx')
        
        self.setWindowTitle("De-memefy")
        self.setGeometry(60, 60, 600, 600)
        self.loadFonts()
        self.loadStyleSheet()
        
        self.outerLayout = QtWidgets.QVBoxLayout()
        self.outerLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.btnsLayout = QtWidgets.QHBoxLayout()
        self.btnsLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.btnsLayout.setSpacing(10)

        self.uploadFileBtn = self.createBtn('Upload File', 125, 30, 'uploadBtn')
        self.uploadFileBtn.clicked.connect(self.showUploadFileDialog)
        
        self.uploadDirBtn = self.createBtn('Upload Folder', 125, 30, 'uploadBtn')
        self.uploadDirBtn.clicked.connect(self.showUploadDirDialog)

        self.btnsLayout.addWidget(self.uploadFileBtn)
        self.btnsLayout.addWidget(self.uploadDirBtn)

        self.outerLayout.addLayout(self.btnsLayout)

        w = QtWidgets.QWidget()
        w.setLayout(self.outerLayout)
        self.setCentralWidget(w)
        self.show()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def showUploadFileDialog(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName()[0]
        try:
            self.model.predict(fileName)
        except:
            pass

    def showUploadDirDialog(self):
        dirName = QtWidgets.QFileDialog.getExistingDirectory()
        self.model.predictDir(dirName)

    def createBtn(self, text: str, w: int, h: int, *classes):
        btn = QtWidgets.QPushButton(text)
        btn.setFixedSize(w, h)
        if classes:
            btn.setProperty('class', ' '.join(classes))
        return btn

    def loadStyleSheet(self, path: str="src/styles/styles.css") -> None:
        with open(path, "r") as f:
            self.setStyleSheet(f.read())

    def loadFonts(self):
        id = QtGui.QFontDatabase.addApplicationFont('fonts/Nunito-Regular.ttf')     # Nunito
        id2 = QtGui.QFontDatabase.addApplicationFont('fonts/Nunito-SemiBold.ttf')   # Nunito SemiBold

        # families = QtGui.QFontDatabase.applicationFontFamilies(id2)