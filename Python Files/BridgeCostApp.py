import sys
import sqlite3, datetime, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QSplitter, QMessageBox,
    QInputDialog, QGroupBox, QHeaderView, QSizePolicy, QFormLayout, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import csv


class BridgeCostApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bridge Cost Comperision")

        app_icon = QIcon("Images/App_logo.png")
        self.setWindowIcon(app_icon)
        
        # Main Layout
        main_layout = QHBoxLayout()
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Database connection
        self.conn = sqlite3.connect("bridge_costs.db")

        # Main GUI components
        self.input_panel = self.create_input_panel()
        main_layout.addWidget(self.input_panel)

        self.plot_panel = self.create_plot_panel()
        main_layout.addWidget(self.plot_panel)

        self.output_panel = self.create_output_panel()
        main_layout.addWidget(self.output_panel)

        # Connect button signals
        self.calculate_button.clicked.connect(self.calculate_costs)
        self.export_button.clicked.connect(self.export_plot)
        self.update_button.clicked.connect(self.update_database)
        self.export_csv_button.clicked.connect(self.export_to_csv)

        self.showMaximized()

    def create_input_panel(self):
        panel = QGroupBox("Input Parameters")
        panel.setStyleSheet("QGroupBox { font-size: 22px; font-weight: bold; }")

        layout = QVBoxLayout()  

        form_layout = QFormLayout()  
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(20)
        form_layout.setContentsMargins(15, 15, 15, 15)
        label_style = "font-size: 18px; font-weight: bold;"
        input_style = """
            QLineEdit {
                font-size: 18px;
                padding: 8px;
            }
        """

        # Input fields
        self.span_input = QLineEdit()
        self.span_input.setValidator(QDoubleValidator(0.0, 999999.0, 2))
        self.span_input.setPlaceholderText("Enter span length in meters")
        self.span_input.setStyleSheet(input_style)
        span_label = QLabel("Span Length (m):")
        span_label.setStyleSheet(label_style)
        form_layout.addRow(span_label, self.span_input)

        self.width_input = QLineEdit()
        self.width_input.setValidator(QDoubleValidator(0.0, 999999.0, 2))
        self.width_input.setPlaceholderText("Enter width in meters")
        self.width_input.setStyleSheet(input_style)
        width_label = QLabel("Width (m):")
        width_label.setStyleSheet(label_style)
        form_layout.addRow(width_label, self.width_input)

        self.traffic_input = QLineEdit()
        self.traffic_input.setValidator(QIntValidator(0, 99999999))
        self.traffic_input.setPlaceholderText("Enter traffic volume (vehicles/day)")
        self.traffic_input.setStyleSheet(input_style)
        traffic_label = QLabel("Traffic Volume (vehicles/day):")
        traffic_label.setStyleSheet(label_style)
        form_layout.addRow(traffic_label, self.traffic_input)

        self.life_input = QLineEdit()
        self.life_input.setValidator(QIntValidator(1, 200))
        self.life_input.setPlaceholderText("Enter design life in years")
        self.life_input.setStyleSheet(input_style)
        life_label = QLabel("Design Life (years):")
        life_label.setStyleSheet(label_style)
        form_layout.addRow(life_label, self.life_input)

        # Buttons
        self.calculate_button = QPushButton("Calculate Costs")
        self.style_button(self.calculate_button)
        form_layout.addRow(self.calculate_button)

        self.update_button = QPushButton("Update Database")
        self.style_button(self.update_button)
        form_layout.addRow(self.update_button)

        layout.addLayout(form_layout)

        # Database Table
        db_label = QLabel("Database")
        db_label.setStyleSheet("font-size: 22px; font-weight: bold; margin-top: 15px;")
        layout.addWidget(db_label)

        self.db_table = QTableWidget()
        self.db_table.setStyleSheet("""
            QTableWidget {
                font-size: 16px;
                border: 1px solid #ccc;
            }
            QHeaderView::section {
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.refresh_database_table()
        layout.addWidget(self.db_table)

        panel.setLayout(layout)
        return panel
    
    def refresh_database_table(self):
        try:
            cursor = self.conn.cursor()

            # Fetch the required data for Steel and Concrete
            cursor.execute("""
                SELECT material, `Base Rate (₹/m²)`, `Maintenance Rate (₹/m²/year)`, `Repair Rate (₹/m²)`, `Demolition Rate (₹/m²)`, 
                       `Environmental Factor (₹/m²)`, `Social Factor (₹/vehicle/year)`, `Delay Factor (₹/vehicle/year)` 
                FROM bridge_costs
                WHERE material IN ('Steel', 'Concrete')
            """)
            data = cursor.fetchall()

            # Define row headers for each parameter
            row_headers = [
                "Base Rate (₹/m²)", "Maintenance Rate (₹/m²/year)", "Repair Rate (₹/m²)", 
                "Demolition Rate (₹/m²)", "Environmental Factor (₹/m²)", 
                "Social Factor (₹/vehicle/year)", "Delay Factor (₹/vehicle/year)"
            ]

            # Initialize table dimensions
            self.db_table.setRowCount(len(row_headers))
            self.db_table.setColumnCount(3)
            self.db_table.setHorizontalHeaderLabels([
                "Parameters", "Steel Bridge (₹)", "Concrete Bridge (₹)"
            ])

            for row_idx in range(len(row_headers)):
                self.db_table.setRowHeight(row_idx, 64)


            for row_idx, row_name in enumerate(row_headers):
                self.db_table.setItem(row_idx, 0, QTableWidgetItem(row_name))

            
            rates = {"Steel": {}, "Concrete": {}}
            for row in data:
                material, base_rate, maintenance_rate, repair_rate, demolition_rate, environmental_factor, social_factor, delay_factor = row
                rates[material] = {
                    "Base Rate (₹/m²)": base_rate,
                    "Maintenance Rate (₹/m²/year)": maintenance_rate,
                    "Repair Rate (₹/m²)": repair_rate,
                    "Demolition Rate (₹/m²)": demolition_rate,
                    "Environmental Factor (₹/m²)": environmental_factor,
                    "Social Factor (₹/vehicle/year)": social_factor,
                    "Delay Factor (₹/vehicle/year)": delay_factor,
                }

            for row_idx, row_name in enumerate(row_headers):
                for col_idx, material in enumerate(["Steel", "Concrete"]):
                    value = rates[material].get(row_name, "N/A")
                    self.db_table.setItem(row_idx, col_idx + 1, QTableWidgetItem(f"{value:.2f}" if isinstance(value, float) else str(value)))

            self.db_table.resizeColumnsToContents()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Could not fetch data: {e}")


    def create_plot_panel(self):
        panel = QGroupBox("Cost Comparison Plot")
        panel.setStyleSheet("QGroupBox { font-size: 22px; font-weight: bold; }")
        layout = QVBoxLayout()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.export_button = QPushButton("Export Plot")
        self.style_button(self.export_button) 
        layout.addWidget(self.export_button)

        panel.setLayout(layout)
        return panel

    def create_output_panel(self):
        panel = QGroupBox("Cost Breakdown")
        panel.setStyleSheet("QGroupBox { font-size: 22px; font-weight: bold; }")
        layout = QVBoxLayout()


        self.output_table = QTableWidget()
        self.output_table.setRowCount(8)
        self.output_table.setColumnCount(3)
        self.output_table.setHorizontalHeaderLabels([
            "Cost Component", "Steel Bridge (₹)", "Concrete Bridge (₹)"
        ])
        self.output_table.setStyleSheet("""
        QTableWidget {
            font-size: 18px;  
        }
        QTableWidget::item {
            padding: 8px;  
        }
        QHeaderView::section {
            font-size: 18px;  
            font-weight: bold;  
        }
        """)
        
        header = self.output_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.output_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addWidget(self.output_table)

        self.export_csv_button = QPushButton("Export Table to CSV")
        self.style_button(self.export_csv_button)
        layout.addWidget(self.export_csv_button)

        panel.setLayout(layout)
        return panel

    def calculate_costs(self):
        try:
            # Retrieve input values
            span_length = float(self.span_input.text())
            width = float(self.width_input.text())
            traffic_volume = float(self.traffic_input.text())
            design_life = int(self.life_input.text())

            # Fetch data from the database
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM bridge_costs")
            data = cursor.fetchall()

            cost_results = []

            for row in data:
                material, base_rate, maintenance_rate, repair_rate, demolition_rate, environmental_factor, social_factor, delay_factor = row

                construction_cost = span_length * width * base_rate
                maintenance_cost = span_length * width * maintenance_rate * design_life
                repair_cost = span_length * width * repair_rate
                demolition_cost = span_length * width * demolition_rate
                environmental_cost = span_length * width * environmental_factor
                social_cost = traffic_volume * social_factor * design_life
                user_cost = traffic_volume * delay_factor * design_life

                total_cost = (construction_cost + maintenance_cost + repair_cost +
                              demolition_cost + environmental_cost + social_cost + user_cost)

                cost_results.append((material, [construction_cost, maintenance_cost, repair_cost,
                                                demolition_cost, environmental_cost, social_cost, user_cost, total_cost]))

            self.output_table.setRowCount(8)

            for i, (component, steel_value, concrete_value) in enumerate([
                ("Construction Cost", cost_results[0][1][0], cost_results[1][1][0]),
                ("Maintenance Cost", cost_results[0][1][1], cost_results[1][1][1]),
                ("Repair Cost", cost_results[0][1][2], cost_results[1][1][2]),
                ("Demolition Cost", cost_results[0][1][3], cost_results[1][1][3]),
                ("Environmental Cost", cost_results[0][1][4], cost_results[1][1][4]),
                ("Social Cost", cost_results[0][1][5], cost_results[1][1][5]),
                ("User Cost", cost_results[0][1][6], cost_results[1][1][6]),
                ("Total Cost", cost_results[0][1][7], cost_results[1][1][7])
            ]):
                self.output_table.setItem(i, 0, QTableWidgetItem(component))
                self.output_table.setItem(i, 1, QTableWidgetItem(f"{steel_value:.2f}"))
                self.output_table.setItem(i, 2, QTableWidgetItem(f"{concrete_value:.2f}"))

            # Generate bar plot
            self.update_plot(cost_results)

        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numeric values for all fields.")

    def update_plot(self, cost_results):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        components = ["Construction", "Maintenance", "Repair", "Demolition", "Environmental", "Social", "User", "Total"]
        steel_costs = [result[1][i] for result in cost_results if result[0] == "Steel" for i in range(8)]
        concrete_costs = [result[1][i] for result in cost_results if result[0] == "Concrete" for i in range(8)]

        x = range(len(components))
        ax.bar([p - 0.2 for p in x], steel_costs, width=0.4, label="Steel", align="center")
        ax.bar([p + 0.2 for p in x], concrete_costs, width=0.4, label="Concrete", align="center")

        ax.set_xticks(x)
        ax.set_xticklabels(components, rotation=45, ha="right")
        ax.set_ylabel("Cost (₹)")
        ax.set_title("Cost Comparison: Steel vs. Concrete")
        ax.legend()

        self.canvas.draw()
        
    def update_database(self):
        try:
            material, ok = QInputDialog.getItem(self, "Select Material", "Choose the material to update:", ["Steel", "Concrete"], editable=False)
            if not ok:
                return

            rates = {}
            for rate_name in ["`Base Rate (₹/m²)`", "`Maintenance Rate (₹/m²/year)`", "`Repair Rate (₹/m²)`", "`Demolition Rate (₹/m²)`", "`Environmental Factor (₹/m²)`",
                              "`Social Factor (₹/vehicle/year)`", "`Delay Factor (₹/vehicle/year)`"]:
                rate, ok = QInputDialog.getDouble(self, f"Update {rate_name}", f"Enter new value for {rate_name} (₹):")
                if not ok:
                    return
                rates[rate_name] = rate

            cursor = self.conn.cursor()
            cursor.execute(f"""
                UPDATE bridge_costs
                SET `Base Rate (₹/m²)` = ?, `Maintenance Rate (₹/m²/year)` = ?, `Repair Rate (₹/m²)` = ?, `Demolition Rate (₹/m²)` = ?, `Environmental Factor (₹/m²)` = ?,
                `Social Factor (₹/vehicle/year)` = ?, `Delay Factor (₹/vehicle/year)` = ?
                WHERE material = ?
            """, (
                rates["`Base Rate (₹/m²)`"], rates["`Maintenance Rate (₹/m²/year)`"], rates["`Repair Rate (₹/m²)`"],
                rates["`Demolition Rate (₹/m²)`"], rates["`Environmental Factor (₹/m²)`"],
                rates["`Social Factor (₹/vehicle/year)`"], rates["`Delay Factor (₹/vehicle/year)`"], material
            ))
            self.conn.commit()

            self.refresh_database_table()

            QMessageBox.information(self, "Database Updated", f"Rates for {material} updated successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Update Error", f"Could not update database: {e}")
            
    def export_plot(self):
        try:
            folder = "Exported Plots"
            os.makedirs(folder, exist_ok=True)

            # Generate a timestamped filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(folder, f"cost_comparison_{timestamp}.png")

            # Save the plot
            self.figure.savefig(filename)
            QMessageBox.information(self, "Export Successful", f"Plot saved as {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Could not save plot: {e}")
            
    def export_to_csv(self):
        try:
            # Ensure the "CSV Files" folder exists
            folder = "CSV Files"
            os.makedirs(folder, exist_ok=True)

            # Generate a timestamped filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"Output_{timestamp}.csv"
            file_path = os.path.join(folder, file_name)

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                headers = [self.output_table.horizontalHeaderItem(i).text() for i in range(self.output_table.columnCount())]
                writer.writerow(headers)

                # Write data rows
                for row in range(self.output_table.rowCount()):
                    row_data = [
                        self.output_table.item(row, col).text() if self.output_table.item(row, col) else ""
                        for col in range(self.output_table.columnCount())
                    ]
                    writer.writerow(row_data)

            # Show success message with the saved file path
            QMessageBox.information(self, "Export Successful", f"Data successfully exported to {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred while exporting: {e}")
        
    def style_button(self, button):
        """
        Apply a consistent style to QPushButton.

        :param button: The QPushButton to style.
        """
        button_stylesheet = """
        QPushButton {
            background-color: #007BFF;  
            color: white;              
            border: none;              
            border-radius: 5px;        
            padding: 10px;             
            font-size: 16px;           
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0056b3; 
        }
        QPushButton:pressed {
            background-color: #003f7f; 
        }
        """
        button.setStyleSheet(button_stylesheet)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BridgeCostApp()
    window.show()
    sys.exit(app.exec_())
