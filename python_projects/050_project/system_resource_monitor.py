import psutil
import time
import datetime
import csv
import os
from typing import Dict, List
import platform
from pathlib import Path

class SystemResourceMonitor:
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        self.system_info = self._get_system_info()
        self.alert_thresholds = {
            'cpu': 80.0,  # CPU usage above 80%
            'memory': 85.0,  # Memory usage above 85%
            'disk': 90.0,  # Disk usage above 90%
        }
        self.monitoring = False
        self.history: List[Dict] = []

    def _get_system_info(self) -> Dict:
        """Get basic system information."""
        return {
            'system': platform.system(),
            'processor': platform.processor(),
            'memory_total': psutil.virtual_memory().total,
            'disk_partitions': psutil.disk_partitions(),
            'python_version': platform.python_version(),
        }

    def get_cpu_info(self) -> Dict:
        """Get current CPU usage information."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 'N/A'
        }

    def get_memory_info(self) -> Dict:
        """Get current memory usage information."""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'percent': mem.percent,
            'used': mem.used,
            'free': mem.free
        }

    def get_disk_info(self) -> Dict:
        """Get disk usage information for all partitions."""
        disk_info = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.mountpoint] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
            except PermissionError:
                continue
        return disk_info

    def check_alerts(self, metrics: Dict) -> List[str]:
        """Check if any metrics exceed alert thresholds."""
        alerts = []
        if metrics['cpu_info']['cpu_percent'] > self.alert_thresholds['cpu']:
            alerts.append(f"HIGH CPU USAGE: {metrics['cpu_info']['cpu_percent']}%")
        
        if metrics['memory_info']['percent'] > self.alert_thresholds['memory']:
            alerts.append(f"HIGH MEMORY USAGE: {metrics['memory_info']['percent']}%")
        
        for mount, disk_data in metrics['disk_info'].items():
            if disk_data['percent'] > self.alert_thresholds['disk']:
                alerts.append(f"HIGH DISK USAGE on {mount}: {disk_data['percent']}%")
        
        return alerts

    def collect_metrics(self) -> Dict:
        """Collect all system metrics."""
        metrics = {
            'timestamp': datetime.datetime.now().isoformat(),
            'cpu_info': self.get_cpu_info(),
            'memory_info': self.get_memory_info(),
            'disk_info': self.get_disk_info()
        }
        return metrics

    def start_monitoring(self, interval: int = 5):
        """Start monitoring system resources."""
        self.monitoring = True
        print("Starting system monitoring...")
        print(f"System Information:\n{self.system_info}")
        
        try:
            while self.monitoring:
                metrics = self.collect_metrics()
                self.history.append(metrics)
                
                # Check for alerts
                alerts = self.check_alerts(metrics)
                if alerts:
                    print("\nALERTS:")
                    for alert in alerts:
                        print(f"⚠️ {alert}")

                # Display current metrics
                self._display_metrics(metrics)
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            self.stop_monitoring()

    def stop_monitoring(self):
        """Stop monitoring and save reports."""
        self.monitoring = False
        self.export_report()

    def _display_metrics(self, metrics: Dict):
        """Display current metrics in a readable format."""
        print("\n" + "="*50)
        print(f"Timestamp: {metrics['timestamp']}")
        print(f"CPU Usage: {metrics['cpu_info']['cpu_percent']}%")
        print(f"Memory Usage: {metrics['memory_info']['percent']}%")
        print("\nDisk Usage:")
        for mount, data in metrics['disk_info'].items():
            print(f"{mount}: {data['percent']}% used")
        print("="*50)

    def export_report(self):
        """Export monitoring history to CSV file."""
        if not self.history:
            print("No data to export")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.reports_dir / f"system_monitor_report_{timestamp}.csv"

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['Timestamp', 'CPU Usage (%)', 'Memory Usage (%)', 
                               'Memory Available (GB)', 'Memory Total (GB)'])
                
                # Write data
                for record in self.history:
                    writer.writerow([
                        record['timestamp'],
                        record['cpu_info']['cpu_percent'],
                        record['memory_info']['percent'],
                        round(record['memory_info']['available'] / (1024**3), 2),
                        round(record['memory_info']['total'] / (1024**3), 2)
                    ])
            
            print(f"\nReport exported to: {filename}")
        except Exception as e:
            print(f"Error exporting report: {e}")

def main():
    monitor = SystemResourceMonitor()
    try:
        monitor.start_monitoring(interval=2)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main() 