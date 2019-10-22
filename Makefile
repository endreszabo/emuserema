all:	gen
gen:
	python ./emuserema.py
git:
	git add -A
	git commit -m "$$(date)"
	git push
