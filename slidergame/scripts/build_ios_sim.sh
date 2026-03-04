#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

CONFIGURATION=${CONFIGURATION:-"Debug"}
DERIVED_DATA_PATH=${DERIVED_DATA_PATH:-"${PROJECT_DIR}/build/ios"}
WORKSPACE_PATH="${PROJECT_DIR}/Slider Game/Slider Game.xcodeproj/project.xcworkspace"
SCHEME="Slider Game"

if ! command -v xcodebuild >/dev/null 2>&1; then
  echo "error: xcodebuild not found; install Xcode command line tools" >&2
  exit 1
fi

if [[ ! -d "${WORKSPACE_PATH}" ]]; then
  echo "error: workspace not found at ${WORKSPACE_PATH}" >&2
  exit 1
fi

echo "Building ${SCHEME} for iOS Simulator..."
echo "Configuration: ${CONFIGURATION}"
echo "Derived Data Path: ${DERIVED_DATA_PATH}"

if command -v xcpretty >/dev/null 2>&1; then
  xcodebuild \
    -workspace "${WORKSPACE_PATH}" \
    -scheme "${SCHEME}" \
    -configuration "${CONFIGURATION}" \
    -sdk iphonesimulator \
    -derivedDataPath "${DERIVED_DATA_PATH}" \
    clean build \
    | xcpretty
else
  echo "note: xcpretty not found; streaming raw xcodebuild output" >&2
  xcodebuild \
    -workspace "${WORKSPACE_PATH}" \
    -scheme "${SCHEME}" \
    -configuration "${CONFIGURATION}" \
    -sdk iphonesimulator \
    -derivedDataPath "${DERIVED_DATA_PATH}" \
    clean build
fi
