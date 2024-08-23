import sys
import cv2
import qimage2ndarray
import pathlib
from copy import deepcopy
import numpy as np
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QImage
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QPushButton, QVBoxLayout, QMessageBox, QColorDialog, QSlider


# widgets.py
class Images:
    def __init__(self):
        pass

    # Other methods for Images class

class Filter(QWidget):
    def __init__(self, main):
        super().__init__()
        uic.loadUi(f"{pathlib.Path(__file__).parent.absolute()}/ui/filter_frame.ui", self)
        self.img_class = main.img_class
        self.update_img = main.update_img
        self.base_frame = main.base_frame
        self.vbox = main.vbox

        self.frame = self.findChild(QFrame, "frame")
        self.contrast_btn = self.findChild(QPushButton, "contrast_btn")
        self.sharpen_btn = self.findChild(QPushButton, "sharpen_btn")
        self.cartoon_btn = self.findChild(QPushButton, "cartoon_btn")
        self.cartoon_btn1 = self.findChild(QPushButton, "cartoon_btn2")
        self.invert_btn = self.findChild(QPushButton, "invert_btn")
        self.bypass_btn = self.findChild(QPushButton, "bypass_btn")

        self.y_btn = self.findChild(QPushButton, "y_btn")
        self.y_btn.setIcon(QIcon(f"{pathlib.Path(__file__).parent.absolute()}/icon/check.png"))
        self.y_btn.setStyleSheet("QPushButton{border: 0px solid;}")
        self.y_btn.setIconSize(QSize(60, 60))

        self.n_btn = self.findChild(QPushButton, "n_btn")
        self.n_btn.setIcon(QIcon(f"{pathlib.Path(__file__).parent.absolute()}/icon/cross.png"))
        self.n_btn.setStyleSheet("QPushButton{border: 0px solid;}")
        self.n_btn.setIconSize(QSize(60, 60))

        self.y_btn.clicked.connect(self.click_y)
        self.n_btn.clicked.connect(self.click_n)
        self.contrast_btn.clicked.connect(self.click_contrast)
        self.sharpen_btn.clicked.connect(self.click_sharpen)
        self.cartoon_btn.clicked.connect(self.click_cartoon)
        self.cartoon_btn1.clicked.connect(self.click_cartoon1)
        self.invert_btn.clicked.connect(self.click_invert)
        self.bypass_btn.clicked.connect(self.click_bypass)

    def click_contrast(self):
        self.img_class.auto_contrast()
        self.update_img()

    def click_sharpen(self):
        self.img_class.auto_sharpen()
        self.update_img()

    def click_cartoon(self):
        self.img_class.auto_cartoon()
        self.update_img()

    def click_cartoon1(self):
        self.img_class.auto_cartoon(1)
        self.update_img()

    def click_invert(self):
        self.img_class.auto_invert()
        self.update_img()

    def click_bypass(self):
        self.img_class.bypass_censorship()
        self.update_img()

    def click_y(self):
        self.frame.setParent(None)
        self.img_class.img_copy = deepcopy(self.img_class.img)
        self.img_class.grand_img_copy = deepcopy(self.img_class.img)
        self.vbox.addWidget(self.base_frame)

    def click_n(self):
        if not np.array_equal(self.img_class.grand_img_copy, self.img_class.img):
            msg = QMessageBox.question(self, "Cancel edits", "Confirm to discard all the changes?", QMessageBox.Yes | QMessageBox.No)
            if msg != QMessageBox.Yes:
                return
        self.frame.setParent(None)
        self.img_class.grand_reset()
        self.update_img()
        self.vbox.addWidget(self.base_frame)


