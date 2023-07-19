# ----- Test Targets -----
rise-test: CONT_ID ?= $(shell docker ps -q | head -n 1 )
rise-test: TOKEN ?= $(shell docker exec $(CONT_ID) jupyter lab list 2>&1 | grep -o "token=[^ ]*" | cut -d= -f2)
rise-test:
	python3 rise_test.py $(TOKEN)

checksum-test: CHECKSUM ?= $(shell make -C .. checksum )
checksum-test: CORRECT_CHECKSUM ?= $(shell cat ../base/checksum )
checksum-test:
ifeq ($(CHECKSUM),$(CORRECT_CHECKSUM))
	@echo "Checksum Test Passed"
else
	@echo "Checksum Test Failed"
	@echo "Expected: $(CORRECT_CHECKSUM)"
	@echo "Got: $(CHECKSUM)"
	exit 1
endif

#screenshots-test: screenshots
screenshots-test:
	python3 screenshots_diff.py

base_screenshots: screenshots-test
base_screenshots:
	mv *.png base_screenshots

clean:
	rm -rf *.png
	rm -rf *.ipynb
	rm -rf .ipynb_checkpoints


