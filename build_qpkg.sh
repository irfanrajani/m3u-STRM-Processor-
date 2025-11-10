#!/bin/bash
set -e

# Check if QDK_DIR is set
if [ -z "$QDK_DIR" ]; then
    echo "QDK_DIR is not set. Please set it to your QDK installation directory."
    exit 1
fi

# Define project and build directories
PROJECT_DIR=$(pwd)
BUILD_DIR="$PROJECT_DIR/build"
PACKAGE_DIR="$PROJECT_DIR/qnap"

# Clean up previous builds
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Run QDK build command
"$QDK_DIR/bin/qbuild" --root "$PACKAGE_DIR" --build-dir "$BUILD_DIR"

echo "QPKG has been built in $BUILD_DIR"