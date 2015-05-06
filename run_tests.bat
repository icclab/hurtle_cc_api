
pep8 -r --show-pep8 adapters api

pylint -i y -r n api adapters

nosetests --with-coverage --cover-erase --cover-package adapters,api