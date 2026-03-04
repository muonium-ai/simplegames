# Makefile for Slider Game

# --- Configuration ---
WORKSPACE   := Slider Game/Slider Game.xcodeproj/project.xcworkspace
SCHEME      := Slider Game
SDK         := iphonesimulator
DEVICE_NAME := iPhone 17
BUNDLE_ID   := muonium.Slider-Game

# --- Build Variables ---
BUILD_DIR      := build
DERIVED_DATA   := $(BUILD_DIR)/derivedData
APP_NAME       := Slider Game.app
APP_PATH       := $(DERIVED_DATA)/Build/Products/Debug-$(SDK)/$(APP_NAME)

# --- Commands ---
.PHONY: all preflight build install launch clean boot run relaunch get_sim_udid

all: run

preflight:
	@command -v xcodebuild >/dev/null 2>&1 || { echo "error: xcodebuild not found"; exit 1; }
	@command -v xcrun >/dev/null 2>&1 || { echo "error: xcrun not found"; exit 1; }
	@test -d "$(WORKSPACE)" || { echo "error: workspace not found at $(WORKSPACE)"; exit 1; }

# Boot the simulator if it's not already running
boot:
	@echo "--- Checking and booting '$(DEVICE_NAME)' simulator ---"
	@if ! xcrun simctl list devices | grep -q -E "$(DEVICE_NAME) .*\(Booted\)"; then \
		echo "Simulator not booted. Attempting to boot..."; \
		xcrun simctl boot "$(DEVICE_NAME)"; \
		sleep 10; \
	else \
		echo "Simulator '$(DEVICE_NAME)' is already booted."; \
	fi

# Build the application for the simulator
build: preflight
	@echo "--- Building $(SCHEME) for '$(DEVICE_NAME)' ---"
	@if command -v xcpretty >/dev/null 2>&1; then \
		xcodebuild \
			-workspace "$(WORKSPACE)" \
			-scheme "$(SCHEME)" \
			-sdk "$(SDK)" \
			-derivedDataPath "$(DERIVED_DATA)" \
			-destination "platform=iOS Simulator,name=$(DEVICE_NAME)" \
			clean build \
			| xcpretty; \
	else \
		echo "note: xcpretty not found; streaming raw xcodebuild output"; \
		xcodebuild \
			-workspace "$(WORKSPACE)" \
			-scheme "$(SCHEME)" \
			-sdk "$(SDK)" \
			-derivedDataPath "$(DERIVED_DATA)" \
			-destination "platform=iOS Simulator,name=$(DEVICE_NAME)" \
			clean build; \
	fi

# Install the application on the booted simulator
install:
	@echo "--- Installing $(APP_NAME) on '$(DEVICE_NAME)' ---"
	@xcrun simctl install booted "$(APP_PATH)"

# Launch the application on the simulator
launch:
	@echo "--- Launching $(BUNDLE_ID) on '$(DEVICE_NAME)' ---"
	@xcrun simctl launch booted $(BUNDLE_ID)

# Clean the build directory
clean: preflight
	@echo "--- Cleaning build artifacts ---"
	@rm -rf "$(BUILD_DIR)"
	@if command -v xcpretty >/dev/null 2>&1; then \
		xcodebuild -workspace "$(WORKSPACE)" -scheme "$(SCHEME)" clean | xcpretty; \
	else \
		echo "note: xcpretty not found; streaming raw xcodebuild output"; \
		xcodebuild -workspace "$(WORKSPACE)" -scheme "$(SCHEME)" clean; \
	fi

# A command to run everything in sequence
run: boot build install launch

# A command to reinstall and launch
relaunch: build install launch
