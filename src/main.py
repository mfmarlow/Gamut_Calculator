import sys

from colour import RGB_COLOURSPACES
import colour.utilities
from Gamut import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import colour
import user_input


class Gamut_win(QtWidgets.QMainWindow):
    def __init__(self):
        super(Gamut_win, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Radio button initial settings
        self.ui.rB_table_s.setChecked(True)
        self.ui.groupBox_import_sample.setEnabled(False)
        # Radio button initial settings
        self.ui.pB_calculate.clicked.connect(self.calculate)
        self.ui.rB_table_s.toggled.connect(self.f_table_s)
        self.ui.rB_file_s.toggled.connect(self.f_file_s)
        self.ui.pb_browse_sample.clicked.connect(self.f_browse_sample)

        self.ui.pb_file_directory_selector.clicked.connect(self.select_file_directory)
        self.ui.actionAbout.triggered.connect(self.about)
        self.table_cell_error = False

    def about(self):
        msg = QtWidgets.QMessageBox()
        msg.setTextFormat(Qt.RichText)
        # msg.about(self, "About", "Gamut Calculator\nVersion: 1.0\n\nNo rights reserved at all cCc\n<a href='http://google.com/'>Google</a>")
        icon = QIcon()
        icon.addPixmap(QPixmap("assets/icon.jpg"), QIcon.Normal, QIcon.Off)
        msg.setWindowIcon(icon)
        msg.setWindowTitle("About")
        msg.setIconPixmap(QPixmap("assets/icon.jpg"))
        msg.setText('<p><span style="color:#0000a0"><span style="font-size:22px">Gamut Calculator</span></span><br><span style="font-size:15px">Version 1.0</span></p><p><span style="font-size:15px">Written in Python by using open source modules <br>by <br>Emre Beşkazak</span></p><p><span style="font-size:15px">Source code:</span><br><a href="https://github.com/emrebeskazak/Gamut_Calculator">GitHub</a></p>')
        x = msg.exec_()

    def f_browse_sample(self):
        self.ui.le_browse_sample.setText(QFileDialog.getOpenFileName()[0])

    def f_browse_sample_filter(self):
        self.ui.le_browse_sample_filter.setText(
            QFileDialog.getOpenFileName()[0])

    def select_file_directory(self):
        self.ui.le_file_directory.setText(QFileDialog.getExistingDirectory())

    def f_table_s(self):
        if self.sender().isChecked():
            self.ui.le_sample_name.setEnabled(True)
            self.ui.tW_sample.setEnabled(True)
            self.ui.groupBox_import_sample.setEnabled(False)

    def f_file_s(self):
        if self.sender().isChecked():
            self.ui.le_sample_name.setEnabled(False)
            self.ui.tW_sample.setEnabled(False)
            self.ui.groupBox_import_sample.setEnabled(True)

    def load_table(self, clrspace):
        table_row = 0
        for item in RGB_COLOURSPACES[clrspace].primaries:
            item = (item)
            table_row += 1

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            if self.ui.tW_sample.hasFocus():
                self.ui.tW_sample.setItem(self.ui.tW_sample.currentRow(), self.ui.tW_sample.currentColumn(), QTableWidgetItem(""))

    ##
    # THE METHOD FOR CALCULATIONS BASED ON THE COORDINATES ENTERED INTO TABLE
    ##
    def calculate(self):

        samples = user_input.get_colorspace_input(self)
        print(samples)

        for sample in samples:
            sample_name = sample[0]
            sample_r = np.array([float(sample[1]), float(sample[2])])
            sample_g = np.array([float(sample[3]), float(sample[4])])
            sample_b = np.array([float(sample[5]), float(sample[6])])
            sample = np.array([sample_r, sample_g, sample_b])
            if not self.table_cell_error:

                # Create the background image
                figure = plt.figure(figsize=(10, 11))
                background_axes = figure.add_axes([0.03, -0.025, 0.962, 0.962])
                image = mpimg.imread("assets/1080px-CIE_1976_UCS.png")
                background_axes.imshow(image)
                background_axes.axis('off')
                # colour.plotting.plot_chromaticity_diagram_CIE1976UCS(axes=axes, transparent_background=False)

                # Add axes for plotting the user input points
                axes = figure.add_axes([0.0062, -0.0028, 1.01, 0.92], frame_on=False)
                axes.axis("off")

                # Set title and subtitle
                axes.set_title('Chromaticity Diagram', y=1.021, fontsize=42, fontweight='bold')
                plt.text(0.5, 0.982, sample_name, ha='center', va='center', transform=axes.transAxes, fontsize=30)

                # Adjust subplot parameters to create more space around the plot
                plt.subplots_adjust(left=0.07, right=0.9, top=0.9, bottom=0.07)

                # Set the x and y axis limits
                axes.set_xlim(-0.05, 0.65)
                axes.set_ylim(-0.05, 0.65)

                # Set a higher z-order for the chromaticity diagram elements
                for artist in axes.get_children():
                    artist.set_zorder(2)
                    artist.set_clip_on(False)
                axes.get_children()[1].set_clip_on(True)

                # Replace 0s with really small numbers instead to avoid division by 0
                EPSILON: float = colour.hints.cast(float, np.finfo(np.float_).eps)

                points = np.where(
                    sample == 0,
                    EPSILON,
                    sample,
                )

                # xys = colour.models.Luv_uv_to_xy(points)
                # xyzs = colour.models.xy_to_XYZ(xys)
                # raw_rgbs = colour.models.XYZ_to_sRGB(xyzs)
                # rgbs = np.clip(raw_rgbs, 0.0, 1.0) #TODO is clipping the right strategy?

                points_plus_first = np.vstack([points, points[0]])
                axes.plot(points_plus_first[..., 0], points_plus_first[...,1], color='black', linewidth=4, zorder=3)

                axes.scatter(points[..., 0], points[..., 1], c='black',edgecolor='black', s=250, linewidths=2.5, zorder=4)

                # def generate_color_dots(axes: Axes):
                #     xs = []
                #     ys = []
                #     num_points = 40
                #     for i in range(num_points):
                #         for j in range(num_points):
                #             xs = np.append(xs, i/(num_points-1))
                #             ys = np.append(ys, j/(num_points-1))
                #     more_points = np.vstack([xs, ys])
                #     more_points = np.transpose(more_points)

                #     xys = colour.models.Luv_uv_to_xy(more_points)
                #     xyzss = colour.models.xy_to_XYZ(xys)
                #     rgbss = np.clip(colour.models.XYZ_to_sRGB(xyzss), 0.0, 1.0)

                #     axes.scatter(more_points[...,0], more_points[...,1], c= rgbss, edgecolor='black', s=50, linewidths=2.5 , zorder=3)

                # generate_color_dots(axes= axes)

                def triangle_area(vertices):
                    # Unpack the vertices
                    x1, y1 = vertices[0]
                    x2, y2 = vertices[1]
                    x3, y3 = vertices[2]

                    # Calculate the area using the determinant formula
                    area = 0.5 * abs(x1*(y2 - y3) + x2 *(y3 - y1) + x3*(y1 - y2))
                    return area

                axes.legend([f'Area: {triangle_area(points):0.4f}'], bbox_to_anchor=(0.9, 0.25), handlelength=0, fontsize=20, framealpha=1)
                plt.show()
                self.save_to_file(sample_name)
            else:
                print("table cell error")

    def save_to_file(self, sample_name):
        self.save_to_file_path = self.ui.le_file_directory.text()
        if (self.save_to_file_path != ""):
            try:
                plt.savefig(f"{self.save_to_file_path}\\{sample_name}_chroma.png")
            except:
                print(f"unable to save file to path: {self.save_to_file_path}\\{sample_name}_chroma.png")
        else:
            print("Not saving image")


app = QtWidgets.QApplication(sys.argv)
win = Gamut_win()

win.show()
sys.exit(app.exec_())


# pyuic5 Gamut.ui -o Gamut.py
