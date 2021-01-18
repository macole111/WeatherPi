#Main Config file that defines the API parameters (location etc.)

#Current location of the screen (lat, long)
latlong = (40.6908507,-73.9981995)

#The Weather.gov API radar station and grid reference (see https://www.weather.gov/documentation/services-web-api)
radarstation = "OKX/31,34"

#PATH Train station (see https://www.reddit.com/r/jerseycity/comments/bb4041/programmatic_realtime_path_data/)
pathstation = "grove_street"

#Local timezone of the screen and display name
timezonelocal = "America/New_York"
timezonelocalname = "NY"

#other timezone also displayed
timezoneother = "Europe/London"
timezoneothername = "LN"

#The mapping of weather types to the Weather Icon Font
ICON_MAP = {

    "Sunrise": "A",
    "Sunny": "B",
    "Clear": "C",
    "Windy": "F",
    "PartlySunny": "H",
    "PartlyClear": "I",
    "Mist": "M",
    "Cloudy": "N",
    "Thunderstorm": "O",
    "LightRain": "Q",
    "Rain": "R",
    "Snow": "W",
    "Sunset": "J"
}