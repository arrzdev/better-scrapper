#requests
import requests 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#parsing
from bs4 import BeautifulSoup as sp
from lxml import etree 

#utils
from util import get_domain

class BetterScrapper:
  def __init__(self, cookies={}, headers={}):
    self.cookies = cookies
    self.headers = headers
    self.rules = []
    self.stack = []

  def set_rule(self, rule):
    #check if rule has required keys
    required_keys = ["match", "func"]
    if not all([key in rule for key in required_keys]) or len(rule) != len(required_keys):
      raise ValueError("Rule should be {match: '...', func: '...'}")
    
    #check if match is a valid xpath
    if not rule["match"].startswith("//"):
      raise ValueError("Rule argument 'match' should be a valid xpath expression")
    
    #check if func is a function
    if not callable(rule["func"]):
      raise ValueError("Rule argument 'func' should be a function that takes 2 arguments: scrapping_collector, element")
    
    #check if rule is not duplicated
    if rule in self.rules:
      raise ValueError("You cannot set the same rule twice. You can set a rule with different 'match' or 'func' arguments.")
    
    self.rules.append(rule)

  def request(self, url, cookies, headers):
    res = requests.get(url, cookies=cookies, headers=headers)
    return sp(res.content, "html.parser")
  
  def request_js(self, url, cookies, headers):
    print("The javascript version is not currently handling cookies and headers correctly.")
    cookies = {}
    headers = {}

    #set chrome headless options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    #set the driver
    driver = webdriver.Chrome(options=chrome_options)

    #add cookies
    # domain = get_domain(url)
    for key, value in cookies.items():
      driver.add_cookie({
        "name": key,
        "value": value,
      })

    #set interceptor to add headers
    driver.request_interceptor = lambda request: [request.headers.update(headers)]
    
    #visit the page
    driver.get(url)

    #TODO: add wait time for page to load
    return sp(driver.page_source, "html.parser")

  def visit(self, url, js=False, cookies=False, headers=False):
    #if we got cookies or/and headers ignore the class ones
    dcookies = cookies if cookies else self.cookies
    dheaders = headers if headers else self.headers

    #make the requests using requests or selenium based on js flag
    soup = self.request(url, dcookies, dheaders) if not js else self.request_js(url, dcookies, dheaders)
    dom = etree.HTML(str(soup)) 

    #match rules
    for rule in self.rules:
      elements = dom.xpath(rule["match"])
      for element in elements:
        #convert element back to beautifulsoup object
        bs_element = sp(etree.tostring(element), "html.parser")
        rule["func"](self, bs_element)

    return soup


def product_process(scrapper, element):
  title = element.find(attrs={"class": "product-thumbnail__description"}).text
  print(title)


if __name__ == "__main__":
  scrapper = BetterScrapper()

  scrapper.set_rule({
    "match": "//article[contains(@class, 'product-thumbnail')]",
    "func": product_process
  })

  scrapper.visit("https://www.auchan.fr/boucherie-volaille-poissonnerie/boucherie/ca-n0201?page=1")



# res = requests.get("https://www.auchan.fr/boucherie-volaille-poissonnerie/boucherie/ca-n0201?page=1")
# soup = sp(res.content, "html.parser")

# matches = soup.find("div", attrs={"class": "product-thumbnail__description"}).text
# for m in matches:
#   #############
