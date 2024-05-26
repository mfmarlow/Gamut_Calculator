import sys

from colour import RGB_COLOURSPACES
import colour.utilities
from matplotlib.patches import Polygon
from Gamut import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
# from PyQt5.Qt import Qt, QApplication, QClipboard

import numpy as np
import matplotlib.pyplot as plt
from colour.plotting import plot_RGB_colourspaces_in_chromaticity_diagram_CIE1976UCS, plot_chromaticity_diagram_CIE1976UCS
from colour import Luv_uv_to_xy
from colour.utilities import Structure
from matplotlib.axes import Axes

import colour
import sample
import area
import user_input

# # RGB Colourspaces keys list: #
# import colour.models
# from pprint import pprint
# # pprint(sorted(colour.models.RGB_COLOURSPACES.keys()))
# pprint(RGB_COLOURSPACES["NTSC \\(1953\\)"])

class Gamut_win(QtWidgets.QMainWindow):
    def __init__(self):
        super(Gamut_win, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.sample_RGB = sample.RGB_primaries()
        # Radio button initial settings
        self.ui.rB_table_s.setChecked(True)
        self.ui.groupBox_import_sample.setEnabled(False)
        # Radio button initial settings
        self.ui.pB_calculate.clicked.connect(self.calculate)
        self.ui.rB_table_s.toggled.connect(self.f_table_s)
        self.ui.rB_file_s.toggled.connect(self.f_file_s)
        self.ui.pb_browse_sample.clicked.connect(self.f_browse_sample)
        self.ui.pb_browse_sample_filter.clicked.connect(self.f_browse_sample_filter)
        self.ui.pb_file_directory_selector.clicked.connect(self.select_file_directory)
        self.ui.actionAbout.triggered.connect(self.about)
        self.table_cell_error = False

    def about(self):
        msg = QtWidgets.QMessageBox()
        msg.setTextFormat(Qt.RichText)  
        # msg.about(self, "About", "Gamut Calculator\nVersion: 1.0\n\nNo rights reserved at all cCc\n<a href='http://google.com/'>Google</a>")
        icon = QIcon()
        icon.addPixmap(QPixmap("icon.jpg"), QIcon.Normal, QIcon.Off)
        msg.setWindowIcon(icon)
        msg.setWindowTitle("About")
        msg.setIconPixmap(QPixmap("icon.jpg"))
        msg.setText('<p><span style="color:#0000a0"><span style="font-size:22px">Gamut Calculator</span></span><br><span style="font-size:15px">Version 1.0</span></p><p><span style="font-size:15px">Written in Python by using open source modules <br>by <br>Emre Beşkazak</span></p><p><span style="font-size:15px">Source code:</span><br><a href="https://github.com/emrebeskazak/Gamut_Calculator">GitHub</a></p>')
        x = msg.exec_()
              
    
    def f_browse_sample(self):
        self.ui.le_browse_sample.setText(QFileDialog.getOpenFileName()[0])
    def f_browse_sample_filter(self):
        self.ui.le_browse_sample_filter.setText(QFileDialog.getOpenFileName()[0])
    def select_file_directory(self):
        self.ui.le_file_directory.setText(QFileDialog.getExistingDirectory())
      
    def f_table_s(self):
        if self.sender().isChecked():
            self.ui.tW_sample.setEnabled(True)
            self.ui.groupBox_import_sample.setEnabled(False)
    def f_file_s(self):
        if self.sender().isChecked():
            self.ui.tW_sample.setEnabled(False)
            self.ui.groupBox_import_sample.setEnabled(True)
   
    def load_table(self, clrspace):
        table_row = 0
        for item in RGB_COLOURSPACES[clrspace].primaries:
            item = (item)
            table_row +=1


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.cntrl = True
        # Ctrl + V Paste code for tabel widget
        elif event.key() == Qt.Key_V:
            if self.cntrl:
                if self.ui.tW_sample.hasFocus():
                    text = QtWidgets.QApplication.clipboard().text()
                    text = text.splitlines()
                    if len(text) > 1:
                        table_row = 0
                        for line in text:
                            l_tuple = line.strip().partition("\t")
                            self.ui.tW_sample.setItem(table_row,0,QTableWidgetItem(l_tuple[0].strip()))
                            self.ui.tW_sample.setItem(table_row,1,QTableWidgetItem(l_tuple[2].strip()))
                            table_row +=1
                    else:
                        l_tuple = text[0].strip().partition("\t")
                        self.ui.tW_sample.setItem(self.ui.tW_sample.currentRow(),self.ui.tW_sample.currentColumn(),QTableWidgetItem(l_tuple[0].strip()))
        # Ctrl + C Copy code for table widget
        elif event.key() == Qt.Key_C:
            if self.cntrl:
                if self.ui.tW_sample.hasFocus():
                    QtWidgets.QApplication.clipboard().setText(f"{self.ui.tW_sample.item(0, 0).text()}\t{self.ui.tW_sample.item(0, 1).text()}\n{self.ui.tW_sample.item(1, 0).text()}\t{self.ui.tW_sample.item(1, 1).text()}\n{self.ui.tW_sample.item(2, 0).text()}\t{self.ui.tW_sample.item(2, 1).text()}\n{self.ui.tW_sample.item(3, 0).text()}\t{self.ui.tW_sample.item(3, 1).text()}")
        elif event.key() == Qt.Key_Delete:
            if self.ui.tW_sample.hasFocus():
                self.ui.tW_sample.setItem(self.ui.tW_sample.currentRow(),self.ui.tW_sample.currentColumn(),QTableWidgetItem(""))

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.cntrl =False

    ##
    # THE METHOD FOR CALCULATIONS BASED ON THE COORDINATES ENTERED INTO TABLE
    ##
    def calculate(self):
        
        sample, self.sample_name = user_input.get_colorspace_input(self)

        if not self.table_cell_error:

            # Create a figure and axes
            figure = plt.figure(figsize=(10, 10))
            axes = figure.add_subplot()

            # Plot the chromaticity diagram
            colour.plotting.plot_chromaticity_diagram_CIE1976UCS(axes=axes, transparent_background=False)
            # colour.plotting.plot_RGB_colourspaces_in_chromaticity_diagram_CIE1976UCS
            # Set the title with a higher position
            axes.set_title('Chromaticity Graph', y=1.05, fontsize=30, fontweight = 'bold')
            plt.text(0.5, 1.02, self.sample_name, ha='center', va='center', transform=axes.transAxes, fontsize=20)

            # Adjust subplot parameters to create more space around the plot
            plt.subplots_adjust(left=0.07, right=0.9, top=0.9, bottom=0.07)

            # Set the x and y axis limits
            axes.set_xlim(-0.05, 0.65)
            axes.set_ylim(-0.05, 0.65)

            # Enable gridlines with a custom z-order
            axes.grid(True)

            # Set a higher z-order for the chromaticity diagram elements
            for artist in axes.get_children():
                artist.set_zorder(2)
                artist.set_clip_on(False)
            axes.get_children()[1].set_clip_on(True)

            axes.set_axisbelow(True)

            EPSILON: float = colour.hints.cast(float, np.finfo(np.float_).eps)

            P = np.where(
                sample == 0,
                EPSILON,
                sample,
            )

            def uv_to_xyz(u, v):
                # Convert from CIE 1976 u'v' to CIE 1931 XYZ
                if v == 0:
                    return 0, 0, 0
                Y = 1
                X = (9 * u) / (4 * v)
                Z = (12 - 3 * u - 20 * v) / (4 * v)
                return X, Y, Z

            def xyz_to_rgb(X, Y, Z):
                # Convert from CIE 1931 XYZ to linear sRGB
                matrix = np.array([
                    [ 3.2406, -1.5372, -0.4986],
                    [-0.9689,  1.8758,  0.0415],
                    [ 0.0557, -0.2040,  1.0570]
                ])
                rgb = np.dot(matrix, np.array([X, Y, Z]))
                return rgb

            def gamma_correction(rgb):
                # Apply gamma correction to linear RGB values to get sRGB values
                def correct(c):
                    if c <= 0.0031308:
                        return 12.92 * c
                    else:
                        return 1.055 * (c ** (1 / 2.4)) - 0.055

                return np.array([correct(c) for c in rgb])

            def clip_rgb(rgb):
                # Clip the RGB values to be in the range [0, 1]
                return np.clip(rgb, 0, 1)

            def uv_to_rgb(u, v):
                X, Y, Z = uv_to_xyz(u, v)
                rgb = xyz_to_rgb(X, Y, Z)
                rgb = gamma_correction(rgb)
                rgb = clip_rgb(rgb)
                return rgb
            
            colour.models.XYZ_to_sRGB
            P = colour.models.xy_to_Luv_uv(P)

            P_p = np.vstack([P, P[0]])
            axes.plot(P_p[..., 0], P_p[..., 1], color = 'black', linewidth = 4, zorder=3)

            for u, v in P_p:
                rgb = uv_to_rgb(u, v)
                axes.scatter(u, v, color = rgb, edgecolor='black', s=250, linewidths=2.5, zorder=4)

            def generate_color_dots(axes: Axes):
                num_points = 20
                for i in range(num_points):
                    for j in range(num_points):
                        u_prime = i/(num_points-1)
                        v_prime = j/(num_points-1)
                        if u_prime == 0 or v_prime == 0:
                            continue

                        rgb = uv_to_rgb(u_prime, v_prime)

                        axes.scatter(u_prime, v_prime, color=rgb, edgecolor='black', s=250, linewidths=2.5 , zorder=3)

            # generate_color_dots(axes= axes)
            plt.show()
            self.save_to_file()
        else:
            print("table cell error")

    def save_to_file(self):
        self.save_to_file_path = self.ui.le_file_directory.text()
        if(self.save_to_file_path != ""):
            try:
                plt.savefig(f"{self.save_to_file_path}\\{self.sample_name}_plot.png")
            except :
                print(f"unable to save file to path: {self.save_to_file_path}\\{self.sample_name}_plot.png")
        else:
            print("Not saving image")
            # plt.savefig(f"{self.sample_RGB.RGB_COLOURSPACE_SAMPLE.name}_plot.png")

app = QtWidgets.QApplication(sys.argv)
win = Gamut_win()

win.show()
sys.exit(app.exec_())


# pyuic5 Gamut.ui -o Gamut.py

