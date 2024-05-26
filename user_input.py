from PyQt5.QtWidgets import QTableWidgetItem
import numpy as np
from colour import Luv_uv_to_xy

def get_sample_name(self):
    if self.ui.le_sample_name.text().strip() != "":
        WHITEPOINT_NAME_SAMPLE = self.ui.le_sample_name.text()
    else:
        WHITEPOINT_NAME_SAMPLE = "Sample"
    return WHITEPOINT_NAME_SAMPLE

def fill_table(self):
    self.ui.tW_sample.setEnabled(True)
    table_row = 0
    for item in self.sample_RGB.RGB_COLOURSPACE_SAMPLE.primaries:
        self.ui.tW_sample.setItem(table_row,0,QTableWidgetItem(str(item[0])))
        self.ui.tW_sample.setItem(table_row,1,QTableWidgetItem(str(item[1])))
        table_row +=1
    self.ui.tW_sample.setItem(3,0,QTableWidgetItem(str((self.sample_RGB.RGB_COLOURSPACE_SAMPLE.whitepoint)[0])))
    self.ui.tW_sample.setItem(3,1,QTableWidgetItem(str((self.sample_RGB.RGB_COLOURSPACE_SAMPLE.whitepoint)[1])))

# def table_contains_whitepoint(self):
#     return type(self.ui.tW_sample.item(3,0)) == QTableWidgetItem and type(self.ui.tW_sample.item(3,1)) == QTableWidgetItem

# def get_whitepoint_from_table(self):
#     if self.ui.tW_sample.item(3, 0).text().strip() != "" and self.ui.tW_sample.item(3, 1).text().strip() != "":
#         if (float(self.ui.tW_sample.item(3, 0).text()) < 0.9) and (float(self.ui.tW_sample.item(3, 0).text()) > 0) and (float(self.ui.tW_sample.item(3, 1).text()) < 0.9) and (float(self.ui.tW_sample.item(3, 1).text()) > 0):
#             CCS_WHITEPOINT_SAMPLE = np.array([float(self.ui.tW_sample.item(3, 0).text()), float(self.ui.tW_sample.item(3, 1).text())])
#             self.wp_s_bool = True
#     else:
#         self.wp_s_bool = False
#         CCS_WHITEPOINT_SAMPLE = np.array([0.3,0.3])
#     return CCS_WHITEPOINT_SAMPLE

def check_values_within_limits(self):
    table_y =0
    while table_y <= 1:
        table_x =0
        while table_x <=5:
            if (self.ui.tW_sample.item(table_x, table_y).text().strip() != "") and (float(self.ui.tW_sample.item(table_x, table_y).text()) < 0.9) and (float(self.ui.tW_sample.item(table_x, table_y).text()) > 0):
                    # print(f"pass ({table_x}, {table_y})")
                pass
            else:
                print(f"Inappropriate table value at ({table_x}, {table_y})")
            table_x +=1
        table_y +=1

def get_colorspace_input(self):
    if self.ui.rB_file_s.isChecked():
        # Get sample name name from line edit form or set generic name if empty
        SAMPLE_NAME = get_sample_name(self)

        self.sample_RGB.set_RGB_primaries_from_file(
            file_path = self.ui.le_browse_sample.text(),
            WHITEPOINT_NAME = SAMPLE_NAME,
            filter_path = self.ui.le_browse_sample_filter.text(),
            filter_bool = self.ui.groupBox_sample_filter.isChecked(),
            is_sample = True,
            spectrum_bool = self.ui.pB_spectrum.isChecked()
            )
        self.wp_s_bool = True

        fill_table(self)

    elif self.ui.rB_table_s.isChecked():
        # Check table values if empty and between 0 and 0.9
        check_values_within_limits(self)

        # Get primary RGB xy coordinates from table widget cells
        PRIMARIES_SAMPLE = np.array(
            [
                Luv_uv_to_xy(np.array([float(self.ui.tW_sample.item(0, 0).text()), float(self.ui.tW_sample.item(0, 1).text())])),   #R
                Luv_uv_to_xy(np.array([float(self.ui.tW_sample.item(1, 0).text()), float(self.ui.tW_sample.item(1, 1).text())])),   #G
                Luv_uv_to_xy(np.array([float(self.ui.tW_sample.item(2, 0).text()), float(self.ui.tW_sample.item(2, 1).text())])),   #B
                Luv_uv_to_xy(np.array([float(self.ui.tW_sample.item(3, 0).text()), float(self.ui.tW_sample.item(3, 1).text())])),   #Y
                Luv_uv_to_xy(np.array([float(self.ui.tW_sample.item(4, 0).text()), float(self.ui.tW_sample.item(4, 1).text())])),   #C
                Luv_uv_to_xy(np.array([float(self.ui.tW_sample.item(5, 0).text()), float(self.ui.tW_sample.item(5, 1).text())])),   #M
            ]
        )
        
        # Get whitepoint xy coordinates from table widget cells and decide whether to show whitepoint or not
        # if table_contains_whitepoint(self):
        #     CCS_WHITEPOINT_SAMPLE = get_whitepoint_from_table(self) 
        # else:
        self.wp_s_bool = False
        # CCS_WHITEPOINT_SAMPLE = np.array([0.3,0.3])     # Values not important. Whitepoint won't show.

        # Get sample name name from line edit form or set generic name if empty
        SAMPLE_NAME = get_sample_name(self)

        # Initialize an RGB_Colourspace object from colour-science module with the data above
        # self.sample_RGB.set_RGB_primaries_from_table(
        #     PRIMARIES = PRIMARIES_SAMPLE,
        #     CCS_WHITEPOINT = CCS_WHITEPOINT_SAMPLE,
        #     WHITEPOINT_NAME = WHITEPOINT_NAME_SAMPLE
        # )

        return PRIMARIES_SAMPLE, SAMPLE_NAME