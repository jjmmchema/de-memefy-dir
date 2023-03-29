import os
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
        
        self.outerLayout = QtWidgets.QVBoxLayout()
        self.outerLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.outerLayout.setSpacing(20)

        self.inputLayout = QtWidgets.QHBoxLayout()
        self.inputLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.inputLayout.setSpacing(10)
        
        self.outputLayout = QtWidgets.QHBoxLayout()
        self.outputLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.outputLayout.setSpacing(10)

        self.inputFolderTxt = self.createLabel(400, 'Folder that contains the images to classify:', 'labelG', 'roundCorners')
        self.inputDirLabel = self.createLineEdit(350, 30, 'Select a folder...', 'general', 'dirEdit', 'roundCorners')
        self.inputDirLabel.installEventFilter(self)
        self.uploadDirBtn = self.createBtn(140, 30, 'Upload Folder', 'general','uploadBtn', 'roundCorners')
        self.uploadDirBtn.clicked.connect(partial(self.showUploadDirDialog, 'uploadDirBtn'))

        self.outputFolderTxt = self.createLabel(550, 'Folder to which the images will be moved after classification:', 'labelG', 'roundCorners')
        self.outputDirLabel = self.createLineEdit(350, 30, 'Select a folder...', 'general', 'dirEdit', 'roundCorners')
        self.outputDirLabel.installEventFilter(self)
        self.saveToDirBtn = self.createBtn(140, 30, 'Upload Folder', 'general','uploadBtn', 'roundCorners')
        self.saveToDirBtn.clicked.connect(partial(self.showUploadDirDialog, 'saveToDirBtn'))

        self.runBtn = self.createBtn(120, 30, 'Run', 'general', 'uploadBtn', 'roundCorners')
        self.runBtn.clicked.connect(self.runPrediction)

        centerAbs = Qt.AlignmentFlag.AlignCenter

        self.inputLayout.addWidget(self.inputDirLabel)
        self.inputLayout.addWidget(self.uploadDirBtn)

        self.outputLayout.addWidget(self.outputDirLabel)
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

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> bool:
        
        obj = None

        if source == self.inputDirLabel:
            obj = self.inputDirLabel
        if source == self.outputDirLabel:
            obj = self.outputDirLabel

        if isinstance(obj, QtWidgets.QLineEdit):
            if event.type() == QtCore.QEvent.Type.FocusIn:
                self.setClasses(obj, 'general', 'leClicked','roundCorners')
                obj.setPlaceholderText('')
                self.loadStyleSheet()

            elif event.type() == QtCore.QEvent.Type.FocusOut and obj.text() == '':
                self.setClasses(obj, 'general', 'dirEdit','roundCorners')
                obj.setPlaceholderText('Select a folder...')
                self.loadStyleSheet()
            
        
        return super(Window, self).eventFilter(source, event)

    def showUploadDirDialog(self, btnName: str):
        dirName = QtWidgets.QFileDialog.getExistingDirectory()
        if dirName:
            if btnName == 'uploadDirBtn':
                self.changeLabelTxt(self.inputDirLabel, dirName)
            elif btnName == 'saveToDirBtn':
                self.changeLabelTxt(self.outputDirLabel, dirName)
            
    def runPrediction(self):
        results = self.model.predict(self.inputDirLabel.text())
        self.organizeFilesInDir(results)

    def organizeFilesInDir(self, results: List[ImageContainer]) -> None:
        dirName = self.outputDirLabel.text()
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

    def changeLabelTxt(self, label: QtWidgets.QLabel, txt: str):
        label.setFocus()
        label.setText(txt)

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

    def setClasses(self, w: QtWidgets.QWidget, *classes):
        if classes:
            w.setProperty('class', ' '.join(classes))
        return w

    def loadStyleSheet(self, path: str="src/styles/styles.css") -> None:
        with open(path, "r") as f:
            self.setStyleSheet(f.read())

    def loadFonts(self):
        id = QtGui.QFontDatabase.addApplicationFont('fonts/Nunito-Regular.ttf')     # Nunito
        id2 = QtGui.QFontDatabase.addApplicationFont('fonts/Nunito-SemiBold.ttf')   # Nunito SemiBold

        # families = QtGui.QFontDatabase.applicationFontFamilies(id2)