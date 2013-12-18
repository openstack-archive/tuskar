#!/bin/sh
TEMPDIR=`mktemp -d`
CFGFILE=tuskar.conf.sample
tools/config/generate_sample.sh -b ./ -p tuskar -o $TEMPDIR
if ! diff $TEMPDIR/$CFGFILE etc/tuskar/$CFGFILE
then
    echo "E: tuskar.conf.sample is not up to date, please run tools/config/generate_sample.sh"
    exit 42
fi
