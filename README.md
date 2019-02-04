# apod_scraper
Scrapes all images from [APOD (Atronomy Picture of the Day)](https://apod.nasa.gov/apod/astropix.html) between a given date range in highest possible resolution.

Uses `requests`+` gevent`+` lxml` for superfast scraping and html parsing.

Use this script responsibly. Sending a lot of simultaneous requests will cause load on the server.

**TODO**: Create a cross-platform Python script for changing desktop background to APOD.

![M31: The Andromeda Galaxy](https://apod.nasa.gov/apod/image/1812/m31_gendler_1080.jpg)

**NOTE**: This is an educational project. All images belong to their respective copyright holders. You can use the scraped images for personal, non-commercial, non-public fair use. Please note that many APOD images are copyrighted and to use them commercially you must gain explicit permission from the copyright owners. 
