import numpy as np

class ImageContainer():

    def __init__(self, imgPath: str, imgArr: np.ndarray):
        self.imgPath = imgPath
        self.imgArr = imgArr
        self.imgLabel = None

    def __str__(self):
        print(
            f'''imgPath: {self.imgPath},
                Label {self.imgLabel}'''
        )