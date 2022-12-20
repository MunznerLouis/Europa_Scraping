#La V2 utilise la page "print" permettant d'afficher toute les pages sur un seul url, evitant donc de faire une nouvelle requête pour chaque changement de page
#Moins de requêtes => site moins saturé + Scraper plus rapide => proprio du site content + jury content => mieux
#par rapport a beautifulsoup, on fait qu'une seul requête par pays, donc 33 requêtes asynchrones, contre ~1600 requêtes (pas asynchrone) avant => mieux

import asyncio      #pip install asyncio    
import requests  #pas sûre si on l'utilisera
import scrapy       #pip install scrapy  --> scrapy ver. > 2.4 pour utiliser asyncio

class europa_spider(scrapy.Spider):

    name = "europa_spider"
    start_urls = [
        "https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes=AT&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber=2&print=Print"
    ]
    def start_requests(self):  #override de la fonction start_request pour que la premiere fonction lancé soit 'parse_countries' et pas 'parse' 
        yield scrapy.Request("https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes=AT&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber=2&print=Print", callback=self.parse_countries)

    async def parse_countries(self, response):
        # Extract the list of countries from the form
        countries = response.xpath("//table[@id='tblAccountSearchCriteria']//select[@name='account.registryCodes']/option/@value").extract()
        print("CHECKPOINT 1",countries,"TEST",countries[1])
        for country in countries:
            url=f"https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber=2&print=Print"
            print("le pays scrapé est :",country,"avec pour url :\n",url)

            yield scrapy.Request(url,callback=self.parse)
            
    async def parse(self, response): #extrait les données du tableau
        
        accounts = response.xpath('/html/body/ul[2]/li')
        for account in accounts:
            data =[]
            for li in account.xpath('.//ul/li'):
                element = li.xpath(".//span[@class='value']/text()").get()
                data.append(element)
            yield {
                "National Administrator": data[9],
                "Account Type": data[8],
                "Account Holder Name": data[7],
                "Main Activity Type":data[6],
                "Permit/Plan Date":data[5],
                "Installation/Aircraft Operator ID":data[4],
                "Permit/Plan ID":data[3],
                "Main Activity Type Code":data[2],
                "Installation Name/Aircraft Operator Code: ":data[1],
                "Latest Compliance Code":data[0],
                }



#lignes de commande pour lancer scrapy / store data dans un cmd : 
# en Json :      scrapy crawl europa_spiderV2 -O data.json                 O majuscule pour Override au cas ou il y a deja un fichier data.json
# en csv  :      scrapy crawl europa_spiderV2 -o data.csv                  O majuscule fonctionne pas pour override en format csv
#il en existe surement plus