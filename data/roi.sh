#!/bin/bash

for i in `ls test`
do
  echo $i $x $y
  x=100000
  y=`cat test/$i |tail -1 |awk '{print $4}'`
done
