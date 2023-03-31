import numpy as np

from pathlib import Path

class ImageContainer():

    def __init__(self, imgPath: str, imgArr: np.ndarray):
        self.imgPath = Path(imgPath)
        self.imgArr = imgArr
        self.imgName = self.imgPath.name
        self.imgLabel = None
        print(self)

    def __str__(self) -> str:
        return f'''Name: {self.imgName}
                   Path: {self.imgPath},
                   Label {self.imgLabel}'''
    