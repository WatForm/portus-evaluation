all:
	./setup_scripts/get-expert-models.sh
	python3 ./setup_scripts/remove-unneeded-files.py
	cd expert-models && ../setup_scripts/fix-models.sh && cd ..
	python3 ./setup_scripts/remove-unsupported.py
	python3 ./setup_scripts/compile-top-level-file-list.py
	python3 ./setup_scripts/compile-top-level-file-list-plus-command-number.py -r
	@echo TOP-LEVEL FILE LIST WITH COMMAND in: models-supported-command.txt

alloy2smt:
	./setup_scripts/get-expert-models.sh
	python3 ./setup_scripts/remove-unneeded-files.py
	cd expert-models && ../setup_scripts/fix-models.sh && cd ..
	python3 ./setup_scripts/compile-top-level-file-list.py
	@echo TOP-LEVEL FILE LIST WITH COMMAND in: models-supported-command.txt	

clean:
	rm -rf expert-models 
	rm -f models-supported.txt
	rm -f models-supported-command.txt
	rm tmp.smt2
