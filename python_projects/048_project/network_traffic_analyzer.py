import scapy.all as scapy
from scapy.layers import http
from pathlib import Path
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
import threading
import queue
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import time

class PacketType:
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    DNS = "DNS"
    OTHER = "OTHER"

class NetworkAnalyzer:
    def __init__(self):
        self.log_file = Path("network_analysis.log")
        self.stats_file = Path("traffic_stats.json")
        self.capture_active = False
        self.packet_queue = queue.Queue()
        self.stats = {
            "total_packets": 0,
            "protocols": {},
            "ip_addresses": {},
            "ports": {},
            "packet_sizes": [],
            "timestamps": []
        }
        self.setup_logging()
        self.load_stats()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_stats(self):
        """Load previous traffic statistics"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except json.JSONDecodeError:
                logging.error("Error loading statistics file")

    def save_stats(self):
        """Save traffic statistics"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=4)

    def start_capture(self, interface: str = None):
        """Start packet capture"""
        self.capture_active = True
        self.capture_thread = threading.Thread(
            target=self._capture_packets,
            args=(interface,)
        )
        self.capture_thread.start()
        self.analysis_thread = threading.Thread(
            target=self._analyze_packets
        )
        self.analysis_thread.start()
        logging.info("Packet capture started")

    def stop_capture(self):
        """Stop packet capture"""
        self.capture_active = False
        self.capture_thread.join()
        self.analysis_thread.join()
        self.save_stats()
        logging.info("Packet capture stopped")

    def _capture_packets(self, interface: Optional[str]):
        """Capture network packets"""
        try:
            scapy.sniff(
                iface=interface,
                store=False,
                prn=lambda x: self.packet_queue.put(x),
                stop_filter=lambda x: not self.capture_active
            )
        except Exception as e:
            logging.error(f"Error capturing packets: {e}")
            self.capture_active = False

    def _analyze_packets(self):
        """Analyze captured packets"""
        while self.capture_active or not self.packet_queue.empty():
            try:
                packet = self.packet_queue.get(timeout=1)
                self._process_packet(packet)
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error analyzing packet: {e}")

    def _process_packet(self, packet):
        """Process individual packet"""
        self.stats["total_packets"] += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stats["timestamps"].append(timestamp)

        # Get protocol
        protocol = self._get_protocol(packet)
        self.stats["protocols"][protocol] = self.stats["protocols"].get(protocol, 0) + 1

        # Get IP addresses
        if scapy.IP in packet:
            src_ip = packet[scapy.IP].src
            dst_ip = packet[scapy.IP].dst
            self.stats["ip_addresses"][src_ip] = self.stats["ip_addresses"].get(src_ip, 0) + 1
            self.stats["ip_addresses"][dst_ip] = self.stats["ip_addresses"].get(dst_ip, 0) + 1

        # Get ports
        if scapy.TCP in packet:
            src_port = packet[scapy.TCP].sport
            dst_port = packet[scapy.TCP].dport
            self.stats["ports"][src_port] = self.stats["ports"].get(src_port, 0) + 1
            self.stats["ports"][dst_port] = self.stats["ports"].get(dst_port, 0) + 1

        # Get packet size
        self.stats["packet_sizes"].append(len(packet))

    def _get_protocol(self, packet) -> str:
        """Determine packet protocol"""
        if scapy.TCP in packet:
            if packet[scapy.TCP].dport == 80 or packet[scapy.TCP].sport == 80:
                return PacketType.HTTP
            elif packet[scapy.TCP].dport == 443 or packet[scapy.TCP].sport == 443:
                return PacketType.HTTPS
            return PacketType.TCP
        elif scapy.UDP in packet:
            if packet[scapy.UDP].dport == 53 or packet[scapy.UDP].sport == 53:
                return PacketType.DNS
            return PacketType.UDP
        elif scapy.ICMP in packet:
            return PacketType.ICMP
        return PacketType.OTHER

    def get_protocol_stats(self) -> Dict:
        """Get protocol statistics"""
        return self.stats["protocols"]

    def get_ip_stats(self) -> Dict:
        """Get IP address statistics"""
        return self.stats["ip_addresses"]

    def get_port_stats(self) -> Dict:
        """Get port statistics"""
        return self.stats["ports"]

    def get_packet_size_stats(self) -> Dict:
        """Get packet size statistics"""
        sizes = self.stats["packet_sizes"]
        if not sizes:
            return {}
        return {
            "min": min(sizes),
            "max": max(sizes),
            "avg": sum(sizes) / len(sizes)
        }

    def plot_protocol_distribution(self, output_path: Optional[str] = None):
        """Plot protocol distribution"""
        protocols = self.get_protocol_stats()
        if not protocols:
            return

        plt.figure(figsize=(10, 6))
        plt.pie(protocols.values(), labels=protocols.keys(), autopct='%1.1f%%')
        plt.title("Protocol Distribution")
        
        if output_path:
            plt.savefig(output_path)
            logging.info(f"Protocol distribution plot saved to {output_path}")
        else:
            plt.show()
        plt.close()

    def plot_traffic_over_time(self, output_path: Optional[str] = None):
        """Plot traffic volume over time"""
        if not self.stats["timestamps"]:
            return

        df = pd.DataFrame({
            'timestamp': pd.to_datetime(self.stats["timestamps"]),
            'count': 1
        })
        df = df.set_index('timestamp').resample('1min').count()

        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['count'])
        plt.title("Traffic Volume Over Time")
        plt.xlabel("Time")
        plt.ylabel("Packets per Minute")
        plt.xticks(rotation=45)
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path)
            logging.info(f"Traffic volume plot saved to {output_path}")
        else:
            plt.show()
        plt.close()

    def plot_packet_sizes(self, output_path: Optional[str] = None):
        """Plot packet size distribution"""
        if not self.stats["packet_sizes"]:
            return

        plt.figure(figsize=(10, 6))
        plt.hist(self.stats["packet_sizes"], bins=50)
        plt.title("Packet Size Distribution")
        plt.xlabel("Packet Size (bytes)")
        plt.ylabel("Frequency")

        if output_path:
            plt.savefig(output_path)
            logging.info(f"Packet size distribution plot saved to {output_path}")
        else:
            plt.show()
        plt.close()

