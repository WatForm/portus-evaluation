all:
	./get-expert-models.sh
	./remove-unneeded-files.py
	cd expert-models && ../fix-models.sh && cd ..
	./remove-unsupported.sh

clean:
	rm -rf expert-models
