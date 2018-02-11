package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/go-resty/resty"
	"github.com/patrickmn/go-cache"
	"github.com/senseyeio/roger"
)

//A CurrencyType is an int distinguishing between Bitcoin, Ethereum, Ripple, ect.
type CurrencyType int

//declare cache for http requests
var c = cache.New(5*time.Minute, 10*time.Minute)

//Definitions of CurrencyType's
const (
	Bitcoin CurrencyType = iota
	Ethereum
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
)

//A CryptoInputData stores the current price and timestamp for use with an algorithm
type CryptoInputData struct {
	price float64
	time  int64
}

//A CryptoOutputData stores the data that tells a wallet whether or not it should buy with a confidence interval.
type CryptoOutputData struct {
	buy        bool
	confidence float64
}

//A Wallet keeps track of an amount of currency for a specific MarketPlace
type Wallet interface {
	Init()
	Exchange(CurrencyType, CurrencyType, float64) (float64, error)
	MarketPlace() MarketPlace
}

//An ExchangePlace is a provider of exchange rates for various currencies
type TickerProvider interface {
	Serve()
}

//An ExchangeAlgorithm takes in TickerProvider data and output exchange requests to Wallets.
type ExchangeAlgorithm interface {
	Execute()
}

//A DummyWallet for keeping track of and exchanging currencies for testing purposes.
type DummyWallet struct {
	Currencies map[CurrencyType]float64
}

type CryptoCompareProvider struct {
	btcTicker chan CryptoInputData
	ethTicker chan CryptoInputData
}

type BtcEthPredictor struct {
	btcTicker   chan CryptoInputData
	ethTicker   chan CryptoInputData
	recommender chan CryptoOutputData
}

func main() {
	btcTicker := make(chan CryptoInputData, 256)
	ethTicker := make(chan CryptoInputData, 256)
	recommender := make(chan CryptoOutputData, 256)

	bfxProvider := CryptoCompareProvider{btcTicker, ethTicker}
	predictor := BtcEthPredictor{btcTicker, ethTicker, recommender}
	bfxProvider.Serve()
	go predictor.Execute()

	fmt.Printf("Hello, world.\n")
}

func (p *BtcEthPredictor) Execute() {
	rClient, err := roger.NewRClient("127.0.0.1", 6311)
	if err != nil {
		fmt.Println("Failed to connect to Rserve.")
		return
	}

}

func CcProvideBtcUsd(c chan<- CryptoInputData) {
	data, err := GetCurrent(BitcoinSymbol, DollarSymbol)

	if err != nil {
		panic(err)
	} else {
		var cid = CryptoInputData{data, time.Now().UTC().Unix()}
		c <- cid
	}
}

func CcProvideEthUsd(c chan<- CryptoInputData) {
	//get data from CryptoCompare
	//format it
	//stuff it into the channel
}

func (p *CryptoCompareProvider) Serve() {
	go CcProvideBtcUsd(p.btcTicker)
	go CcProvideEthUsd(p.ethTicker)
}

func (w *DummyWallet) Exchange(currentCur, newCur CurrencyType, amtToBuy float64) (float64, error) {

}

// Currency ticker symbols.
const (
	BitcoinSymbol  string = "BTC"
	EthereumSymbol string = "ETH"
	DollarSymbol   string = "USD"
)

// API URLs
const (
	currentDataURL    = "https://min-api.cryptocompare.com/data/price?fsym=%s&tsyms=%s"
	historicalDataURL = "https://min-api.cryptocompare.com/data/pricehistorical?fsym=%s&tsyms=%s&ts=%s"
)

type CurrentCurrency struct {
	USD float64 `json:"USD"`
}

type HistoricalCurrencyBTC struct {
	BTC CurrentCurrency `json:"BTC"`
}

type HistoricalCurrencyETH struct {
	ETH CurrentCurrency `json:"ETH"`
}

func GetCurrent(fsym string, tsym string) (float64, error) {
	url := fmt.Sprintf(currentDataURL, fsym, tsym)

	resp, err := resty.R().Get(url)

	if err != nil {
		log.Fatal("Failed to parse response: ", err)
		return 0.0, err
	}

	if resp.RawResponse.StatusCode != 200 {
		log.Fatal(fmt.Sprintf("Unable to make request: %s", resp.Status))
		return 0.0, fmt.Errorf("Unable to make request: %s", resp.Status)
	}

	var data CurrentCurrency

	if err := json.Unmarshal(resp.Body(), &data); err != nil {
		log.Fatal("Failed to parse response: ", err)
	}

	return data.USD, nil
}

func GetHistorical(fsym string, tsym string, utc int) (float64, error) {
	url := fmt.Sprintf(historicalDataURL, fsym, tsym, utc)

	resp, err := resty.R().Get(url)

	if err != nil {
		log.Fatal("Failed to parse response: ", err)
		return 0.0, err
	}

	if resp.RawResponse.StatusCode != 200 {
		log.Fatal(fmt.Sprintf("Unable to make request: %s", resp.Status))
		return 0.0, fmt.Errorf("Unable to make request: %s", resp.Status)
	}

	if fsym == BitcoinSymbol {
		var data HistoricalCurrencyBTC

		if err := json.Unmarshal(resp.Body(), &data); err != nil {
			log.Fatal("Failed to parse response: ", err)
		}

		return data.BTC.USD, nil
	} else if fsym == EthereumSymbol {
		var data HistoricalCurrencyETH

		if err := json.Unmarshal(resp.Body(), &data); err != nil {
			log.Fatal("Failed to parse response: ", err)
		}

		return data.ETH.USD, nil
	} else {
		log.Fatal(fmt.Sprintf("Unable to handle fsym: %s", fsym))
		return 0.0, nil
	}
}
