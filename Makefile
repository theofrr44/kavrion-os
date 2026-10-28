.PHONY: test iso verify zip
test:
	python3 tests/test_sysinfo.py && bash tests/check_repo.sh
iso:
	sudo scripts/build.sh --install-deps
verify:
	scripts/verify-iso.sh dist/kavrion-os-$$(cat VERSION)-amd64.iso
zip:
	cd .. && zip -qr kavrion-os-src-$$(cat kavrion-os/VERSION).zip kavrion-os -x 'kavrion-os/build/*' 'kavrion-os/dist/*' '*/__pycache__/*'
