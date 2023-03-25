import os
import numpy as np
import onnxruntime as oxr

from PIL import Image
from pathlib import Path

class Model():

    __modelsDir = Path('models').absolute()
    __imgExtensions = ('png', 'jpg', 'jpeg', 'bmp')

    def __init__(self, fileName : str) -> None:
        self.__modelPath = self.__modelsDir / fileName

        if not self.__modelPath.exists():
            # Error, file doesn't exist
            pass

        self.__modelSession = oxr.InferenceSession(str(self.__modelPath))

    def loadImageToArray(self, imgPath: str) -> np.ndarray:
        img = Image.open(imgPath)
        img = img.resize((255, 255))
        
        imgArr = np.asarray(img, dtype=np.float32)
        imgArr = imgArr.transpose((2, 0, 1)) / 255
        # imgArr = imgArr[None, :] 

        return imgArr

    def loadImgsInDir(self, dirName: str):
        imgs = []
        for path, _, files in os.walk(dirName):
            for f in files:
                filePath = os.path.abspath(os.path.join(path, f))
                if filePath.lower().endswith(self.__imgExtensions):
                    imgs.append(self.loadImageToArray(filePath))
        return np.array(imgs)

    def predict(self, dirPath: str):
        imgArr = self.loadImgsInDir(dirPath)
        input = {self.__modelSession.get_inputs()[0].name: imgArr}
        res = self.__modelSession.run(None, input)
        print(res)