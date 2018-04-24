package main

import (
	"encoding/json"
	. "fugger-junior/pump-n-dump/config"
	. "fugger-junior/pump-n-dump/dao"
	. "fugger-junior/pump-n-dump/models"
	"io/ioutil"
	"log"
	"net/http"
	"strings"

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
			markets[item["MarketName"].(string)] = Summary{OpenBuyOrders: item["OpenBuyOrders"].(float64), OpenSellOrders: item["OpenSellOrders"].(float64),
				Volume: item["Volume"].(float64), TimeStamp: item["TimeStamp"].(string)}
		}
	}

	for _, summary := range markets {
		// fmt.Print(index + ": ")
		// fmt.Println(summary)

		summary.ID = bson.NewObjectId()
		if err := dao.Insert(summary); err != nil {
			log.Fatal(err)
		}
	}
}
