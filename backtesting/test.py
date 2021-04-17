#!/bin/bash

for i in `cat data/tickers.csv`
do
  python3 more_liver.py $i > data/test/$i.txt
done

