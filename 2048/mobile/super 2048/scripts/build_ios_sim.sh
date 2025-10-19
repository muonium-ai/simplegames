#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_DIR}/.." && pwd)"
PROJECT_PATH="${PROJECT_DIR}/super 2048.xcodeproj"
SCHEME=${SCHEME:-"super 2048"}
CONFIGURATION=${CONFIGURATION:-"Debug"}
SDK=${SDK:-"iphonesimulator"}
DESTINATION=${DESTINATION:-"platform=iOS Simulator,name=iPhone 17"}
DERIVED_DATA_PATH=${DERIVED_DATA_PATH:-"${REPO_ROOT}/build/ios"}

mkdir -p "${DERIVED_DATA_PATH}"

xcodebuild \
  -project "${PROJECT_PATH}" \
  -scheme "${SCHEME}" \
  -configuration "${CONFIGURATION}" \
  -sdk "${SDK}" \
  -destination "${DESTINATION}" \
  -derivedDataPath "${DERIVED_DATA_PATH}" \
  build
