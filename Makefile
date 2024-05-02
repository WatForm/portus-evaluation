all:
	./get-expert-models.sh
	./remove-unsupported.sh
	cd expert-models
	../fix-models
	cd ..

clean:
	rm -rf expert-models
