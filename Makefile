unittests: 
	venv/bin/python3 -m unittest test/test_*.py

.PHONY: inttests
inttests: 
	venv/bin/python3 -m unittest inttest/itest_*.py

.PHONY: venv
venv:
	if [ ! -d "venv" ]; then python3 -m venv venv; fi
	venv/bin/pip3 install -r requirements.txt
