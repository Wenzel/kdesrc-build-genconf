# kdesrc-build-genconf

# Dependencies

- `Qt5`
- `Python 3`

# Setup

    virtualenv --always-copy venv
    pip install -r requirements.txt
    ./install_pyqt5.sh
    for i in `echo *.ui`; do pyuic5 $i -o ${i%.ui}.py ; done

# Usage

    ./kdesrc-build-genconf.py
