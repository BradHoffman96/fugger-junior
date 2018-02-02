package main

  import(
    "fmt"
    "log"
    "net/http"
    "io/ioutil"
    "encoding/json"
  )

var arbitrary_json map[string]interface{}

func main() { //https://min-api.cryptocompare.com/data/pricehistorical
  // documentation: https://www.cryptocompare.com/api#-api-data-histohour-
  // test query https://min-api.cryptocompare.com/data/histohour?fsym=BTC&tsym=USD&limit=60&aggregate=3&e=CCCAGG

  var fsym string = "BTC" //set of variables to be inserted into URL
  var tsym string = "ETH"
  var limit string = "30"
  var e string = "CCCAGG"

  url := fmt.Sprintf("https://min-api.cryptocompare.com/data/histohour?fsym=%s&tsym=%s&limit=%s&aggregate=3&e=%s", fsym, tsym, limit, e)
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
  for _, v := range(test) {
    item := (v.(map[string]interface{}))
    fmt.Println(fmt.Sprintf("time: %f, close: %f, high: %f, low: %f, open: %f, volumefrom: %f, volumeto %f", //you can just do multiline code between ( )
      item["time"], item["close"], item["high"], item["low"], item["open"], item["volumefrom"], item["volumeto"])) //pull out values
  }
}
