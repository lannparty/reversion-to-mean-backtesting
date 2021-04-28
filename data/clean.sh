#!/bin/bash

for ticker in `cat tickers.csv`
do
  if [ ! -s "raw/$ticker.json" ]
  then
    echo "Empty file, removing"
    rm "raw/$ticker.json"
  fi
done

for ticker in `cat tickers.csv`
do
  if [ ! -s "test/$ticker.json" ]
  then
    echo "Empty file, removing"
    rm "test/$ticker.json"
  fi
done
