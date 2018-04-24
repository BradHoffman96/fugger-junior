package main

import (
	"encoding/json"
	"fmt"
	. "fugger-junior/pump-n-dump/config"
	. "fugger-junior/pump-n-dump/dao"
	. "fugger-junior/pump-n-dump/models"
	"io/ioutil"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/globalsign/mgo/bson"
)

var config = Config{}
var dao = MarketsDAO{}

var arbitrary_json map[string]interface{}

func init() {
	config.Read()

	dao.Server = config.Server
	dao.Database = config.Database
	dao.Connect()
}

func main() {
	for {
		url := "https://bittrex.com/api/v1.1/public/getmarketsummaries"
		resp, err := http.Get(url)
		if err != nil {
			log.Fatal(err)
		}
		defer resp.Body.Close()

		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			log.Fatal(err)
		}

		json.Unmarshal([]byte(body), &arbitrary_json)
		result := arbitrary_json["result"].([]interface{})
		markets := make(map[string]Summary)

		for _, v := range result {
			item := (v.(map[string]interface{}))
			if strings.Contains(item["MarketName"].(string), "BTC") {
				markets[item["MarketName"].(string)] = Summary{
					OpenBuyOrders:  item["OpenBuyOrders"].(float64),
					OpenSellOrders: item["OpenSellOrders"].(float64),
					Volume:         item["Volume"].(float64),
					TimeStamp:      item["TimeStamp"].(string),
					Last:           item["Last"].(float64)}
			}
		}

		for market, summary := range markets {
			// fmt.Print(market + ": ")
			// fmt.Println(summary)

			//TODO: Make this concurrent
			summary.ID = bson.NewObjectId()
			if err := dao.Insert(market, summary); err != nil {
				log.Fatal(err)
			}
		}

		fmt.Println(time.Now())
		time.Sleep(30 * time.Second)
	}
}
