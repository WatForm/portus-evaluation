all:
	./setup_scripts/get-expert-models.sh
	./setup_scripts/remove-unneeded-files.py
	cd expert-models && ../setup_scripts/fix-models.sh && cd ..
	./setup_scripts/remove-unsupported.sh
	./setup_scripts/compile-top-level-file-list.py
	@echo TOP-LEVEL FILE LIST in: models-supported.txt

clean:
	rm -rf expert-models 
	rm -f models-supported.txt
