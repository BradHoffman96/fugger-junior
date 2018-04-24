package config

import (
	"log"

	"github.com/BurntSushi/toml"
)

//Struct containing the details for server and db connection
type Config struct {
	Server   string
	Database string
}

func (c *Config) Read() {
	if _, err := toml.DecodeFile("config.toml", &c); err != nil {
		log.Fatal(err)
	}
}
