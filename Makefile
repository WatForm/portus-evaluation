all:
	./setup_scripts/get-expert-models.sh
	./setup_scripts/remove-unneeded-files.py
	cd expert-models && ../setup_scripts/fix-models.sh && cd ..
	./setup_scripts/remove-unsupported.sh
	./setup_scripts/compile-top-level-file-list.py
	./setup_scripts/compile-top-level-file-list-plus-command-number.py -r
	@echo TOP-LEVEL FILE LIST WITH COMMAND in: models-supported-command.txt

clean:
	rm -rf expert-models 
	rm -f models-supported.txt
	rm -f models-supported-command.txt
