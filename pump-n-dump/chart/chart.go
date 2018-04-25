package main

import (
	"fmt"
	. "fugger-junior/pump-n-dump/dao"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/wcharczuk/go-chart/drawing"

	"github.com/wcharczuk/go-chart"
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

func getOpenOrders() ([]float64, []float64) {
	var openBuyOrders []float64
	var openSellOrders []float64

	summaries, err := dao.FindAll("BTC-TRX")
	if err != nil {
		log.Fatal(err)
	}

	for _, summary := range summaries {
		openBuyOrders = append(openBuyOrders, summary.OpenBuyOrders)
		openSellOrders = append(openSellOrders, summary.OpenSellOrders)
	}

	return openBuyOrders, openSellOrders
}

func drawChart(res http.ResponseWriter, req *http.Request) {
	dates, prices := getValues()
	_, openSellOrders := getOpenOrders()

	max := 0.0
	min := 0.0

	for _, price := range prices {
		if price >= max {
			fmt.Printf("%f > %f\n", price, max)
			max = price
		} else {
			fmt.Printf("%f < %f\n", price, min)
			min = price
		}
	}

	priceSeries := chart.TimeSeries{
		Name: "BTC-TRX Price",
		Style: chart.Style{
			Show:        true,
			StrokeColor: chart.GetDefaultColor(0),
		},
		XValues: dates,
		YValues: prices,
	}

	// buyOrdersSeries := chart.TimeSeries{
	// 	Name: "BTC-TRX Buy Orders",
	// 	Style: chart.Style{
	// 		Show:        true,
	// 		StrokeColor: drawing.ColorGreen,
	// 	},
	// 	XValues: dates,
	// 	YValues: openBuyOrders,
	// 	YAxis:   chart.YAxisSecondary,
	// }

	sellOrdersSeries := chart.TimeSeries{
		Name: "BTC-TRX Sell Orders",
		Style: chart.Style{
			Show:        true,
			StrokeColor: drawing.ColorRed,
		},
		XValues: dates,
		YValues: openSellOrders,
		YAxis:   chart.YAxisSecondary,
	}

	graph := chart.Chart{
		XAxis: chart.XAxis{
			Style:        chart.Style{Show: true},
			TickPosition: chart.TickPositionBetweenTicks,
		},
		YAxis: chart.YAxis{
			Style: chart.Style{Show: true},
			Range: &chart.ContinuousRange{
				Min: .000006,
				Max: .000007,
			},
		},
		YAxisSecondary: chart.YAxis{
			Style: chart.StyleShow(),
			Range: &chart.ContinuousRange{
				Min: 7000,
				Max: 8000,
			},
		},
		Series: []chart.Series{
			priceSeries,
			sellOrdersSeries,
		},
	}

	res.Header().Set("Content-Type", "image/png")
	graph.Render(chart.PNG, res)
}

func init() {
	dao.Server = "localhost"
	dao.Database = "markets_db"
	dao.Connect()
}

func main() {
	http.HandleFunc("/", drawChart)
	http.ListenAndServe(":8080", nil)
}
