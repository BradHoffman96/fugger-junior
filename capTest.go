package main

  import(
    "os"
    "fmt"
    "log"
    "time"
    "strconv"
    "net/http"
    "io/ioutil"
    "encoding/csv"
    "encoding/json"
  )

var arbitrary_json map[string]interface{}

func main() { //https://min-api.cryptocompare.com/data/pricehistorical
  // documentation: https://www.cryptocompare.com/api#-api-data-histohour-
  // test query https://min-api.cryptocompare.com/data/histohour?fsym=BTC&tsym=USD&limit=60&aggregate=3&e=CCCAGG

  var fsym string = "BTC" //set of variables to be inserted into URL
  var tsym string = "USD"
  var limit string = "2000" //api says limit is 2000 but only pulling 667 results?
  var e string = "CCCAGG"

  csvName := fmt.Sprintf("%s_to_%s_%s.csv", fsym, tsym, e) //add time when I figure the return out better
  file, err := os.OpenFile(csvName, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
  if err != nil {
    log.Fatal(err)
  }
  writer := csv.NewWriter(file)
  header := []string{"time", "close", "high", "low", "open", "volumefrom", "volumeto"}
  writer.Write(header) //writer can seemingly only take strings so the conversion below is a bit of a mess

  for x := 1454418000; x <= 1486069200; x+= 7200000 {
    xint := strconv.Itoa(x)
    url := fmt.Sprintf("https://min-api.cryptocompare.com/data/histohour?fsym=%s&tsym=%s&limit=%s&aggregate=1&e=%s&toTs=%s", fsym, tsym, limit, e, xint)
    resp, err := http.Get(url) //&toTs allows you to specify a specific time: https://min-api.cryptocompare.com/
    //fsym is from symbol // tsym is to symbol // limit is limit //e is name of exchange
    if err != nil{
      log.Fatal(err) //need an alternative for fatal
    }
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body) //https://gist.github.com/kousik93/6d95c4c4d37d8c731d7b
    if err != nil{
      log.Fatal(err)
    }

    json.Unmarshal([]byte(body), &arbitrary_json)
    //.([]interface{}) is a type assertion
    test := arbitrary_json["Data"].([]interface{}) //incredibly helpful https://stackoverflow.com/questions/31815969/go-cannot-range-over-my-var-type-interface

    for i, v := range(test) {
      item := (v.(map[string]interface{}))
      row := []string{strconv.FormatFloat(item["time"].(float64), 'E', -1, 64), strconv.FormatFloat(item["close"].(float64), 'E', -1, 64),
        strconv.FormatFloat(item["high"].(float64), 'E', -1, 64), strconv.FormatFloat(item["low"].(float64), 'E', -1, 64),
        strconv.FormatFloat(item["open"].(float64), 'E', -1, 64), strconv.FormatFloat(item["volumefrom"].(float64), 'E', -1, 64),
        strconv.FormatFloat(item["volumeto"].(float64), 'E', -1, 64)} //interface to float64 to string
      err := writer.Write(row)
      if err != nil{
        fmt.Println("Line failed to print ", i)
      }
    }
    time.Sleep(1 * time.Second)
  }
  defer file.Close()
  defer writer.Flush()
}
