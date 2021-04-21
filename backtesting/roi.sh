#!/bin/bash

for i in `ls compare`
do
	echo $i >> out.file
	cat compare/$i |tail -1 |awk '{print $4}' >> out.file
done
