package main

import (
	"fmt"
	"time"

	"github.com/patrickmn/go-cache"
)

//A CurrencyType is an int distinguishing between Bitcoin, Ethereum, Ripple, ect.
type CurrencyType int

//declare cache for http requests
var c = cache.New(5*time.Minute, 10*time.Minute)

//Definitions of CurrencyType's
const (
	Bitcoin CurrencyType = iota
	Ethereum
	Ripple
)

//A MarketPlace is an int distinguishing between Bitfinex, Binance, etc.
type MarketPlace int

//gdax
//bittrix
//kraken
//Definitions of MarketPlace's
const (
	Dummy MarketPlace = iota
	Bitfinex
	Binance
)

//A Wallet keeps track of an amount of currency for a specific MarketPlace
type Wallet interface {
	Init()
	Exchange(CurrencyType, CurrencyType, float64) (float64, error)
	MarketPlace() MarketPlace
}

//An ExchangePlace is a provider of exchange rates for various currencies
type ExchangePlace interface {
	Init()
	ExchangeRate(int, int) (float64, error)
}

//An ExchangeAlgorithm takes in ExchangePlace data and output exchange requests to Wallets.
type ExchangeAlgorithm interface {
	Execute(Wallet)
}

//A DummyWallet for keeping track of and exchanging currencies for testing purposes.
type DummyWallet struct {
	Currencies map[CurrencyType]float64
}

//A BitfinexWallet responsible for keeping track of and exchanging currencies from Bitfinex.
type BitfinexWallet struct {
	Currencies map[CurrencyType]float64
}

//A BinanceWallet responsible for keeping track of and exchanging currencies from BinanceWallet.
type BinanceWallet struct {
	Currencies map[CurrencyType]float64
}

/*
API Response Structs
*/
//Bitfinex
type BitfinexTickerResponse struct {
	Mid       float64 `json:"mid"`
	Bid       float64 `json:"bid"`
	Ask       float64 `json:"ask"`
	LastPrice float64 `json:"last_price"`
	Low       float64 `json:"low"`
	High      float64 `json:"high"`
	Volume    float64 `json:"volume"`
	Timestamp float64 `json:"timestamp"`
}

func main() {
	fmt.Printf("Hello, world.\n")
}
