package main

import (
	"fmt"
	. "fugger-junior/pump-n-dump/dao"
	"log"
	"net/http"
	"strings"
	"time"

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

func drawChart(res http.ResponseWriter, req *http.Request) {
	dates, prices := getValues()

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

	graph := chart.Chart{
		XAxis: chart.XAxis{
			Style:        chart.Style{Show: true},
			TickPosition: chart.TickPositionBetweenTicks,
		},
		YAxis: chart.YAxis{
			Style: chart.Style{Show: true},
			Range: &chart.ContinuousRange{
				Max: .000007,
				Min: .000006,
			},
		},
		Series: []chart.Series{
			priceSeries,
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
