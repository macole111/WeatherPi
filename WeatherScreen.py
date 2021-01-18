#!/usr/bin/python3

import sys
import os

#Add in the code for the EPD Screen
libdir = 'lib'
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5b_HD

import logging
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import datetime
import pytz
import math
import urllib, json
from urllib.request import urlopen
import geopy.distance
import config

logging.basicConfig(level=logging.INFO)

#Import the fonts at several sizes
font24 = ImageFont.truetype('Font.ttc', 24)
font18 = ImageFont.truetype('Font.ttc', 18)
font14 = ImageFont.truetype('Font.ttc', 14)
weather = ImageFont.truetype('meteocons.ttf', 64)
smallweather = ImageFont.truetype('meteocons.ttf', 42)

def renderIcon(weather, isdaytime):
    """Param:
        weather: String - the current short weather forecast
        isdaytime: boolean - true if the current period is day

        This function takes the short forecast and looks for keywords that indicate the type of weather.
        It then returns the icon that shows that type of weather
    """

    output = config.ICON_MAP["Sunny"]

    if not isdaytime:
        output = config.ICON_MAP['Clear']
    
    if "Snow" in weather:
        output = config.ICON_MAP["Snow"]

    if "Cloudy" in weather:
        output = config.ICON_MAP["Cloudy"]

    if "Partly Cloudy" in weather and isdaytime:
        output = config.ICON_MAP["PartlySunny"]
    
    if "Partly Cloudy" in weather and not isdaytime:
        output = config.ICON_MAP["PartlyClear"]
    
    if "Storm" in weather:
        output = config.ICON_MAP["Thunderstorm"]
    
    if "Lightning" in weather:
        output = config.ICON_MAP["Thunderstorm"]

    if "Thunderstorm" in weather:
        output = config.ICON_MAP["Thunderstorm"]

    if "Rain" in weather:
        output = config.ICON_MAP["Rain"]

    if "Rain Showers Likely" in weather:
        output = config.ICON_MAP["Rain"]

    if "Light Rain" in weather:
        output = config.ICON_MAP["LightRain"]

    if "Slight Chance Rain" in weather or "Slight Chance Rain Showers" in weather and isdaytime:
        output = config.ICON_MAP["Sunny"]
        
    if "Slight Chance Rain" in weather or "Slight Chance Rain Showers" in weather and not isdaytime:
        output = config.ICON_MAP["Clear"]
        
    if "Clear" in weather:
        if isdaytime:
            output = config.ICON_MAP["Sunny"]
        else:
            output = config.ICON_MAP["Clear"]
    
    return output

def wrap_by_word(s, n):
    '''returns a string where \\n is inserted between every n words'''
    a = s.split()
    ret = ''
    for i in range(0, len(a), n):
        ret += ' '.join(a[i:i+n]) + '\n'

    return ret

def renderDetailedWeather(period,x,y,drawblack,drawred):
    """Param:
        period: The dict containing the current period's weather forecast
        x: the left x coordinate for the space where this element will be rendered
        y: the top y coordinate for the space where this element will be rendered
        drawblack: The black colour canvas object
        drawred: The red colour canvas object

        Takes the weather forecast for future period and renders it with full details (large icon, Temp and detailed forecast)
    """
    drawred.text((x,y), renderIcon(period["shortForecast"],period["isDaytime"]), font=weather, fill=0)

    drawblack.text((x+80,y), period["name"], font=font24, fill=0)

    celsius = round((period["temperature"] - 32) * 5/9)

    if(period["temperature"] > 60):
        drawred.text((x+80,y+30), str(period["temperature"]) + " °F (" + str(celsius) + " °C)" , font=font24, fill=0)
    else:
        drawblack.text((x+80,y+30), str(period["temperature"]) + " °F (" + str(celsius) + " °C)" , font=font24, fill=0)

    forecast = ".".join(period["detailedForecast"].split(".", 3)[:-1])

    drawblack.multiline_text((x,y+60), wrap_by_word(forecast,6),font=font14, fill=0, align="center")


