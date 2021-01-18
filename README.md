# markcole WeatherPi

This project is the successor to my other Javascript based web application that display local Weather, Train and aircraft information on Raspberry pi (https://github.com/macole111/Weather). I wanted to replace the Touchscreen LCD with a more eco-friendly eInk screen.

The code uses the following data sources:

- Weather.gov forecast API
- OpenSkies live aircraft information
- A user supplied PATH train times API (https://www.reddit.com/r/jerseycity/comments/bb4041/programmatic_realtime_path_data/)

# Layout

- WeatherScreen.py - the main code responsible for talking to the APIs and rendering the eInk screen
- config.py - contains the config such as timezones and lat long
- lib/ - the epd e-ink screen libraries

# Use

Simply run python3 WeatherScreen.py (may require pip to install some modules such as geopi)

# Hardware

![Weather App on Pi](example.jpg?raw=true "Weather App on Pi")


- Raspberry Pi 3A
- Waveshare 7.5inch E-Ink Display HAT for Raspberry Pi 800×480 (two colour model)
- https://www.amazon.com/gp/product/B08QCJFJK5/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1