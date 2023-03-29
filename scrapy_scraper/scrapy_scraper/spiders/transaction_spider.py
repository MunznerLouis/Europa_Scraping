import asyncio      #pip install asyncio (pas sûre de l'utiliser)    
import scrapy       #pip install scrapy  --> scrapy ver. > 2.4 pour utiliser asyncio
import logging
from datetime import datetime, timedelta


class transaction_spider(scrapy.Spider):

    name = "transaction_spider"
    
    start_urls = "https://ec.europa.eu/clima/ets/transaction.do?endDate=&suppTransactionType=-1&transactionStatus=4&originatingAccountType=-1&originatingAccountIdentifier=&originatingAccountHolder=&languageCode=en&destinationAccountIdentifier=&transactionID=&transactionType=-1&destinationAccountType=-1&search=Search&toCompletionDate=&originatingRegistry=-1&destinationAccountHolder=&fromCompletionDate=&destinationRegistry=-1&startDate=&TITLESORT-currentSortSettings-transactionDate-H=A&currentSortSettings=transactionDate%20ASC"
    
    custom_settings = {
        'LOG_LEVEL': 'INFO',
    }

    def start_requests(self):  #override de la fonction start_request pour que la premiere fonction lancé soit 'parse_checker' et pas 'parse' 
        yield scrapy.Request(self.start_urls, callback=self.parse_checker)
    
    #PARTIE VERIF SI IL FAUT SCRAP
    def parse_checker(self, response):
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        last_date = response.css("table#tblTransactionSearchResult tr:nth-child(3) td:nth-child(3) span::text").get(default='').strip()

        with open("../../transaction_check.txt", "r") as f:
            lines = f.readlines()
        date_verif = lines[3].split(' : ')[-1].strip()
        print("DATE",last_date,'==',date_verif,date_verif==last_date)

        with open("../../transaction_check.txt", "w") as f:
            f.write(f"Date du dernier lancement du script transaction_spider.py : {datetime.now()}\n")
            if last_date != date_verif:
                f.write(f"Date de la dernière update du fichier transaction_check.txt : {datetime.now()}\n\n")
                f.write(f"Date de la dernière update du site : {last_date}\n")
                print("File updated.")
            else:
                f.write(''.join(lines[1:]))
                print("File already up to date.")
        
        delta = datetime.now()-datetime.strptime(lines[1].split(' : ')[-1].strip(),date_format)
        print("écart entre les deux dates : ",delta)
        #on remet la meme condition car le script shell peut pas se lancer dans le 'with open():'
        if date_verif !=last_date or delta >= timedelta(days=90):
            yield scrapy.Request("https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=-1&destinationRegistry=-1&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&search=Search&currentSortSettings=", callback=self.parse_pages)

    #----- PARTIE SCRAPING -----
    async def parse_pages(self, response):
        pages = int(response.xpath("//input[@name='resultList.lastPageNumber']/@value").get())
        for page in range(2,pages+2):
            url = f"https://ec.europa.eu/clima/ets/transaction.do?languageCode=fr&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=-1&destinationRegistry=-1&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&currentSortSettings=&backList=%3CBack&resultList.currentPageNumber={page}"
            yield response.follow(url,callback=self.parse)

    async def parse(self, response): #extrait les données du tableau
        total_pages = response.xpath("//input[@name='resultList.lastPageNumber']/@value").get()
        page = response.xpath("//input[@name='resultList.currentPageNumber']/@value").get()
        print(f"page {page} sur {total_pages}")

        if total_pages is None:
            logging.warning(f"Page content is None for {response.url}, retrying...")
            yield response.follow(
                response.url,
                callback=self.parse
                )
        else:
            for row in response.css('table#tblTransactionSearchResult tr:nth-child(n+3)'):  #on commande a n+3 car les infos sont pas pertinentes avant ça
                dico_data ={                
                    'Transaction_ID':                   row.css('td:nth-child(1) span::text').get(default='').strip(),
                    'Transaction_Type':                 row.css('td:nth-child(2) span::text').get(default='').strip(),
                    'Transaction_Date':                 row.css('td:nth-child(3) span::text').get(default='').strip(),
                    'Transaction_Status':               row.css('td:nth-child(4) span::text').get(default='').strip(),
                    'Transferring_Registry':            row.css('td:nth-child(5) span::text').get(default='').strip(),
                    'Transferring_Account_Type':        row.css('td:nth-child(6) span::text').get(default='').strip(),
                    'Transferring_Account_Name':        row.css('td:nth-child(7) span::text').get(default='').strip(),
                    'Transferring_Account_Identifier':  row.css('td:nth-child(8) span::text').get(default='').strip(),
                    'Transferring_Account_Holder':      row.css('td:nth-child(9) span::text').get(default='').strip(),
                    'Acquiring_Registry':               row.css('td:nth-child(10) span::text').get(default='').strip(),
                    'Acquiring_Account_Type':           row.css('td:nth-child(11) span::text').get(default='').strip(),
                    'Acquiring_Account_Name':           row.css('td:nth-child(12) span::text').get(default='').strip(),  
                    'Acquiring_Account_Identifier':     row.css('td:nth-child(13) span::text').get(default='').strip(), 
                    'Acquiring_Account_Holder':         row.css('td:nth-child(14) span::text').get(default='').strip(),  
                    'Nb_of_Units':                      row.css('td:nth-child(15) span::text').get(default='').strip()         
                    } 
                yield dico_data

