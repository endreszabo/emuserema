all:	gen
gen:
	python ./run.py
git:
	git add -A
	git commit -m "$$(date)"
	git push
