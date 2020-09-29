.PHONY: venv freeze requirements install run

all: venv requirements run

venv:
	python3 -m venv venv

requirements:
	. venv/bin/activate 						;\
	pip install -r requirements.txt

run: guard-TOKEN
	. venv/bin/activate 						;\
	python main.py

install:
	. venv/bin/activate 						;\
	pip install PyGithub 						;\
	pip install yamale							;\
	pip freeze > requirements.txt

clean:
	rm -rf venv

guard-%:
	@ if [ "${${*}}" = "" ]; then 				\
		echo "Environment variable $* not set"	;\
		exit 1									;\
	fi
