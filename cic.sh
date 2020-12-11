#!/bin/bash

cd /export/witham3/etools
export PATH=~/anaconda2/bin:$PATH
. ~/.bashrc
conda activate cic
python3 cic.py /p/user_pub/inconsistencies/ /export/witham3/cmor/