def renderHour(period,x,y,drawblack,drawred):
    """Param:
        period: The dict containing the current period's weather forecast
        x: the left x coordinate for the space where this element will be rendered
        y: the top y coordinate for the space where this element will be rendered
        drawblack: The black colour canvas object
        drawred: The red colour canvas object

        Takes the weather forecast for future period and renders it small with some basic details (small icon, Temp and wind)

        Returns: Width of the element in px
    """

    #get the hour number from the datestamp
    hour = period["startTime"].split(":")[0].split("T")[1]

    drawred.text((x+10,y), renderIcon(period["shortForecast"],period["isDaytime"]), font=smallweather, fill=0)

    celsius = round((period["temperature"] - 32) * 5/9)

    text =  hour + ":00\n" + str(period["temperature"]) + " F (" + str(celsius) + " C)\n" +  period["windSpeed"] + " " + period["windDirection"]

    drawblack.multiline_text((x,y+40), text, font=font14, fill=0, align="center")

    w, h = drawblack.multiline_textsize(text, font=font14)

    return w

def renderFiveDay(period,x,y,drawblack,drawred):
    """Param:
        period: The dict containing the current period's weather forecast
        x: the left x coordinate for the space where this element will be rendered
        y: the top y coordinate for the space where this element will be rendered
        drawblack: The black colour canvas object
        drawred: The red colour canvas object

        Takes the weather forecast for future period and renders it with medium details (large icon, Temp and short forecast)

        Returns: Width of the element in px
    """

    wn, hn = drawblack.textsize(period["name"], font = font24)

    wf, hf = drawblack.multiline_textsize(wrap_by_word(period["shortForecast"],4), font=font14)

    #use the largest text's width as the size so we don't bump into the element to the right of us 

    if(wf > wn):
        w = wf
    else:
        w = wn

    drawblack.text((x+(w-wn)/2,y), period["name"], font=font24, fill=0)

    wi, hi = drawred.textsize( renderIcon(period["shortForecast"],period["isDaytime"]), font = smallweather)

    drawred.text((x+(w-wi)/2,y+30), renderIcon(period["shortForecast"],period["isDaytime"]), font=smallweather, fill=0)

    celsius = round((period["temperature"] - 32) * 5/9)

    wc, hc = drawred.textsize( str(period["temperature"]) + " F (" + str(celsius) + " C)\n", font=font18)

    drawblack.text((x+(w-wc)/2,y+80), str(period["temperature"]) + " F (" + str(celsius) + " C)\n", font=font18, fill=0)

    drawblack.multiline_text((x+(w-wf)/2,y+105), wrap_by_word(period["shortForecast"],4), font=font14, fill=0, align="center")

    return w

def renderSunriseSunset(data,tz,x,y,drawback,drawred):
    """Param:
        period: The dict containing the current period's weather forecast
        tz: the timezone of the screen that the times should be shown in
        x: the left x coordinate for the space where this element will be rendered
        y: the top y coordinate for the space where this element will be rendered
        drawblack: The black colour canvas object
        drawred: The red colour canvas object

        Takes the sunrise and sunset data and renders it to the screen along with day length
    """

    #calculate the day length in mins

    length = "Day Length: " + str(math.floor(data['results']['day_length'] / 60 / 60)) + " hours " + str((data['results']['day_length'] % 60)) + " mins"

    sunrise = data['results']['sunrise']
    sunset = data['results']['sunset']

    sunrise = datetime.datetime.strptime(sunrise, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=pytz.utc).astimezone(tz)
    sunset = datetime.datetime.strptime(sunset, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=pytz.utc).astimezone(tz)

    sunrise = sunrise.strftime("%H:%M") + " AM"
    sunset = sunset.strftime("%H:%M") + " PM"

    wsr, hsr = drawback.textsize(sunrise, font = font14)
    wss, hss = drawback.textsize(sunrise, font = font14)

    drawred.text((x,y), config.ICON_MAP["Sunrise"], font=smallweather, fill=0)

    drawback.text((x+40,y+10), sunrise, font=font14, fill=0)

    drawred.text((x+wsr+40,y), config.ICON_MAP["Sunset"], font=smallweather, fill=0)

    drawback.text((x+wsr+80,y+10), sunset, font=font14, fill=0)

    drawback.text((x+wsr+90+wss,y+10), length, font=font14, fill=0)

