import PySimpleGUI as sg
import psutil
import matplotlib.pyplot as plt
import io
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import threading
import time
from collections import deque
import pandas as pd

class SystemMonitor:
    def __init__(self, history_length: int = 60):
        self.history_length = history_length
        self.cpu_history = deque(maxlen=history_length)
        self.memory_history = deque(maxlen=history_length)
        self.timestamps = deque(maxlen=history_length)
        self.monitoring = False
        self.alert_thresholds = {
            'cpu': 80.0,  # Alert if CPU usage > 80%
            'memory': 80.0,  # Alert if memory usage > 80%
            'disk': 90.0  # Alert if disk usage > 90%
        }
    
    def start_monitoring(self):
        self.monitoring = True
    
    def stop_monitoring(self):
        self.monitoring = False
    
    def get_cpu_info(self) -> Dict:
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_history.append(cpu_percent)
        self.timestamps.append(datetime.now())
        
        return {
            'percent': cpu_percent,
            'count': psutil.cpu_count(),
            'freq': psutil.cpu_freq().current
        }
    
    def get_memory_info(self) -> Dict:
        memory = psutil.virtual_memory()
        self.memory_history.append(memory.percent)
        
        return {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent,
            'used': memory.used
        }
    
    def get_disk_info(self) -> List[Dict]:
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except:
                continue
        return disks
    
    def get_network_info(self) -> Dict:
        network = psutil.net_io_counters()
        return {
            'bytes_sent': network.bytes_sent,
            'bytes_recv': network.bytes_recv,
            'packets_sent': network.packets_sent,
            'packets_recv': network.packets_recv
        }
    
    def get_process_list(self) -> List[Dict]:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except:
                continue
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)
    
    def create_usage_graph(self) -> Optional[bytes]:
        try:
            plt.figure(figsize=(10, 4))
            plt.plot(list(self.timestamps), list(self.cpu_history), label='CPU')
            plt.plot(list(self.timestamps), list(self.memory_history), label='Memory')
            plt.title('System Resource Usage')
            plt.xlabel('Time')
            plt.ylabel('Usage %')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='PNG')
            plt.close()
            return buf.getvalue()
        except:
            return None
    
    def check_alerts(self) -> List[str]:
        alerts = []
        
        # Check CPU
        if self.cpu_history and self.cpu_history[-1] > self.alert_thresholds['cpu']:
            alerts.append(f"High CPU usage: {self.cpu_history[-1]:.1f}%")
        
        # Check Memory
        memory = psutil.virtual_memory()
        if memory.percent > self.alert_thresholds['memory']:
            alerts.append(f"High memory usage: {memory.percent:.1f}%")
        
        # Check Disk
        for disk in self.get_disk_info():
            if disk['percent'] > self.alert_thresholds['disk']:
                alerts.append(f"High disk usage on {disk['mountpoint']}: {disk['percent']:.1f}%")
        
        return alerts

def create_layout():
    return [
        [sg.Text("System Monitor", font=("Helvetica", 16))],
        [
            sg.Frame("CPU & Memory", [
                [sg.Text("CPU Usage: ", key="-CPU-")],
                [sg.Text("Memory Usage: ", key="-MEMORY-")],
                [sg.Image(key="-GRAPH-")]
            ])
        ],
        [
            sg.Frame("Disk Usage", [
                [sg.Table(
                    values=[],
                    headings=["Device", "Mount", "Total", "Used", "Free", "%"],
                    auto_size_columns=True,
                    num_rows=3,
                    key="-DISK-TABLE-"
                )]
            ])
        ],
        [
            sg.Frame("Network", [
                [sg.Text("Bytes Sent: ", key="-BYTES-SENT-")],
                [sg.Text("Bytes Received: ", key="-BYTES-RECV-")]
            ])
        ],
        [
            sg.Frame("Processes", [
                [sg.Table(
                    values=[],
                    headings=["PID", "Name", "CPU %", "Memory %"],
                    auto_size_columns=True,
                    num_rows=5,
                    key="-PROCESS-TABLE-"
                )]
            ])
        ],
        [
            sg.Button("Start Monitoring"),
            sg.Button("Stop Monitoring"),
            sg.Button("Export Data"),
            sg.Button("Exit")
        ]
    ]

def format_bytes(bytes_num: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024:
            return f"{bytes_num:.1f} {unit}"
        bytes_num /= 1024
    return f"{bytes_num:.1f} PB"

def monitoring_thread(window, monitor):
    while monitor.monitoring:
        # Get system info
        cpu_info = monitor.get_cpu_info()
        memory_info = monitor.get_memory_info()
        disk_info = monitor.get_disk_info()
        network_info = monitor.get_network_info()
        process_info = monitor.get_process_list()[:5]  # Top 5 processes
        
        # Check for alerts
        alerts = monitor.check_alerts()
        
        # Update window
        window.write_event_value('-UPDATE-', {
            'cpu': cpu_info,
            'memory': memory_info,
            'disk': disk_info,
            'network': network_info,
            'processes': process_info,
            'alerts': alerts
        })
        
        time.sleep(1)

def main():
    monitor = SystemMonitor()
    window = sg.Window("System Monitor", create_layout(), resizable=True, finalize=True)
    
    while True:
        event, values = window.read(timeout=100)
        
        if event in (sg.WIN_CLOSED, "Exit"):
            monitor.stop_monitoring()
            break
        
        if event == "Start Monitoring":
            monitor.start_monitoring()
            threading.Thread(target=monitoring_thread, args=(window, monitor), daemon=True).start()
            
        if event == "Stop Monitoring":
            monitor.stop_monitoring()
        
        if event == "Export Data":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data = {
                'Timestamp': list(monitor.timestamps),
                'CPU_Usage': list(monitor.cpu_history),
                'Memory_Usage': list(monitor.memory_history)
            }
            df = pd.DataFrame(data)
            df.to_csv(f"system_monitor_{timestamp}.csv", index=False)
            sg.popup(f"Data exported to system_monitor_{timestamp}.csv")
        
        if event == '-UPDATE-':
            data = values['-UPDATE-']
            
            # Update CPU & Memory
            window['-CPU-'].update(f"CPU Usage: {data['cpu']['percent']:.1f}%")
            window['-MEMORY-'].update(f"Memory Usage: {data['memory']['percent']:.1f}%")
            
            # Update graph
            graph_data = monitor.create_usage_graph()
            if graph_data:
                window['-GRAPH-'].update(data=graph_data)
            
            # Update disk table
            disk_data = [
                [
                    d['device'],
                    d['mountpoint'],
                    format_bytes(d['total']),
                    format_bytes(d['used']),
                    format_bytes(d['free']),
                    f"{d['percent']}%"
                ]
                for d in data['disk']
            ]
            window['-DISK-TABLE-'].update(disk_data)
            
            # Update network info
            window['-BYTES-SENT-'].update(f"Bytes Sent: {format_bytes(data['network']['bytes_sent'])}")
            window['-BYTES-RECV-'].update(f"Bytes Received: {format_bytes(data['network']['bytes_recv'])}")
            
            # Update process table
            process_data = [
                [p['pid'], p['name'], f"{p['cpu_percent']:.1f}%", f"{p['memory_percent']:.1f}%"]
                for p in data['processes']
            ]
            window['-PROCESS-TABLE-'].update(process_data)
            
            # Show alerts
            if data['alerts']:
                sg.popup_no_wait("\n".join(data['alerts']), title="System Alerts")
    
    window.close()

if __name__ == "__main__":
    main() 