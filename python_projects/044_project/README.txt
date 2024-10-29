Data Visualization Tool
=====================

Project Structure:
----------------
044_project/
├── data_visualization_tool.py  # Main program file
├── chart_config.json          # Configuration file (created on first run)
└── README.txt                # This file

Requirements:
------------
1. Python 3.7 or higher
2. Required Python packages:
   - matplotlib
   - pandas
   - seaborn
   - numpy

Installation:
------------
1. Install required packages:
   pip install matplotlib pandas seaborn numpy

Features:
--------
1. Data Loading
   - Support for CSV and Excel files
   - Automatic data type detection
   - Data validation

2. Chart Types
   - Line charts
   - Bar charts
   - Scatter plots
   - Pie charts
   - Histograms
   - Box plots
   - Heatmaps

3. Customization
   - Multiple themes
   - Custom colors
   - Adjustable sizes
   - Title and labels

4. Data Analysis
   - Basic statistics
   - Column information
   - Missing value detection
   - Correlation analysis

Classes:
-------
1. ChartType
   - Defines available chart types
   - Constants for chart selection

2. DataVisualizer
   - Main visualization class
   - Handles data loading
   - Creates and manages charts
   - Provides data analysis

Configuration:
------------
1. Themes
   - Default theme
   - Dark theme
   - Light theme
   - Custom themes

2. Chart Settings
   - Figure size
   - DPI
   - Save format
   - Style preferences

Usage:
-----
1. Run the program:
   python data_visualization_tool.py

2. Main Operations:
   - Load data files
   - Create various charts
   - Customize appearance
   - Save/export charts

3. Data Analysis:
   - View data information
   - Calculate statistics
   - Analyze columns
   - Check correlations

Important Notes:
--------------
1. Data Files:
   - Support for CSV (.csv)
   - Support for Excel (.xlsx, .xls)
   - Proper column headers required

2. Memory Usage:
   - Large files may require more RAM
   - Consider data sampling
   - Close figures when done

3. Chart Export:
   - Multiple format support
   - High-resolution output
   - Automatic file naming

4. Themes:
   - Configurable via JSON
   - Persistent settings
   - Custom theme support

Troubleshooting:
--------------
1. Common Issues:
   - ModuleNotFoundError: Install required packages
   - Memory Error: Reduce data size
   - Display Error: Check matplotlib backend

2. Data Problems:
   - Check file format
   - Verify column names
   - Handle missing values

For Support:
----------
[Your contact information or repository link here] 