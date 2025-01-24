# Steel vs. Concrete Bridge Cost Comparison Application

This project provides an interactive GUI-based tool for comparing the costs of steel and concrete bridges based on various parameters such as span, width, traffic volume, and design life. The tool uses a database to store material cost rates and generates visual cost breakdowns and comparisons.

---

## Contents  
- [Features](#features)  
- [Requirements](#requirements)  
- [How to Run the Program](#how-to-run-the-program)  
- [Notes](#notes)  
- [Using the Application](#using-the-application)  
- [Contact](#contact)  

---

## Features:
- User-friendly GUI for inputting bridge parameters.
- Dynamic cost breakdown and comparison of steel and concrete bridges.
- Interactive plots for cost visualization.
- Exportable cost comparison table in CSV format.
- Database customization for material rates.

---

## Requirements:
- Python 3.10 or later
- Required libraries: 
  - **PyQt5**
  - **Matplotlib**
  - **SQLite3 (default with Python)**

Install the dependencies using the following command:  
```bash
pip install PyQt5 matplotlib
```

---

## How to Run the Program:

**1. Extract the Zip File**  
   - Extract the contents of the zip file to your desired location, e.g., `D:\folder\App`.
   

**2. Run the Application**  
   - Locate and execute the `BridgeCostApp.exe` file in the folder to launch the application.

**Note**: The database file (`bridge_costs.db`) is already included in the zip file. You do not need to run the `Database.py` file unless you want to recreate the database.

**Optional**: To create the database and pre-populate it with values, follow these steps:
- Navigate to **`Python Files`** folder.
- Open a Python interpreter (e.g., IDLE, Anaconda, or Terminal).
- Run the `Database.py` file:
   ```bash
   python Database.py
   ```
- Cut the `bridge_costs.db` file and paste it in the **`BridgeCostApp`** folder.
---

## Notes:
- Ensure that the "`bridge_costs.db`" is present in the folder before running the application.
- For any issues with dependencies, verify that the required libraries are installed using `pip list`.

---

## Using the Application:

1. **Input Parameters**:
   - Enter the span length (m), width (m), traffic volume (vehicles/day), and design life (years).

2. **Calculate Costs**:
   - Click "Calculate Costs" to compute the costs for steel and concrete bridges.

3. **View Results**:
   - View the cost breakdown in the table and the bar chart.

4. **Export Data**:
   - Export the cost breakdown to a CSV file using the "Export Table to CSV" button.
   - Export the bar chart to a PNG file using the "Export Plot" button.

5. **Update Database**:
   - Use the "Update Database" button to modify material cost rates.

---

## Contact:
For questions or issues, please contact:  
**Jayesh Dubey**  

Email: **jayeshdubey823@gmail.com**

--- 
