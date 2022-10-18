# Generate nautical chart rulers as .png images 

Given a chart scale (e.g. 1:40,000) and target latitude (e.g. 37° 25' N), generate .png images showing a latitude/distance scale and a longitude scale. This code assumes the WGS 84 geoid and datum. Note, the latitude/distance scale will only be correct at the specified latitude. As latitude on the chart moves away from this value, the Mercator projection will distort the chart. For charts covering a small area, this effect can be ignored. However, I don't recommend using these rulers for charts over 1:200,000 scale.              
## Usage
```
usage: gen_ruler.py [-h] [--dpi DPI] scale latitude length

positional arguments:
  scale       Scale of chart ruler (integer N for scale of 1 to N)
  latitude    Latitude at which to generate the longitude ruler (in degrees
              and minutes)
  length      Length of the ruler, in minutes of latitude / longitude

optional arguments:
  -h, --help  show this help message and exit
  --dpi DPI   DPI of resulting image
```
```
example: gen_ruler.py 40000 "37 25" 5 --dpi 560
```
This generates 5-minute rulers for a 1:4000 scale chart at 37° 25' longitude with a DPI of 560  

## Examples

![Distance ruler example](distance_40000_5.png "Distance ruler")
![Longitude ruler example](longitude_40000_37_25_5.png "Longitude ruler")   