def renderPATH(train,x,y,drawblack,drawred):
    """Param:
        period: The dict containing the current period's weather forecast
        x: the left x coordinate for the space where this element will be rendered
        y: the top y coordinate for the space where this element will be rendered
        drawblack: The black colour canvas object
        drawred: The red colour canvas object

        Takes the PATH arrival time for a single train and renders the details to the screen.
    """

    #calculate the Time to arrive compared to the current time
    arrival = datetime.datetime.strptime(train["projectedArrival"], '%Y-%m-%dT%H:%M:%SZ')

    now = datetime.datetime.now()

    timetoarrival = (arrival - now).total_seconds() / 60.0

    if timetoarrival < 1:
        drawblack.text((x,y), "< 1 min", font=font18, fill=0)
    else:
        drawblack.text((x,y), str(math.ceil(timetoarrival)) + " mins", font=font18, fill=0)

    draw_Himage.line((x+71, y, x+71, y+30), fill = 0)

    if train["status"] == "ON_TIME" or train["status"] == "ARRIVING_NOW":
        drawblack.text((x+75,y), "On Time", font=font18, fill=0)
    else:
        drawred.text((x+75,y), train['status'], font=font18, fill=0)

    draw_Himage.line((x+147, y, x+147, y+30), fill = 0)

    if train["headsign"] == "World Trade Center":
        drawred.text((x+152,y), train["headsign"], font=font18, fill=0)
    else:
        drawblack.text((x+152,y), train["headsign"], font=font18, fill=0)


def renderAircraft(aircraft,x,y,drawblack,drawred):
    """Param:
        period: The dict containing the current period's weather forecast
        x: the left x coordinate for the space where this element will be rendered
        y: the top y coordinate for the space where this element will be rendered
        drawblack: The black colour canvas object
        drawred: The red colour canvas object

        Takes an aircraft in the local area and renderes the details to the screen
    """

    text = aircraft[1] + " | " + str(round(aircraft[17])) + "km | " + str(round(aircraft[10])) + " | " + str(round(aircraft[7])) + "ft | " + str(round(aircraft[9] * 1.944)) + " knots | " + str(round(aircraft[11] * 196.85)) + " ft/min | squawk " + str(aircraft[14])

    drawblack.text((x, y), text, font=font14, fill=0)

