import asyncio      #pip install asyncio (pas sûre de l'utiliser)    
import scrapy       #pip install scrapy  --> scrapy ver. > 2.4 pour utiliser asyncio

class europa_spider(scrapy.Spider):

    name = "europa_spider"
    start_urls = [
        "https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes=AT&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber=1&nextList=Next%3E"
    ]

    def start_requests(self):  #override de la fonction start_request pour que la premiere fonction lancé soit 'parse_countries' et pas 'parse' 
        yield scrapy.Request("https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes=AT&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber=1&nextList=Next%3", callback=self.parse_countries_and_pages)

    async def parse_countries_and_pages(self, response):
        countries = response.xpath("//table[@id='tblAccountSearchCriteria']//select[@name='account.registryCodes']/option/@value").extract()
        for country in countries:
            pages = response.css("td.bgpagecontent input:nth-child(5)::attr(value)").get()
            for page in range(int(pages)):
                url=f"https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={page}&nextList=Next%3"
                yield scrapy.Request(url,callback=self.parse)        

    async def parse(self, response): #extrait les données du tableau

        for row in response.css('table#tblAccountSearchResult tr:nth-child(n+3)'):  # (n+3) car les infos sont pas pertinentes avant ça
            
            dico_table_data ={               
                'National_Administrator':                   None if not row.css('td:nth-child(1) span::text').get().strip() else row.css('td:nth-child(1) span::text').get().strip(),
                'Account_Type':                             None if not row.css('td:nth-child(2) span::text').get().strip() else row.css('td:nth-child(2) span::text').get().strip(),
                'Account_Holder_Name':                      None if not row.css('td:nth-child(3) span::text').get().strip() else row.css('td:nth-child(3) span::text').get().strip(),
                'Installation/Aircraft_ID':                 None if not row.css('td:nth-child(4) span::text').get().strip() else row.css('td:nth-child(4) span::text').get().strip(),
                'Installation_Name/Aircraft_Operator_Code': None if not row.css('td:nth-child(5) span::text').get().strip() else row.css('td:nth-child(5) span::text').get().strip(),
                'Company_Regustration_No':                  None if not row.css('td:nth-child(6) span::text').get().strip() else row.css('td:nth-child(6) span::text').get().strip(),
                'Permit/Plan_ID':                           None if not row.css('td:nth-child(7) span::text').get().strip() else row.css('td:nth-child(7) span::text').get().strip(),
                'Permit/Plan_Date':                         None if not row.css('td:nth-child(8) span::text').get().strip() else row.css('td:nth-child(8) span::text').get().strip(),
                'Main_Activity_Type':                       None if not row.css('td:nth-child(9) span::text').get().strip() else row.css('td:nth-child(9) span::text').get().strip(),
                'Latest_Compliance_Code':                   None if not row.css('td:nth-child(10) span::text').get().strip() else row.css('td:nth-child(10) span::text').get().strip()} 
            url = row.css('td:nth-child(11) td:nth-child(2) a::attr(href)').get()

            yield scrapy.Request(url, self.parse_compliances,meta={'dico_table_data': dico_table_data})



    async def parse_compliances(self, response):
        dico_table_data = response.meta['dico_table_data']        
        dico_compliances = {}
        for row in response.css('[id=tblChildDetails] div table tr:nth-child(n+3):not(:nth-last-child(-n+6))'): #(-n+6) car les 7dernieres lignes servent à rien (et provoquent des erreurs)
            key_year = row.css('td:nth-child(2) span::text').get().strip()
            dico_compliances["Compliance"+key_year] = ( {"Allowances_in_Allocation":        None if not row.css('td:nth-child(3) span::text').get().strip() else row.css('td:nth-child(3) span::text').get().strip()},
                                                        {"Verified_Emissions":              None if not row.css('td:nth-child(4) span::text').get().strip() else row.css('td:nth-child(4) span::text').get().strip()},
                                                        {"Units_Surrendered":               None if not row.css('td:nth-child(5) span::text').get().strip() else row.css('td:nth-child(5) span::text').get().strip()},
                                                        {"Cumulative_Surrendered_Units":    None if not row.css('td:nth-child(6) span::text').get().strip() else row.css('td:nth-child(6) span::text').get().strip()},
                                                        {"Cumulative_Verified_Emissions":   None if not row.css('td:nth-child(7) span::text').get().strip() else row.css('td:nth-child(7) span::text').get().strip()},
                                                        {"Compliance_Code":                 None if not row.css('td:nth-child(8) span::text').get().strip() else row.css('td:nth-child(8) span::text').get().strip()} )
        dico_data = dico_table_data | dico_compliances
        yield dico_data


'''
lignes de commande pour lancer scrapy / store data dans un cmd : 
scrapy crawl europa_spider -O data.csv                 
scrapy runspider europa_spider.py -O data.csv

"runspider" permet de lancer une spider à la fois, alors que "crawl" peut permettre d'en lancer plusieurs

pour lancer Crawl il faut etre n'importe ou dans le projet scrapy


pour lancer runspider il faut être dans le meme directory que la spider (ici europa_spider) 
c'est pour ça que le .csv se sauvegarde automatiquement a cet endroit
'''