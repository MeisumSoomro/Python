System Resource Monitor
=====================

A comprehensive system monitoring tool that tracks CPU, memory, and disk usage in real-time.

Features:
--------
1. Real-time Performance Tracking
   - Monitor CPU usage percentage
   - Track memory utilization
   - Monitor disk space usage
   - Real-time metrics display

2. Resource Usage Alerts
   - Configurable alert thresholds
   - CPU usage alerts (default: 80%)
   - Memory usage alerts (default: 85%)
   - Disk usage alerts (default: 90%)
   - Visual alert indicators

3. Historical Data Analysis
   - Store metrics history
   - Track resource usage over time
   - Data persistence in CSV format
   - Timestamp-based tracking

4. Performance Reporting
   - CSV report generation
   - Detailed system metrics
   - Customizable report formats
   - Export options

5. System Health Monitoring
   - System information tracking
   - Process monitoring
   - Resource utilization trends
   - Health status indicators

Requirements:
------------
- Python 3.7 or higher
- psutil library (pip install psutil)
- Operating System: Windows/Linux/MacOS

Installation:
------------
1. Ensure Python 3.7+ is installed
2. Install required package:
   pip install psutil

Usage:
-----
1. Run the script:
   python system_resource_monitor.py

2. Monitor output:
   - Real-time metrics will be displayed
   - Alerts will show when thresholds are exceeded
   - Press Ctrl+C to stop monitoring

3. Reports:
   - Generated in 'reports' directory
   - Format: CSV with timestamp
   - Contains CPU, memory, and disk metrics

Configuration:
-------------
Alert thresholds can be modified in the SystemResourceMonitor class:
- CPU threshold: 80%
- Memory threshold: 85%
- Disk threshold: 90%

Report Format:
------------
CSV columns:
- Timestamp
- CPU Usage (%)
- Memory Usage (%)
- Memory Available (GB)
- Memory Total (GB)

Example Output:
-------------
===============================
Timestamp: 2024-03-14T15:30:45
CPU Usage: 45%
Memory Usage: 65%

Disk Usage:
C:\: 75% used
D:\: 60% used
===============================

Notes:
-----
- Reports are automatically saved when monitoring stops
- Each monitoring session creates a new report file
- Alert thresholds can be customized as needed
- Multiple instances can be run for different monitoring profiles 