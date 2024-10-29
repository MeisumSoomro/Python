import zlib
import gzip
import zipfile
import tarfile
import os
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json
import shutil
from tqdm import tqdm

class CompressionAlgorithm:
    GZIP = "gzip"
    ZIP = "zip"
    TAR_GZ = "tar.gz"
    ZLIB = "zlib"

class CompressionStats:
    def __init__(self):
        self.original_size: int = 0
        self.compressed_size: int = 0
        self.compression_ratio: float = 0.0
        self.compression_time: float = 0.0
        self.algorithm: str = ""
        self.timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "original_size": self.original_size,
            "compressed_size": self.compressed_size,
            "compression_ratio": self.compression_ratio,
            "compression_time": self.compression_time,
            "algorithm": self.algorithm,
            "timestamp": self.timestamp
        }

class FileCompressor:
    def __init__(self):
        self.stats_file = Path("compression_history.json")
        self.compression_history: List[Dict] = []
        self.load_history()

    def compress_file(self, input_path: str, algorithm: str = CompressionAlgorithm.GZIP) -> Tuple[str, CompressionStats]:
        """Compress a file using the specified algorithm"""
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        stats = CompressionStats()
        stats.original_size = input_path.stat().st_size
        stats.algorithm = algorithm
        start_time = datetime.now()

        output_path = str(input_path) + self._get_extension(algorithm)

        try:
            if algorithm == CompressionAlgorithm.GZIP:
                self._compress_gzip(input_path, output_path)
            elif algorithm == CompressionAlgorithm.ZIP:
                self._compress_zip(input_path, output_path)
            elif algorithm == CompressionAlgorithm.TAR_GZ:
                self._compress_tar_gz(input_path, output_path)
            elif algorithm == CompressionAlgorithm.ZLIB:
                self._compress_zlib(input_path, output_path)
            else:
                raise ValueError(f"Unsupported compression algorithm: {algorithm}")

            stats.compression_time = (datetime.now() - start_time).total_seconds()
            stats.compressed_size = Path(output_path).stat().st_size
            stats.compression_ratio = (stats.original_size - stats.compressed_size) / stats.original_size * 100
            stats.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.compression_history.append(stats.to_dict())
            self.save_history()

            return output_path, stats

        except Exception as e:
            if Path(output_path).exists():
                Path(output_path).unlink()
            raise e

    def compress_directory(self, input_dir: str, algorithm: str = CompressionAlgorithm.ZIP) -> Tuple[str, CompressionStats]:
        """Compress an entire directory"""
        input_path = Path(input_dir)
        if not input_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {input_dir}")

        stats = CompressionStats()
        stats.algorithm = algorithm
        start_time = datetime.now()

        output_path = str(input_path) + self._get_extension(algorithm)

        try:
            if algorithm == CompressionAlgorithm.ZIP:
                self._compress_directory_zip(input_path, output_path)
            elif algorithm == CompressionAlgorithm.TAR_GZ:
                self._compress_directory_tar_gz(input_path, output_path)
            else:
                raise ValueError(f"Unsupported directory compression algorithm: {algorithm}")

            stats.compression_time = (datetime.now() - start_time).total_seconds()
            stats.original_size = self._get_directory_size(input_path)
            stats.compressed_size = Path(output_path).stat().st_size
            stats.compression_ratio = (stats.original_size - stats.compressed_size) / stats.original_size * 100
            stats.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.compression_history.append(stats.to_dict())
            self.save_history()

            return output_path, stats

        except Exception as e:
            if Path(output_path).exists():
                Path(output_path).unlink()
            raise e

    def _compress_gzip(self, input_path: Path, output_path: str):
        with open(input_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _compress_zip(self, input_path: Path, output_path: str):
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(input_path, input_path.name)

    def _compress_tar_gz(self, input_path: Path, output_path: str):
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(input_path, arcname=input_path.name)

    def _compress_zlib(self, input_path: Path, output_path: str):
        with open(input_path, 'rb') as f_in:
            data = f_in.read()
            compressed_data = zlib.compress(data)
            with open(output_path, 'wb') as f_out:
                f_out.write(compressed_data)

    def _compress_directory_zip(self, input_path: Path, output_path: str):
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(input_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(input_path.parent)
                    zipf.write(file_path, arcname)

    def _compress_directory_tar_gz(self, input_path: Path, output_path: str):
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(input_path, arcname=input_path.name)

    def _get_extension(self, algorithm: str) -> str:
        return {
            CompressionAlgorithm.GZIP: ".gz",
            CompressionAlgorithm.ZIP: ".zip",
            CompressionAlgorithm.TAR_GZ: ".tar.gz",
            CompressionAlgorithm.ZLIB: ".zlib"
        }[algorithm]

    def _get_directory_size(self, directory: Path) -> int:
        total_size = 0
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                total_size += file_path.stat().st_size
        return total_size

    def get_compression_history(self) -> List[Dict]:
        return self.compression_history

    def save_history(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.compression_history, f, indent=4)

    def load_history(self):
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.compression_history = json.load(f)
            except json.JSONDecodeError:
                self.compression_history = []

def main():
    compressor = FileCompressor()
    
    while True:
        print("\nFile Compression Tool")
        print("1. Compress File")
        print("2. Compress Directory")
        print("3. View Compression History")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            file_path = input("Enter file path: ")
            print("\nAvailable algorithms:")
            print("1. GZIP")
            print("2. ZIP")
            print("3. TAR.GZ")
            print("4. ZLIB")
            
            algo_choice = input("Choose algorithm (1-4): ")
            algorithm = {
                "1": CompressionAlgorithm.GZIP,
                "2": CompressionAlgorithm.ZIP,
                "3": CompressionAlgorithm.TAR_GZ,
                "4": CompressionAlgorithm.ZLIB
            }.get(algo_choice, CompressionAlgorithm.GZIP)
            
            try:
                output_path, stats = compressor.compress_file(file_path, algorithm)
                print(f"\nCompression completed!")
                print(f"Output file: {output_path}")
                print(f"Original size: {stats.original_size:,} bytes")
                print(f"Compressed size: {stats.compressed_size:,} bytes")
                print(f"Compression ratio: {stats.compression_ratio:.2f}%")
                print(f"Time taken: {stats.compression_time:.2f} seconds")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == "2":
            dir_path = input("Enter directory path: ")
            print("\nAvailable algorithms:")
            print("1. ZIP")
            print("2. TAR.GZ")
            
            algo_choice = input("Choose algorithm (1-2): ")
            algorithm = {
                "1": CompressionAlgorithm.ZIP,
                "2": CompressionAlgorithm.TAR_GZ
            }.get(algo_choice, CompressionAlgorithm.ZIP)
            
            try:
                output_path, stats = compressor.compress_directory(dir_path, algorithm)
                print(f"\nCompression completed!")
                print(f"Output file: {output_path}")
                print(f"Original size: {stats.original_size:,} bytes")
                print(f"Compressed size: {stats.compressed_size:,} bytes")
                print(f"Compression ratio: {stats.compression_ratio:.2f}%")
                print(f"Time taken: {stats.compression_time:.2f} seconds")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == "3":
            history = compressor.get_compression_history()
            if not history:
                print("No compression history found!")
                continue
                
            print("\nCompression History:")
            print("-" * 80)
            for entry in history:
                print(f"Timestamp: {entry['timestamp']}")
                print(f"Algorithm: {entry['algorithm']}")
                print(f"Original size: {entry['original_size']:,} bytes")
                print(f"Compressed size: {entry['compressed_size']:,} bytes")
                print(f"Compression ratio: {entry['compression_ratio']:.2f}%")
                print(f"Time taken: {entry['compression_time']:.2f} seconds")
                print("-" * 40)
        
        elif choice == "4":
            print("Thank you for using File Compression Tool!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 