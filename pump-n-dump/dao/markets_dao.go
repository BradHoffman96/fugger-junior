package dao

import (
	"fugger-junior/pump-n-dump/models"
	"log"

	"github.com/globalsign/mgo/bson"

	"github.com/globalsign/mgo"
)

type MarketsDAO struct {
	Server   string
	Database string
}

var db *mgo.Database

//this is going to need to be changed because there will be a collection for each market
const (
	COLLECTION = "markets"
)

func (m *MarketsDAO) Connect() {
	session, err := mgo.Dial(m.Server)
	if err != nil {
		log.Fatal(err)
	} else {
		log.Println("Connected to server")
	}
	db = session.DB(m.Database)
}

func (m *MarketsDAO) Insert(market string, summary models.Summary) error {
	err := db.C(market).Insert(&summary)
	return err
}

func (m *MarketsDAO) FindAll(market string) ([]models.Summary, error) {
	var summaries []models.Summary
	err := db.C(market).Find(bson.M{}).All(&summaries)
	return summaries, err
}
