#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

CONFIGURATION=${CONFIGURATION:-"Debug"}
DERIVED_DATA_PATH=${DERIVED_DATA_PATH:-"${PROJECT_DIR}/build/ios"}
WORKSPACE_PATH="${PROJECT_DIR}/Slider Game/Slider Game.xcodeproj/project.xcworkspace"
SCHEME="Slider Game"

echo "Building ${SCHEME} for iOS Simulator..."
echo "Configuration: ${CONFIGURATION}"
echo "Derived Data Path: ${DERIVED_DATA_PATH}"

xcodebuild \
  -workspace "${WORKSPACE_PATH}" \
  -scheme "${SCHEME}" \
  -configuration "${CONFIGURATION}" \
  -sdk iphonesimulator \
  -derivedDataPath "${DERIVED_DATA_PATH}" \
  clean build \
  | xcpretty
