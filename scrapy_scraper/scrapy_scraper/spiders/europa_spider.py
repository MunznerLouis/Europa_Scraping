
import asyncio      #pip install asyncio (pas sûre de l'utiliser)    
import scrapy       #pip install scrapy  --> scrapy ver. > 2.4 pour utiliser asyncio

class europa_spider(scrapy.Spider):

    name = "europa_spider"
    start_urls = [
        "https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes=AT&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber=1&nextList=Next%3E"
    ]

    async def parse(self, response): #extrait les données du tableau
        for row in response.css('table#tblAccountSearchResult tr:nth-child(n+3)'):  #on commande a n+3 car les infos sont pas pertinentes avant ça

            dico_data ={                'National_Administrator': row.css('td:nth-child(1) span::text').get().strip(),
                'Account_Type': row.css('td:nth-child(2) span::text').get().strip(),
                'Account_Holder_Name': row.css('td:nth-child(3) span::text').get().strip(),
                'Installation/Aircraft_ID': row.css('td:nth-child(4) span::text').get().strip(),
                'Installation_Name/Aircraft_Operator_Code': row.css('td:nth-child(5) span::text').get().strip(),
                'Company_Regustration_No': row.css('td:nth-child(6) span::text').get().strip(),
                'Permit/Plan_ID': row.css('td:nth-child(7) span::text').get().strip(),
                'Permit/Plan_Date': row.css('td:nth-child(8) span::text').get().strip(),
                'Main_Activity_Type': row.css('td:nth-child(9) span::text').get().strip(),
                'Latest_Compliance_Code': row.css('td:nth-child(10) span::text').get().strip()} 
                #ajouter une colonne par année de Compliance "Compliance_2005 , Compliance_2006" etc avec des tuples pour les données des lignes

            yield dico_data
            

    async def parse_countries(self, response):
        return
        #to be coded

    async def parse_pages(self, response):
        return
        #to be coded

    async def parse_Compliances(self, response):
        return
        #to be coded


'''
lignes de commande pour lancer scrapy / store data dans un cmd : 
scrapy crawl europa_spider -O data.csv                 
scrapy runspider europa_spider.py -O data.csv

"runspider" permet de lancer une spider à la fois, alors que "crawl" peut permettre d'en lancer plusieurs

pour lancer Crawl il faut etre n'importe ou dans le projet scrapy

pour lancer runspider il faut être dans le meme directory que la spider (ici europa_spider) 
c'est pour ça que le .csv se sauvegarde automatiquement a cet endroit
'''