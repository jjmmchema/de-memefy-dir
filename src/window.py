import shutil

from typing import List
from pathlib import Path
from functools import partial

from model import Model
from imageContainer import ImageContainer

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
        
        # -------- Layouts --------
        # Create the layout that will contain all other layouts
        self.outerLayout = QtWidgets.QVBoxLayout()
        self.outerLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.outerLayout.setSpacing(20)

        # Layout that will contain all widgets associated with the input
        self.inputLayout = QtWidgets.QHBoxLayout()
        self.inputLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.inputLayout.setSpacing(10)
        
        # Layout that will contain all widgets associated with the output
        self.outputLayout = QtWidgets.QHBoxLayout()
        self.outputLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.outputLayout.setSpacing(10)

        # -------- Labels --------
        # Both just contain the specified test
        self.inputFolderTxt = self.createLabel(400, 'Folder that contains the images to classify:', 'labelG', 'roundCorners')
        self.outputFolderTxt = self.createLabel(550, 'Folder to which the images will be moved after classification:', 'labelG', 'roundCorners')

        # -------- Line Edits --------
        # Line Edits to allow the user to type the path of the input and output folder, respectively.
        # Alternatively, they can show the path of the folder selected through one of the buttons.
        self.inputDirLEdit = self.createLineEdit(350, 30, 'Select a folder...', 'general', 'dirEdit', 'roundCorners')
        self.outputDirLEdit = self.createLineEdit(350, 30, 'Select a folder...', 'general', 'dirEdit', 'roundCorners')

        # Allow self (Window in this case) to implement a function for filtering events that
        # involve any of these Line Edits.
        self.inputDirLEdit.installEventFilter(self) 
        self.outputDirLEdit.installEventFilter(self)

        # -------- Buttons --------
        self.uploadDirBtn = self.createBtn(140, 30, 'Upload Folder', 'general','uploadBtn', 'roundCorners')
        self.saveToDirBtn = self.createBtn(140, 30, 'Upload Folder', 'general','uploadBtn', 'roundCorners')
        self.runBtn = self.createBtn(120, 30, 'Run', 'general', 'uploadBtn', 'roundCorners')

        # Connect each button to it's respective function
        self.uploadDirBtn.clicked.connect(partial(self.showUploadDirDialog, 'uploadDirBtn'))
        self.saveToDirBtn.clicked.connect(partial(self.showUploadDirDialog, 'saveToDirBtn'))
        self.runBtn.clicked.connect(self.runPrediction)

        # -------- Add widgets to GUI --------
        centerAbs = Qt.AlignmentFlag.AlignCenter   # For the sake of less typing

        self.inputLayout.addWidget(self.inputDirLEdit)
        self.inputLayout.addWidget(self.uploadDirBtn)

        self.outputLayout.addWidget(self.outputDirLEdit)
        self.outputLayout.addWidget(self.saveToDirBtn)

        self.outerLayout.addWidget(self.inputFolderTxt, alignment=centerAbs)        
        self.outerLayout.addLayout(self.inputLayout)
        self.outerLayout.addWidget(self.outputFolderTxt, alignment=centerAbs)
        self.outerLayout.addLayout(self.outputLayout)
        self.outerLayout.addWidget(self.runBtn, alignment=centerAbs)

        w = QtWidgets.QWidget()
        w.setLayout(self.outerLayout)
        self.setCentralWidget(w)
        self.setFocus()
        self.show()

    # -------- Main functionality functions --------

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> bool:   # Override
        """
            Function that catches and handles all events involving any
            of the QObject that has had the method _installEventFilter(self)_
            invoked. 
            self just means that this object, Window, will be the one handling the events.
        """
        obj = None

        if source == self.inputDirLEdit:
            obj = self.inputDirLEdit
        if source == self.outputDirLEdit:
            obj = self.outputDirLEdit

        if isinstance(obj, QtWidgets.QLineEdit):
            if event.type() == QtCore.QEvent.Type.FocusIn:
                self.setClasses(obj, 'general', 'leClicked','roundCorners')
                obj.setPlaceholderText('')
                self.loadStyleSheet()

            elif event.type() == QtCore.QEvent.Type.FocusOut and obj.text() == '':
                self.setClasses(obj, 'general', 'dirEdit','roundCorners')
                obj.setPlaceholderText('Select a folder...')
                self.loadStyleSheet()
            
        return super(Window, self).eventFilter(source, event)   # Call super to keep the functionality inherited from QMainWindow

    def showUploadDirDialog(self, btnName: str):
        dirName = QtWidgets.QFileDialog.getExistingDirectory()
        if dirName:
            if btnName == 'uploadDirBtn':
                self.changeLabelTxt(self.inputDirLEdit, dirName)
            elif btnName == 'saveToDirBtn':
                self.changeLabelTxt(self.outputDirLEdit, dirName)
            
    def runPrediction(self):
        if self.inputDirLEdit.text() and self.outputDirLEdit.text():
            results = self.model.predict(self.inputDirLEdit.text())
            self.organizeFilesInDir(results)
        else:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle('Warning')
            dlg.setText('Please fill out all the fields')
            dlg.exec()

    def organizeFilesInDir(self, results: List[ImageContainer]) -> None:
        dirName = self.outputDirLEdit.text()
        if not dirName:
            return
    
        memesDir = Path(dirName) / 'memes'
        othersDir = Path(dirName) / 'others'

        memesDir.mkdir(exist_ok=True)
        othersDir.mkdir(exist_ok=True)

        for container in results:
            if container.imgLabel == 'Meme':
                shutil.move(container.imgPath, memesDir / container.imgName)
            elif container.imgLabel == 'Other':
                shutil.move(container.imgPath, othersDir / container.imgName)

    # -------- Widget-creating/modifying functions --------

    def createLabel(self, w:int, text: str, *classes):
        lb = QtWidgets.QLabel(text)
        lb.setFixedWidth(w)
        lb.setFixedHeight(35)
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return self.setClasses(lb, *classes)

    def createBtn(self, w: int, h: int, text: str, *classes):
        btn = QtWidgets.QPushButton(text)
        btn.setFixedSize(w, h)
        return self.setClasses(btn, *classes)
    
    def createLineEdit(self, w: int, h:int, placeHolder: str= '', *classes):
        le = QtWidgets.QLineEdit()
        le.setFixedSize(w, h)
        le.setPlaceholderText(placeHolder)
        return self.setClasses(le, *classes)

    def changeLabelTxt(self, label: QtWidgets.QLabel, txt: str):
        label.setFocus()
        label.setText(txt)

    def setClasses(self, w: QtWidgets.QWidget, *classes):
        if classes:
            w.setProperty('class', ' '.join(classes))
        return w

    # -------- Function for key pressing events --------

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:   # Override
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    # -------- Loader functions --------

    def loadStyleSheet(self, path: str="src/styles/styles.css") -> None:
        with open(path, "r") as f:
            self.setStyleSheet(f.read())

    def loadFonts(self):
        id = QtGui.QFontDatabase.addApplicationFont('fonts/Nunito-Regular.ttf')     # Nunito
        id2 = QtGui.QFontDatabase.addApplicationFont('fonts/Nunito-SemiBold.ttf')   # Nunito SemiBold

        # families = QtGui.QFontDatabase.applicationFontFamilies(id2)