def main():
    analyzer = NetworkAnalyzer()
    
    while True:
        print("\nNetwork Traffic Analyzer")
        print("1. Start Capture")
        print("2. Stop Capture")
        print("3. Show Protocol Stats")
        print("4. Show IP Stats")
        print("5. Show Port Stats")
        print("6. Show Packet Size Stats")
        print("7. Plot Protocol Distribution")
        print("8. Plot Traffic Over Time")
        print("9. Plot Packet Sizes")
        print("10. Exit")
        
        choice = input("\nEnter your choice (1-10): ")
        
        if choice == "1":
            if analyzer.capture_active:
                print("Capture already running!")
                continue
            
            interface = input("Enter interface name (leave empty for default): ").strip()
            analyzer.start_capture(interface if interface else None)
            print("Packet capture started...")
        
        elif choice == "2":
            if not analyzer.capture_active:
                print("No capture running!")
                continue
            
            analyzer.stop_capture()
            print("Packet capture stopped.")
        
        elif choice == "3":
            stats = analyzer.get_protocol_stats()
            if stats:
                print("\nProtocol Statistics:")
                for protocol, count in stats.items():
                    print(f"{protocol}: {count} packets")
            else:
                print("No protocol statistics available!")
        
        elif choice == "4":
            stats = analyzer.get_ip_stats()
            if stats:
                print("\nTop IP Addresses:")
                sorted_ips = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]
                for ip, count in sorted_ips:
                    print(f"{ip}: {count} packets")
            else:
                print("No IP statistics available!")
        
        elif choice == "5":
            stats = analyzer.get_port_stats()
            if stats:
                print("\nTop Ports:")
                sorted_ports = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]
                for port, count in sorted_ports:
                    print(f"Port {port}: {count} packets")
            else:
                print("No port statistics available!")
        
        elif choice == "6":
            stats = analyzer.get_packet_size_stats()
            if stats:
                print("\nPacket Size Statistics:")
                print(f"Minimum: {stats['min']} bytes")
                print(f"Maximum: {stats['max']} bytes")
                print(f"Average: {stats['avg']:.2f} bytes")
            else:
                print("No packet size statistics available!")
        
        elif choice == "7":
            save = input("Save plot to file? (y/n): ").lower() == 'y'
            if save:
                output_path = input("Enter output file path: ")
                analyzer.plot_protocol_distribution(output_path)
            else:
                analyzer.plot_protocol_distribution()
        
        elif choice == "8":
            save = input("Save plot to file? (y/n): ").lower() == 'y'
            if save:
                output_path = input("Enter output file path: ")
                analyzer.plot_traffic_over_time(output_path)
            else:
                analyzer.plot_traffic_over_time()
        
        elif choice == "9":
            save = input("Save plot to file? (y/n): ").lower() == 'y'
            if save:
                output_path = input("Enter output file path: ")
                analyzer.plot_packet_sizes(output_path)
            else:
                analyzer.plot_packet_sizes()
        
        elif choice == "10":
            if analyzer.capture_active:
                analyzer.stop_capture()
            print("Thank you for using Network Traffic Analyzer!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 