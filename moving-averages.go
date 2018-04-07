package main

import (
	"time"

	"github.com/BradHoffman96/fugger-junior/fugger"
)

/*
MovingAverage contains the current state of the moving average
The moving average structure and methods have been taken from https://github.com/RobinUS2/golang-moving-average and included for further modification
*/
type MovingAverage struct {
	Window      int
	values      []float64
	valPos      int
	slotsFilled bool
}

//A DummyWallet for keeping track of and exchanging currencies for testing purposes.
type DummyWallet struct {
	Currencies  map[fugger.CurrencyType]float64
	recommender chan fugger.CryptoOutputData
}

type CryptoCompareProvider struct {
	btcTicker chan fugger.CryptoInputData
}

type BtcUsdPredictor struct {
	btcTicker   chan fugger.CryptoInputData
	recommender chan fugger.CryptoOutputData
}

//Serve pushes price updates every 24 hours for the recommender
func (p *CryptoCompareProvider) Serve() {
	ticker := time.NewTicker(24 * time.Hour)
	go func() {
		for {
			select {
			case <-ticker.C:
				go CcProvideBtcUsd(p.btcTicker)
			}
		}
	}()
}

// CcProvideBtcUsd returns the current price of bitcoin in USD
func CcProvideBtcUsd(c chan<- fugger.CryptoInputData) {
	data, err := fugger.GetCurrent(fugger.BitcoinSymbol, fugger.DollarSymbol)

	if err != nil {
		panic(err)
	} else {
		var cid = fugger.CryptoInputData{Price: data, Time: time.Now().UTC().Unix()}
		c <- cid
	}
}

// CcHistoricalBtcUsd returns the historical closing prices in USD for each day of the specified time interval
func CcHistoricalBtcUsd(c chan<- fugger.CryptoInputData, window int) {
	baseTime := time.Now()
	for i := 0; i < window; i++ {
		queryTime := baseTime.AddDate(0, 0, -20+i)
		data, err := fugger.GetHistorical(fugger.BitcoinSymbol, fugger.DollarSymbol, queryTime.Unix())

		if err != nil {
			panic(err)
		} else {
			newData := fugger.CryptoInputData{Price: data, Time: queryTime.Unix()}
			c <- newData
		}
	}
}

//ConsumeRecommendations from the recommendation queue and buy/sell bitcoin
func (w *DummyWallet) ConsumeRecommendations() {
	for {
		select {
		case data, ok := <-w.recommender:
			if ok {
				if data.Buy {
					w.Exchange(fugger.Usd, fugger.Bitcoin, w.Currencies[fugger.Usd])
				} else {
					w.Exchange(fugger.Bitcoin, fugger.Usd, w.Currencies[fugger.Bitcoin])
				}
			}
		}
	}
}

//Exchange currencies
func (w *DummyWallet) Exchange(currentCur, newCur fugger.CurrencyType, amtToBuy float64) (float64, error) {
	rate, err := fugger.GetCurrent(fugger.DollarSymbol, fugger.BitcoinSymbol)
	if err != nil {
		panic(err)
	} else {
		//Usd to Bitcoin
		if currentCur == fugger.Usd && newCur == fugger.Bitcoin {
			w.Currencies[fugger.Bitcoin] = w.Currencies[fugger.Usd] / rate
			w.Currencies[fugger.Usd] = 0
			//Bitcoin to USD
		} else if currentCur == fugger.Bitcoin && newCur == fugger.Usd {
			w.Currencies[fugger.Usd] = w.Currencies[fugger.Bitcoin] * rate
			w.Currencies[fugger.Bitcoin] = 0
		}
	}
	return 1, nil
}

//Execute creates recommendations telling to buy/sell and the associated confidence level
func (p *BtcUsdPredictor) Execute() {
	shortLength := 5
	longLength := 20
	shortWindow := NewMA(shortLength)
	longWindow := NewMA(longLength)
	waitingToSell := true
	for {
	emptyQueue:
		for {
			select {
			case data, ok := <-p.btcTicker:
				if ok {
					shortWindow.Add(data.Price)
					longWindow.Add(data.Price)
				}
			default:
				break emptyQueue
			}
		}

		//get difference between the two windows
		diff := shortWindow.Avg() - longWindow.Avg()
		//if positive buy
		if diff > 0 && waitingToSell {
			waitingToSell = false
			recc := fugger.CryptoOutputData{Buy: true, Confidence: 1.0}
			p.recommender <- recc
		}
		//if negative sell
		if diff < 0 && !waitingToSell {
			waitingToSell = true
			recc := fugger.CryptoOutputData{Buy: false, Confidence: 1.0}
			p.recommender <- recc
		}
	}
}

func main() {
	window := 20
	fugger.GetCurrent(fugger.BitcoinSymbol, fugger.DollarSymbol)

	btcTicker := make(chan fugger.CryptoInputData, 256)
	recommender := make(chan fugger.CryptoOutputData, 256)

	//push historical into channel
	CcHistoricalBtcUsd(btcTicker, window)
	bfxProvider := CryptoCompareProvider{btcTicker}
	predictor := BtcUsdPredictor{btcTicker, recommender}
	wallet := Init([]fugger.CurrencyType{fugger.Usd, fugger.Bitcoin})
	wallet.Currencies[fugger.Usd] = 10000

	//provide daily price updates
	bfxProvider.Serve()
	//begin moving average algorithm
	go predictor.Execute()
	go wallet.ConsumeRecommendations()
	for {

	}
}

/*
Avg the moving average struct's values
The moving average structure and methods have been taken from https://github.com/RobinUS2/golang-moving-average
*/
func (ma *MovingAverage) Avg() float64 {
	var sum = float64(0)
	var c = ma.Window - 1

	// Are all slots filled? If not, ignore unused
	if !ma.slotsFilled {
		c = ma.valPos - 1
		if c < 0 {
			// Empty register
			return 0
		}
	}

	// Sum values
	var ic = 0
	for i := 0; i <= c; i++ {
		sum += ma.values[i]
		ic++
	}

	// Finalize average and return
	avg := sum / float64(ic)
	return avg
}

//Add a new value to the moving average struct
func (ma *MovingAverage) Add(val float64) {
	// Put into values array
	ma.values[ma.valPos] = val

	// Increment value position
	ma.valPos = (ma.valPos + 1) % ma.Window

	// Did we just go back to 0, effectively meaning we filled all registers?
	if !ma.slotsFilled && ma.valPos == 0 {
		ma.slotsFilled = true
	}
}

//NewMA initalizes a new MA struct
func NewMA(window int) *MovingAverage {
	return &MovingAverage{
		Window:      window,
		values:      make([]float64, window),
		valPos:      0,
		slotsFilled: false,
	}
}

//Init DummyWallet initalization
func Init(currencies []fugger.CurrencyType) *DummyWallet {
	wallet := &DummyWallet{
		Currencies: make(map[fugger.CurrencyType]float64),
	}
	for _, c := range currencies {
		wallet.Currencies[c] = 0.0
	}

	return wallet
}
