#!/bin/bash
BASEPATH=$HOME/app/xindex
rm -f $BASEPATH/doc/*.html
txt2tags -t html t2t/*.t2t
