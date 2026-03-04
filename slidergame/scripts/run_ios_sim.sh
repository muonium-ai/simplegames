#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

CONFIGURATION=${CONFIGURATION:-"Debug"}
DERIVED_DATA_PATH=${DERIVED_DATA_PATH:-"${PROJECT_DIR}/build/ios"}
APP_NAME="Slider Game"
BUNDLE_ID="muonium.Slider-Game"
SIMULATOR_NAME=${SIMULATOR_NAME:-"iPhone 17"}
APP_PATH="${DERIVED_DATA_PATH}/Build/Products/${CONFIGURATION}-iphonesimulator/${APP_NAME}.app"

if ! command -v xcrun >/dev/null 2>&1; then
  echo "error: xcrun not found; install Xcode command line tools" >&2
  exit 1
fi

if [[ ! -d "${APP_PATH}" ]]; then
  echo "error: app bundle not found at ${APP_PATH}" >&2
  echo "hint: run scripts/build_ios_sim.sh first" >&2
  exit 1
fi

SIMULATOR_UDID="$(xcrun simctl list devices "available" | awk -v name="${SIMULATOR_NAME}" '
  /^[[:space:]]/ {
    line = $0
    sub(/^[[:space:]]+/, "", line)
    split(line, parts, " \\(")
    device_name = parts[1]
    if (device_name != name) {
      next
    }
    if (match(line, /\([0-9A-F-]+\)/)) {
      print substr(line, RSTART + 1, RLENGTH - 2)
      exit
    }
  }
')"

if [[ -z "${SIMULATOR_UDID}" ]]; then
  echo "error: simulator ${SIMULATOR_NAME} not found" >&2
  exit 1
fi

echo "Using simulator ${SIMULATOR_NAME} (${SIMULATOR_UDID})"
echo "Ensuring simulator is booted..."
xcrun simctl boot "${SIMULATOR_UDID}" >/dev/null 2>&1 || true
xcrun simctl bootstatus "${SIMULATOR_UDID}" -b >/dev/null

echo "Uninstalling previous build (if any)..."
xcrun simctl uninstall "${SIMULATOR_UDID}" "${BUNDLE_ID}" >/dev/null 2>&1 || true

echo "Installing ${APP_NAME}.app to ${SIMULATOR_NAME}..."
xcrun simctl install "${SIMULATOR_UDID}" "${APP_PATH}"

echo "Launching ${BUNDLE_ID}..."
if ! xcrun simctl launch "${SIMULATOR_UDID}" "${BUNDLE_ID}"; then
  echo "warning: app install completed but launch command failed" >&2
fi
