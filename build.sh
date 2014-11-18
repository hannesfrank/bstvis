#!/usr/bin/env bash

source /etc/bash_completion.d/virtualenvwrapper
workon pyBSTViewer

# running unittests with coverage
coverage run --branch --source=. --omit=test* -m unittest discover -s tests/

# reporting coverage
coverage report

# generating html report
coverage html
# and open in browser (if executed locally)
# xdg-open htmlcov/index.html

# copy result to webspace
mv -T htmlcov/ /home/hannes/www/coverage/pyBSTViewer/
# TODO maybe use pyBSTViewer/latest and keep versions

deactivate