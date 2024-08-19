# Description: Makefile for Nextflow pipeline development

.PHONY: clean md5sum test run-test

clean:
	rm -rf work/ testing/output .nextflow.log* .nextflow/

md5sum:
	bash assets/test/md5.sh

run-test:
	nextflow run main.nf -profile test,mamba

test: clean
	$(MAKE) run-test
	$(MAKE) md5sum

