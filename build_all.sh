#!/bin/bash

echo "USB-Monitor Cross-Platform Build"
echo "================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed!"
    echo "Please install Python 3.9+ and try again."
    exit 1
fi

echo "Starting cross-platform build..."
echo "This will create both Windows .exe and macOS .app files!"
echo

python3 build_cross_platform.py

echo
echo "Build completed!"
