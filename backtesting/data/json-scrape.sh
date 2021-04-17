#!/bin/bash

for key in `cat keys.csv`
do
EXHAUSTED=0
  for ticker in `cat tickers.csv`
  do
    if test -f "raw/$ticker.json"
    then
      echo "$ticker exists, checking if data is good."
      if cat raw/$ticker.json |grep "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day."
      then
        echo "Bad data, removing."
        rm "raw/$ticker.json"
      fi

      if [ ! -s "raw/$ticker.json" ]
      then
        echo "Empty file, removing"
        rm "raw/$ticker.json"
      fi
    fi
  
    if ! test -f "raw/$ticker.json"
    then 
      echo "$ticker does not exist, scraping."
      curl "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=$ticker&outputsize=full&apikey=$key" > raw/$ticker.json
      echo "curl https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=$ticker&outputsize=full&apikey=$key > raw/$ticker.json"
      if cat raw/$ticker.json |grep "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day."
      then
        echo "Key exhausted"
        rm "raw/$ticker.json"
	EXHAUSTED=1
	break
      fi
    fi
    echo $EXHAUSTED EXHAUSTED
    if [ $EXHAUSTED -eq "1" ]
    then
      break
    fi
  done
done
