package main

import (
	"fmt"
	. "fugger-junior/pump-n-dump/dao"
	"log"
)

var dao = MarketsDAO{}

func init() {
	dao.Server = "localhost"
	dao.Database = "markets_db"
	dao.Connect()
}

func main() {
	summaries, err := dao.FindAll("BTC-TRX")
	if err != nil {
		log.Fatal(err)
	}

	for _, summary := range summaries {
		fmt.Println(summary)
	}
}
