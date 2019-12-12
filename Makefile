all:	gen
gen:
	python ./bin/emuserema
git:
	git add -A
	git commit -m "$$(date)"
	git push
rel:
	rm dist/* || true
	vim setup.py
	python3 setup.py bdist_wheel
	python3 -m twine upload --repository pypi dist/*

