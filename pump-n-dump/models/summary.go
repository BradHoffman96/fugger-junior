package models

import "github.com/globalsign/mgo/bson"

//Summary object containing data from the API call
type Summary struct {
	ID             bson.ObjectId `bson:"_id"`
	Last           float64       `bson:"Last"`
	OpenBuyOrders  float64       `bson:"OpenBuyOrders"`
	OpenSellOrders float64       `bson:"OpenSellOrders"`
	Volume         float64       `bson:"Volume"`
	TimeStamp      string        `bson:"TimeStamp"`
}
