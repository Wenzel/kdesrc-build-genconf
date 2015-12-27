#!/bin/bash

# check for virtualenv
python -c 'import sys; print(sys.real_prefix)' > /dev/null 2>&1 || exit 1

TEMP=`mktemp -d`
echo $TEMP

# install SIP
SIP_VER="sip-4.17"
cd $TEMP
wget http://sourceforge.net/projects/pyqt/files/sip/"$SIP_VER"/"$SIP_VER".tar.gz
tar xzf "$SIP_VER".tar.gz
cd $SIP_VER
python configure.py
make
make install

# install PyQt5
PYQT_VER="PyQt-gpl-5.5.1"
cd $TEMP
wget http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.5.1/"$PYQT_VER".tar.gz
tar xzf "$PYQT_VER".tar.gz
cd $PYQT_VER
python configure.py --qmake $(which qmake-qt5)
make -j4
make install

