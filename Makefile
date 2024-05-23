all:
	./get-expert-models.sh
	./remove-unneeded-files.py
	./remove-unsupported.sh
	cd expert-models && ../fix-models.sh && cd ..

clean:
	rm -rf expert-models
