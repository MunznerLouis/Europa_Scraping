import scrapy
from datetime import datetime

class transaction_check(scrapy.Spider):
    name = "transaction_check"
    start_urls = [
        "https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=-1&destinationRegistry=-1&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&search=Search&currentSortSettings="
    ]

    def parse(self, response):
        nb_pages = response.xpath("//input[@name='resultList.lastPageNumber']/@value").get()
        lastdate = response.css("table#tblTransactionSearchResult tr:nth-child(3) td:nth-child(3) span::text").get().strip()

        #option 'r' pour recuperer les infos du .txt
        with open("../../transaction_check.txt", "r") as f:
            lines = f.readlines()
        p = lines[3].split(' : ')[-1].strip()
        date = lines[4].split(' : ')[-1].strip()
        
        #option 'w' pour overwrite par dessus
        with open("../../transaction_check.txt", "w") as f:
            f.write(f"Date du dernier lancement du script transaction_check.py : {datetime.now()}\n")
            #print([p,nb_pages,date,lastdate])   #debug
            if p != nb_pages or date != lastdate:
                f.write(f"Date de dernière update du fichier transaction_check.txt : {datetime.now()}\n\n")
                f.write(f"Nombre de lignes de la dernière update : {nb_pages}\n")
                f.write(f"Date de dernière update : {lastdate}")

                #lancer la commande bash 'scrapy crawl transaction_spider -O ../../data.csv'

                print("File updated.")
            else:
                f.write(''.join(lines[1:]))
                print("File already up to date.")