class Adjust(QWidget):
    def __init__(self, main):
        super().__init__()
        uic.loadUi(f"{pathlib.Path(__file__).parent.absolute()}/ui/adjust_frame.ui", self)
        self.get_zoom_factor = main.get_zoom_factor
        self.img_class = main.img_class
        self.update_img = main.update_img
        self.base_frame = main.base_frame
        self.rb = main.rb
        self.vbox = main.vbox
        self.flip = main.flip
        self.zoom_factor = main.zoom_factor
        self.zoom_moment = main.zoom_moment
        self.slider = main.slider
        self.gv = main.gv
        self.vbox1 = main.vbox1
        self.start_detect = False

        self.frame = self.findChild(QFrame, "frame")
        self.crop_btn = self.findChild(QPushButton, "crop_btn")
        self.rotate_btn = self.findChild(QPushButton, "rotate_btn")
        self.brightness_btn = self.findChild(QPushButton, "brightness_btn")
        self.contrast_btn = self.findChild(QPushButton, "contrast_btn")
        self.saturation_btn = self.findChild(QPushButton, "saturation_btn")
        self.mask_btn = self.findChild(QPushButton, "mask_btn")

        self.y_btn = self.findChild(QPushButton, "y_btn")
        self.y_btn.setIcon(QIcon(f"{pathlib.Path(__file__).parent.absolute()}/icon/check.png"))
        self.y_btn.setStyleSheet("QPushButton{border: 0px solid;}")
        self.y_btn.setIconSize(QSize(60, 60))

        self.n_btn = self.findChild(QPushButton, "n_btn")
        self.n_btn.setIcon(QIcon(f"{pathlib.Path(__file__).parent.absolute()}/icon/cross.png"))
        self.n_btn.setStyleSheet("QPushButton{border: 0px solid;}")
        self.n_btn.setIconSize(QSize(60, 60))

        self.y_btn.clicked.connect(self.click_y)
        self.n_btn.clicked.connect(self.click_n)
        self.crop_btn.clicked.connect(self.click_crop)
        self.rotate_btn.clicked.connect(lambda: self.click_crop(rotate=True))
        self.brightness_btn.clicked.connect(lambda: self.click_brightness())
        self.contrast_btn.clicked.connect(lambda: self.click_brightness(mode=1))
        self.saturation_btn.clicked.connect(lambda: self.click_brightness(mode=2))
        self.mask_btn.clicked.connect(lambda: self.click_brightness(mode=3))

    def click_crop(self, rotate=False):
        def click_y1():
            self.rb.update_dim()
            if rotate:
                self.img_class.rotate_img(self.rotate_value, crop=True, flip=self.flip)
                self.img_class.crop_img(int(self.rb.top * 2 / self.zoom_factor),
                                        int(self.rb.bottom * 2 / self.zoom_factor),
                                        int(self.rb.left * 2 / self.zoom_factor),
                                        int(self.rb.right * 2 / self.zoom_factor))
            else:
                self.img_class.reset(self.flip)
                self.img_class.crop_img(int(self.rb.top / self.zoom_factor),
                                        int(self.rb.bottom / self.zoom_factor),
                                        int(self.rb.left / self.zoom_factor),
                                        int(self.rb.right / self.zoom_factor))

            self.update_img()
            self.zoom_moment = False

            self.img_class.img_copy = deepcopy(self.img_class.img)
            self.slider.setParent(None)
            self.slider.valueChanged.disconnect()
            crop_frame.frame.setParent(None)
            self.vbox.addWidget(self.frame)
            self.rb.close()

        def click_n1():
            if not np.array_equal(img_copy, self.img_class.img):
                msg = QMessageBox.question(self, "Cancel edits", "Confirm to discard all the changes?", QMessageBox.Yes | QMessageBox.No)
                if msg != QMessageBox.Yes:
                    return
            self.img_class.reset()
            self.update_img()
            self.zoom_moment = False

            self.slider.setParent(None)
            self.slider.valueChanged.disconnect()
            crop_frame.frame.setParent(None)
            self.vbox.addWidget(self.frame)
            self.rb.close()

        def change_slide():
            self.rotate_value = self.slider.value()
            self.slider.setValue(self.rotate_value)

            self.img_class.rotate_img(self.rotate_value)

            self.rb.setGeometry(int(self.img_class.left * self.zoom_factor),
                                int(self.img_class.top * self.zoom_factor),
                                int((self.img_class.right - self.img_class.left) * self.zoom_factor),
                                int((self.img_class.bottom - self.img_class.top) * self.zoom_factor))

            self.rb.update_dim()
            self.update_img(True)

        def add_90():
            if self.rotate_value <= 270:
                self.rotate_value += 90
            else:
                self.rotate_value = 360
            self.slider.setValue(self.rotate_value)
            change_slide()

        def subtract_90():
            if self.rotate_value >= 90:
                self.rotate_value -= 90
            else:
                self.rotate_value = 0
            self.slider.setValue(self.rotate_value)
            change_slide()

        def vertical_flip():
            nonlocal vflip_ct
            self.img_class.img = cv2.flip(self.img_class.img, 0)
            if rotate:
                self.update_img(True)
            else:
                self.update_img()
            vflip_ct += 1
            self.flip[0] = vflip_ct % 2 == 1

        def horizontal_flip():
            nonlocal hflip_ct
            self.img_class.img = cv2.flip(self.img_class.img, 1)
            if rotate:
                self.update_img(True)
            else:
                self.update_img()
            hflip_ct += 1
            self.flip[1] = hflip_ct % 2 == 1

        crop_frame = Crop()
        crop_frame.n_btn.clicked.connect(click_n1)
        crop_frame.y_btn.clicked.connect(click_y1)

        self.frame.setParent(None)
        self.vbox.addWidget(crop_frame)
        crop_frame.show()

        self.slider.setMinimum(-180)
        self.slider.setMaximum(180)
        self.slider.setValue(0)
        self.slider.setOrientation(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(90)
        self.slider.setSingleStep(10)
        self.slider.setPageStep(10)
        self.slider.valueChanged.connect(change_slide)

        vflip_ct = 0
        hflip_ct = 0
        self.flip = [0, 0]

        self.findChild(QPushButton, "flip_v").clicked.connect(vertical_flip)
        self.findChild(QPushButton, "flip_h").clicked.connect(horizontal_flip)

    def click_brightness(self, mode=0):
        def click_y1():
            self.img_class.reset()
            self.img_class.adjust_brightness(self.value, mode)
            self.update_img()
            self.img_class.img_copy = deepcopy(self.img_class.img)
            self.slider.setParent(None)
            self.slider.valueChanged.disconnect()
            brightness_frame.frame.setParent(None)
            self.vbox.addWidget(self.frame)

        def click_n1():
            if not np.array_equal(img_copy, self.img_class.img):
                msg = QMessageBox.question(self, "Cancel edits", "Confirm to discard all the changes?", QMessageBox.Yes | QMessageBox.No)
                if msg != QMessageBox.Yes:
                    return
            self.img_class.reset()
            self.update_img()
            self.slider.setParent(None)
            self.slider.valueChanged.disconnect()
            brightness_frame.frame.setParent(None)
            self.vbox.addWidget(self.frame)

        def change_slide():
            self.value = self.slider.value()
            if mode == 0:
                self.img_class.adjust_brightness(self.value)
            elif mode == 1:
                self.img_class.adjust_contrast(self.value)
            elif mode == 2:
                self.img_class.adjust_saturation(self.value)
            else:
                self.img_class.adjust_mask(self.value)

            self.update_img()

        brightness_frame = Brightness()
        brightness_frame.y_btn.clicked.connect(click_y1)
        brightness_frame.n_btn.clicked.connect(click_n1)

        self.frame.setParent(None)
        self.vbox.addWidget(brightness_frame)
        brightness_frame.show()

        self.slider.setMinimum(-100)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.slider.setOrientation(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(10)
        self.slider.valueChanged.connect(change_slide)

        img_copy = deepcopy(self.img_class.img)


class Brightness(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(f"{pathlib.Path(__file__).parent.absolute()}/ui/brightness_frame.ui", self)
        self.frame = self.findChild(QFrame, "frame")
        self.y_btn = self.findChild(QPushButton, "y_btn")
        self.n_btn = self.findChild(QPushButton, "n_btn")
        self.y_btn.clicked.connect(self.click_y)
        self.n_btn.clicked.connect(self.click_n)

    def click_y(self):
        self.frame.setParent(None)
        self.close()

    def click_n(self):
        self.frame.setParent(None)
        self.close()


class Crop(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(f"{pathlib.Path(__file__).parent.absolute()}/ui/crop_frame.ui", self)
        self.frame = self.findChild(QFrame, "frame")
        self.y_btn = self.findChild(QPushButton, "y_btn")
        self.n_btn = self.findChild(QPushButton, "n_btn")
        self.y_btn.clicked.connect(self.click_y)
        self.n_btn.clicked.connect(self.click_n)

    def click_y(self):
        self.frame.setParent(None)
        self.close()

    def click_n(self):
        self.frame.setParent(None)
        self.close()
