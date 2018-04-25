package main

import (
	"fmt"
	. "fugger-junior/pump-n-dump/dao"
	"log"
	"strings"
	"time"
)

var dao = MarketsDAO{}

func getValues() ([]time.Time, []float64) {
	var dates []time.Time
	var prices []float64

	summaries, err := dao.FindAll("BTC-TRX")
	if err != nil {
		log.Fatal(err)
	}

	for _, summary := range summaries {
		fmt.Println(summary.TimeStamp)
		timeString := strings.Split(summary.TimeStamp, "T0")
		newTimeString := timeString[0] + "T" + timeString[1]

		parsed, err := time.Parse("2006-01-02T15:04:05", newTimeString)
		if err != nil {
			log.Fatal(err)
		}

		dates = append(dates, parsed)
		prices = append(prices, summary.Last)
	}

	return dates, prices
}

func init() {
	dao.Server = "localhost"
	dao.Database = "markets_db"
	dao.Connect()
}

func main() {
	dates, prices := getValues()

	fmt.Println(dates)
	fmt.Println(prices)
}