def renderWeatherScreen(draw_Himage, draw_other):
    """Param:
        draw_Himage: The black colour canvas object
        draw_other: The red colour canvas object

        The main function that generates the weather screen view
    """

    # Drawing on the Horizontal image
    logging.info("1.Drawing the Weather Screen..")

    #Draw the current time in the top left of the screen

    tz_NY = pytz.timezone(config.timezonelocal) 
    tz_LN = pytz.timezone(config.timezoneother)

    timenowln = config.timezoneothername + ": " + datetime.datetime.now(tz_LN).strftime("%d/%m/%Y, %H:%M")
    timenowny = config.timezonelocalname +  ": " + datetime.datetime.now(tz_NY).strftime("%d/%m/%Y, %H:%M")

    wln, hln = draw_Himage.textsize(timenowln, font = font18)
    wny, hny = draw_Himage.textsize(timenowny, font = font18)

    draw_Himage.text((wln+20,1), timenowny, font = font18, fill = 0)

    draw_Himage.text((0,1), timenowln, font = font18, fill = 0)

    #Calculate and render the Sunset information in the local timezone

    try:
        with urlopen("https://api.sunrise-sunset.org/json?lat=" + str(config.latlong[0]) + "&lng=" + str(config.latlong[1]) + "&formatted=0") as url:
            response = url.read()

    except:
        print("Sunrise/Sunset API down")

    data = json.loads(response)

    renderSunriseSunset(data,tz_NY,wny+wln+70,-10,draw_Himage,draw_other)

    #Draw the line under the sunset and the time info

    draw_Himage.rectangle((1, 25, epd.width - 1, 25), outline = 0)

    #Show the detailed weather information for the next 3 upcoming periods

    try:
        with urlopen("https://api.weather.gov/gridpoints/" + config.radarstation + "/forecast") as url:
            response = url.read()

        weatherperiods = json.loads(response)

        for i in range(0, 3):
            renderDetailedWeather(weatherperiods["properties"]["periods"][i],(epd.width*i/3)+20,28,draw_Himage,draw_other)

        
    except:
        print("Upcoming  Weather API down")

    #Show the next 12 hour forecast periods in a line across the screen

    try:
        with urlopen("https://api.weather.gov/gridpoints/" + config.radarstation + "/forecast/hourly") as url:
            response = url.read()
    except:
        print("Hourly Weather API down")

    hourlyweather = json.loads(response)

    #keeps track of the left hand x offset
    size = 15

    #keeps track of how many hours we've rendered so far
    j = 0

    #for each hour period returned by the API
    for i in range(0, len(hourlyweather["properties"]["periods"])):

        #calculate if the period is actually in the future
        utc=pytz.UTC

        time = datetime.datetime.strptime(hourlyweather["properties"]["periods"][i]["endTime"], '%Y-%m-%dT%H:%M:%S%z')
        
        now = utc.localize(datetime.datetime.now())

        #If we've not yet rendered 12 hours, render the hour
        if time > now and j < 12:

            size = 10 + size + renderHour(hourlyweather["properties"]["periods"][i],size,165,draw_Himage,draw_other)

            j += 1

            #if we're not at the last element, render a line before the next element
            if j < 12:
                draw_Himage.line((size-5, 165, size-5, 260), fill = 0)


    #Render the 5 day weather forecast

    try:
        with urlopen("https://api.weather.gov/gridpoints/" + config.radarstation + "/forecast") as url:
            response = url.read()

        fiveDayWeather = json.loads(response)

    except:
        print("5 Day Weather API down")

    size = 60

    #This goes to twelve, as we only render the daytime ones
    for i in range(2, 12):
        if fiveDayWeather["properties"]["periods"][i]["isDaytime"]:
            size = 40 + size + renderFiveDay(fiveDayWeather["properties"]["periods"][i],size,260,draw_Himage,draw_other)
            if i < 10:
                draw_Himage.line((size-15, 270, size-15, 400), fill = 0)


    #Get the PATH train info for the given station
    try:
        with urlopen("https://path.api.razza.dev/v1/stations/" + config.pathstation + "/realtime") as url:
            response = url.read()

    except:
        print("PATH API down")

    data = json.loads(response)

    #quick function to sort the trains by arrival time (soonest first)
    def gettime(train):
        return datetime.datetime.strptime(train["projectedArrival"], '%Y-%m-%dT%H:%M:%SZ')

    data["upcomingTrains"].sort(key=gettime)

    for i in range(0,len(data["upcomingTrains"])):
        renderPATH(data["upcomingTrains"][i],0,410+(i*30),draw_Himage,draw_other)

    #Get the aircraft in area of the latlong

    try:
        with urlopen("https://opensky-network.org/api/states/all?lamin=" + str(config.latlong[0] - 0.3) + "&lomin=" + str(config.latlong[1] - 0.3) + "&lamax=" + str(config.latlong[0] + 0.3) + "&lomax=" + str(config.latlong[1] + 0.3)) as url:
            response = url.read()

    except:
        print("Aircraft API down")

    data = json.loads(response)

    #For all the aircraft, we need to calculate how far away they are to sort
    for i in range(0, len(data['states'])):
        here = config.latlong
        there = (data["states"][i][6],data["states"][i][5])

        data['states'][i].append(geopy.distance.geodesic(here, there).km)

    #used to sort by distance
    def getdist(state):
        return state[17]

    data["states"].sort(key=getdist)

    j = 0
    
    for i in range(0,len(data["states"])):
        if not data["states"][i][8] and data["states"][i][7] > 100 and j < 7:
            renderAircraft(data["states"][i], 400, 410+(j*20),draw_Himage,draw_other)
            j += 1

try:

    #Interface with the e-ink screen
    epd = epd7in5b_HD.EPD()

    #create the canvases for each of the colours
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    Other = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw_Himage = ImageDraw.Draw(Himage)
    draw_other = ImageDraw.Draw(Other)

    #calculate what we're going to render
    renderWeatherScreen(draw_Himage, draw_other)

    #clear the screen
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    #display the buffered image
    epd.display(epd.getbuffer(Himage),epd.getbuffer(Other))
    
    epd.Dev_exit()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5b_HD.epdconfig.module_exit()
    exit()
