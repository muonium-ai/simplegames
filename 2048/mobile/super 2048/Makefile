.PHONY: build-ios-sim install-ios-sim clean-ios

build-ios-sim:
	./scripts/build_ios_sim.sh

install-ios-sim: build-ios-sim
	./scripts/install_ios_sim.sh

clean-ios:
	rm -rf ../../build/ios
