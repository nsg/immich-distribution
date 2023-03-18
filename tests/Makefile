
test: .env/bin/seleniumbase
	pytest tests_selenium.py --server=127.0.0.1 --port=4444 --headed

.env:
	virtualenv .env

.env/bin/seleniumbase: .env
	pip install -r requirements.txt
