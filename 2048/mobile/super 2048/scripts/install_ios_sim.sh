#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_DIR}/.." && pwd)"
CONFIGURATION=${CONFIGURATION:-"Debug"}
DERIVED_DATA_PATH=${DERIVED_DATA_PATH:-"${REPO_ROOT}/build/ios"}
APP_NAME=${APP_NAME:-"super 2048"}
BUNDLE_ID=${BUNDLE_ID:-"muonium.super-2048"}
SIMULATOR_NAME=${SIMULATOR_NAME:-"iPhone 17"}
APP_PATH="${DERIVED_DATA_PATH}/Build/Products/${CONFIGURATION}-iphonesimulator/${APP_NAME}.app"

if [[ ! -d "${APP_PATH}" ]]; then
  echo "error: app bundle not found at ${APP_PATH}" >&2
  echo "hint: run scripts/build_ios_sim.sh first" >&2
  exit 1
fi

if ! xcrun simctl list devices "available" | grep -q "${SIMULATOR_NAME}"; then
  echo "error: simulator ${SIMULATOR_NAME} not found" >&2
  exit 1
fi

echo "Ensuring simulator ${SIMULATOR_NAME} is booted..."
xcrun simctl boot "${SIMULATOR_NAME}" >/dev/null 2>&1 || true
xcrun simctl bootstatus "${SIMULATOR_NAME}" -b >/dev/null

echo "Uninstalling previous build (if any)..."
xcrun simctl uninstall "${SIMULATOR_NAME}" "${BUNDLE_ID}" >/dev/null 2>&1 || true

echo "Installing ${APP_NAME}.app to ${SIMULATOR_NAME}..."
xcrun simctl install "${SIMULATOR_NAME}" "${APP_PATH}"

echo "Launching ${BUNDLE_ID}..."
xcrun simctl launch "${SIMULATOR_NAME}" "${BUNDLE_ID}" || true
