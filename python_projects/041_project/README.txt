File Compression Tool
===================

Project Structure:
----------------
041_project/
├── file_compression_tool.py    # Main program file
├── compression_history.json    # Compression history storage (created on first use)
└── README.txt                  # This file

Requirements:
------------
1. Python 3.7 or higher
2. Required Python packages:
   - tqdm (for progress bars)

Installation:
------------
1. Install the required package:
   pip install tqdm

Features:
--------
1. File Compression
   - Support for multiple compression algorithms:
     * GZIP
     * ZIP
     * TAR.GZ
     * ZLIB
   - Progress tracking
   - Compression statistics

2. Directory Compression
   - Compress entire directories
   - Support for ZIP and TAR.GZ formats
   - Maintains directory structure

3. Compression History
   - Tracks all compression operations
   - Stores statistics and metrics
   - Viewable compression history

4. Statistics Tracking
   - Original file size
   - Compressed size
   - Compression ratio
   - Processing time

Supported Algorithms:
------------------
1. GZIP (.gz)
   - Best for single text files
   - Good compression ratio

2. ZIP (.zip)
   - Supports multiple files
   - Widely compatible
   - Good for directories

3. TAR.GZ (.tar.gz)
   - Unix-style archive
   - Excellent compression
   - Preserves permissions

4. ZLIB (.zlib)
   - Raw compression
   - Minimal overhead
   - Good for small files

Usage:
-----
1. Run the program:
   python file_compression_tool.py

2. Choose operation:
   - Compress File
   - Compress Directory
   - View History

3. Select compression algorithm

4. Provide file/directory path

5. View results and statistics

Notes:
-----
- Compressed files are saved in the same directory as the input
- History is automatically saved after each operation
- Original files are preserved

Troubleshooting:
--------------
1. "File not found": Check if the path is correct
2. "Permission denied": Check file permissions
3. "Not a directory": Ensure path is a directory for directory compression

For Support:
----------
[Your contact information or repository link here] 