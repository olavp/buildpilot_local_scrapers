#!/home/scraper/buildpilot_local_scrapers/env/bin/python3

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.profile = "/home/scraper/.mozilla/firefox/i0to7fjz.Newspapers"

driver = webdriver.Firefox(options=options)


