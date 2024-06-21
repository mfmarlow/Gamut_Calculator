import numpy as np
import csv
from numpy._typing import NDArray


def check_values_within_limits(self):
    table_y = 0
    while table_y <= 1:
        table_x = 0
        while table_x <= 2:
            if (self.ui.tW_sample.item(table_x, table_y).text().strip() != "") and (float(self.ui.tW_sample.item(table_x, table_y).text()) < 0.9) and (float(self.ui.tW_sample.item(table_x, table_y).text()) > 0):
                # print(f"pass ({table_x}, {table_y})")
                pass
            else:
                print(f"Inappropriate table value at ({table_x}, {table_y})")
            table_x += 1
        table_y += 1


def get_colorspace_input(self):
    if self.ui.rB_file_s.isChecked():
        file_path = self.ui.le_browse_sample.text()
        try:
            with open(file_path,"r", encoding='utf8', errors='replace') as file:
                csv_rows = csv.reader(file)
                data = list(csv_rows)
                array = np.array(data)
                samples_u_prime = array[11]
                samples_v_prime = array[12]
                SAMPLE = np.array(
                    [
                        np.array(
                            [
                                get_sample_name(self),
                                samples_u_prime[1], samples_v_prime[1],
                                samples_u_prime[2], samples_v_prime[2],
                                samples_u_prime[3], samples_v_prime[3]
                            ]
                        )
                    ]
                )
                return SAMPLE
        except:
            return np.array(
                [
                    np.array(
                        [
                            get_sample_name(self)
                        ]
                    )
                ]
            )

    elif self.ui.rB_table_s.isChecked():
        # Check table values if empty and between 0 and 0.9
        check_values_within_limits(self)

        # Get primary RGB uv coordinates from table widget cells
        SAMPLE = np.array(
            [
                np.array(
                    [
                        get_sample_name(self),
                        self.ui.tW_sample.item(0, 0).text(), self.ui.tW_sample.item(0, 1).text(),   #R
                        self.ui.tW_sample.item(1, 0).text(), self.ui.tW_sample.item(1, 1).text(),   #G
                        self.ui.tW_sample.item(2, 0).text(), self.ui.tW_sample.item(2, 1).text(),   #B
                    ]
                )
            ]
        )

        return SAMPLE

def get_sample_name(self):
    if self.ui.le_sample_name.text().strip() != "":
        WHITEPOINT_NAME_SAMPLE = self.ui.le_sample_name.text()
    else:
        WHITEPOINT_NAME_SAMPLE = "Placeholder"
    return WHITEPOINT_NAME_SAMPLE