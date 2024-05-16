import sys

from colour import RGB_COLOURSPACES
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
        
        user_input.get_colorspace_input(self)

        if not self.table_cell_error:
            # Results text
            self.sample_area = area.sample_area(self.sample_RGB.RGB_COLOURSPACE_SAMPLE)
            self.ui.textBrowser.setText(f"in CIE 1976 (uv) colorspace\nArea: {self.sample_area}")

            # Plot colourspace diagrams
            self.wp_bool = self.wp_s_bool
            
            plot_RGB_colourspaces_in_chromaticity_diagram_CIE1976UCS(
                self.sample_RGB.RGB_COLOURSPACE_SAMPLE,
                show_whitepoints = self.wp_bool,
                show = True,
                plot_kwargs= {
                    "color":"black",
                    "marker": "o",
                    "markeredgecolor" : "black",
                    "markerfacecolor": ('white', 0.0),
                    "markerfacecoloralt": ('white', 0.0)
                    },
                kwargs = {
                    "title" : None,
                    "legend" : False,
                    "transparent_background" : False,
                    "axes_visible" : True
                    }
            )

        else:
            print("table cell error")

app = QtWidgets.QApplication(sys.argv)
win = Gamut_win()

win.show()
sys.exit(app.exec_())


# pyuic5 Gamut.ui -o Gamut.py

