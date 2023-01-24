import asyncio      #pip install asyncio (pas sûre de l'utiliser)    
import scrapy       #pip install scrapy  --> scrapy ver. > 2.4 pour utiliser asyncio

class transaction_spider(scrapy.Spider):

    name = "transaction_spider"
    
    start_urls = [
        "https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=-1&destinationRegistry=-1&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&search=Search&currentSortSettings="
    ]


    def start_requests(self):  #override de la fonction start_request pour que la premiere fonction lancé soit 'parse_countries' et pas 'parse' 
        yield scrapy.Request("https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=-1&destinationRegistry=-1&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&search=Search&currentSortSettings=", callback=self.parse_pages)

    async def parse_pages(self, response):

        pages = int(response.xpath("//input[@name='resultList.lastPageNumber']/@value").get())
        #<input type="text" name="resultList.lastPageNumber" size="4" value="55342" disabled="disabled" class="cellinset">


        for page in range(pages):
            url=url = f"https://ec.europa.eu/clima/ets/transaction.do?languageCode=fr&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=-1&destinationRegistry=-1&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&currentSortSettings=&resultList.currentPageNumber={page}&nextList=Next%3E"
            yield scrapy.Request(url,callback=self.parse)


    async def parse(self, response): #extrait les données du tableau
        for row in response.css('table#tblTransactionSearchResult tr:nth-child(n+3)'):  #on commande a n+3 car les infos sont pas pertinentes avant ça

            dico_data ={                
                'Transaction_ID': row.css('td:nth-child(1) span::text').get().strip(),
                'Transaction_Type': row.css('td:nth-child(2) span::text').get().strip(),
                'Transaction_Date': row.css('td:nth-child(3) span::text').get().strip(),
                'Transaction_Status': row.css('td:nth-child(4) span::text').get().strip(),
                'Transferring_Registry': row.css('td:nth-child(5) span::text').get().strip(),
                'Transferring_Account_Type': row.css('td:nth-child(6) span::text').get().strip(),
                'Transferring_Account_Name': row.css('td:nth-child(7) span::text').get().strip(),
                'Transferring_Account_Identifier': row.css('td:nth-child(8) span::text').get().strip(),
                'Transferring_Account_Holder': row.css('td:nth-child(9) span::text').get().strip(),
                'Acquiring_Registry': row.css('td:nth-child(10) span::text').get().strip(),
                'Acquiring_Account_Type': row.css('td:nth-child(11) span::text').get().strip(),
                'Acquiring_Account_Name': row.css('td:nth-child(12) span::text').get().strip(), 
                'Acquiring_Account_Identifier': row.css('td:nth-child(13) span::text').get().strip(), 
                'Acquiring_Account_Holder': row.css('td:nth-child(14) span::text').get().strip(),  
                'Nb_of_Units': row.css('td:nth-child(15) span::text').get().strip()          
                
                } 
              

            yield dico_data
