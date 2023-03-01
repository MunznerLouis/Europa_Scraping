import scrapy
from datetime import datetime, timedelta
import subprocess

class transaction_check(scrapy.Spider):
    name = "transaction_check"
    start_urls = [
        "https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=-1&destinationRegistry=-1&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&search=Search&currentSortSettings="
    ]

    def parse(self, response):
        nb_pages = response.xpath("//input[@name='resultList.lastPageNumber']/@value").get()

        #option 'r' pour recuperer les infos du .txt
        with open("../../transaction_check.txt", "r") as f:
            lines = f.readlines()
        p = lines[3].split(' : ')[-1].strip()
        
        #option 'w' pour overwrite par dessus
        with open("../../transaction_check.txt", "w") as f:
            f.write(f"Date du dernier lancement du script transaction_check.py : {datetime.now()}\n")
            #print([p,nb_pages,date,lastdate])   #debug
            if p != nb_pages:
                f.write(f"Date de dernière update du fichier transaction_check.txt : {datetime.now()}\n\n")
                f.write(f"Nombre de pages de la dernière update : {nb_pages}\n")
                print("File updated.")
            else:
                f.write(''.join(lines[1:]))
                print("File already up to date.")

        date_format = '%Y-%m-%d %H:%M:%S.%f'
        delta = datetime.now()-datetime.strptime(lines[1].split(' : ')[-1].strip(),date_format)
        print("écart entre les deux dates : ",delta)
        #on remet la meme condition car le script shell peut pas se lancer dans le 'with open():'
        if p !=nb_pages or delta >= timedelta(days=30):
            subprocess.run("scrapy crawl transaction_spider -O ../../data_transaction.csv", shell=True) #marche pas


