import sys
import pathlib
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QFrame, QGraphicsView, QGraphicsScene, QSlider
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import uic
import qimage2ndarray
import cv2

# main.py
from widgets import Images, Filter, Adjust, Ai, ResizableRubberBand

# Your main application code

# Replace these imports with your actual widget implementations
from widgets import Images, Filter, Adjust, Ai, ResizableRubberBand

class Start(QWidget):
    def __init__(self):
        super().__init__()
        ui_path = f"{pathlib.Path(__file__).parent.absolute()}/ui/startup.ui"
        icon_path = f"{pathlib.Path(__file__).parent.absolute()}/icon/icon.png"
        try:
            uic.loadUi(ui_path, self)
        except FileNotFoundError:
            print("Error: The file 'startup.ui' does not exist.")
            sys.exit(1)
        self.setWindowIcon(QIcon(icon_path))

        self.button = self.findChild(QPushButton, "browse")
        self.button.clicked.connect(self.on_click)
        self.files, self.main_window = None, None

    def on_click(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Choose Image File", "",
                                                "Image Files (*.jpg *.png *.jpeg *.ico);;All Files (*)")
        if files:
            self.files = files
            self.close()
            self.main_window = Main(self.files) 
            self.main_window.show()

class Main(QWidget):
    def __init__(self, files):
        super().__init__()
        ui_path = f"{pathlib.Path(__file__).parent.absolute()}/ui/main.ui"
        icon_path = f"{pathlib.Path(__file__).parent.absolute()}/icon/icon.png"
        try:
            uic.loadUi(ui_path, self)
        except FileNotFoundError:
            print("Error: The file 'main.ui' does not exist.")
            sys.exit(1)
        self.setWindowIcon(QIcon(icon_path))
        self.move(120, 100)
        self.img_list, self.rb = [], None
        for f in files:
            self.img_list.append(Images(f))
        self.img_id = 0
        self.img_class = self.img_list[self.img_id]
        self.img = QPixmap(qimage2ndarray.array2qimage(cv2.cvtColor(self.img_class.img, cv2.COLOR_BGR2RGB)))

        # find widgets and connect them
        self.vbox = self.findChild(QVBoxLayout, "vbox")
        self.vbox1 = self.findChild(QVBoxLayout, "vbox1")
        self.base_frame = self.findChild(QFrame, "base_frame")
        self.filter_btn = self.findChild(QPushButton, "filter_btn")
        self.filter_btn.clicked.connect(self.filter_frame)
        self.adjust_btn = self.findChild(QPushButton, "adjust_btn")
        self.adjust_btn.clicked.connect(self.adjust_frame)
        self.ai_btn = self.findChild(QPushButton, "ai_btn")
        self.ai_btn.clicked.connect(self.ai_frame)
        self.save_btn = self.findChild(QPushButton, "save_btn")
        self.save_btn.clicked.connect(self.click_save)
        self.slider = self.findChild(QSlider, "slider")
        self.slider.setParent(None)

        # display img
        self.gv = self.findChild(QGraphicsView, "gv")
        self.scene = QGraphicsScene()
        self.scene_img = self.scene.addPixmap(self.img)
        self.gv.setScene(self.scene)

        # zoom in
        self.zoom_moment = False
        self._zoom = 0

        # misc
        self.rotate_value, self.brightness_value, self.contrast_value, self.saturation_value = 0, 0, 1, 0
        self.flip = [False, False]
        self.zoom_factor = 1

    def update_img(self, movable=False):
        self.img = QPixmap(qimage2ndarray.array2qimage(cv2.cvtColor(self.img_class.img, cv2.COLOR_BGR2RGB)))
        self.scene.removeItem(self.scene_img)
        self.scene_img = self.scene.addPixmap(self.img)
        if movable:
            self.scene_img.setFlag(QGraphicsItem.ItemIsMovable)
        else:
            self.fitInView()

    def get_zoom_factor(self):
        return self.zoom_factor

    def filter_frame(self):
        filter_frame = Filter(self)
        self.base_frame.setParent(None)
        self.vbox.addWidget(filter_frame.frame)

    def adjust_frame(self):
        adjust_frame = Adjust(self)
        self.base_frame.setParent(None)
        self.vbox.addWidget(adjust_frame.frame)

    def ai_frame(self):
        self.rb = ResizableRubberBand(self)
        ai_frame = Ai(self)
        self.base_frame.setParent(None)
        self.vbox.addWidget(ai_frame.frame)

    def click_save(self):
        try:
            file, _ = QFileDialog.getSaveFileName(self, 'Save File', f"{self.img_class.img_name}."
                                                                     f"{self.img_class.img_format}",
                                                  "Image Files (*.jpg *.png *.jpeg *.ico);;All Files (*)")
            self.img_class.save_img(file)
        except Exception:
            pass

    def wheelEvent(self, event):
        if self.zoom_moment:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.gv.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def fitInView(self):
        rect = QRectF(self.img.rect())
        if not rect.isNull():
            self.gv.setSceneRect(rect)

            unity = self.gv.transform().mapRect(QRectF(0, 0, 1, 1))
            self.gv.scale(1 / unity.width(), 1 / unity.height())
            view_rect = self.gv.viewport().rect()
            scene_rect = self.gv.transform().mapRect(rect)
            factor = min(view_rect.width() / scene_rect.width(),
                         view_rect.height() / scene_rect.height())
            self.gv.scale(factor, factor)
            self._zoom = 0
            self.zoom_factor = factor


def main():
    app = QApplication(sys.argv)
    window = Start()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
