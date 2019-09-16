all:	clean gen install
clean:
	find output/SSH/openssh/ -type f -delete
test:
	python ./compile-test.py
gen:
	python ./emuserema.py
install:
	cp output/SSH/openssh/* ~/.ssh/configs/
git:
	git add -A
	git commit -m "$$(date)"
	git push
