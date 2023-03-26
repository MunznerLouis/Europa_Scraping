import asyncio
import logging
import scrapy       #pip install scrapy  --> scrapy ver. > 2.4 pour utiliser asyncio


class europa_spider(scrapy.Spider):

    name = "europa_spider"
    start_urls = [
        "https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=accountTypeCode+ASC&backList=%3CBack&resultList.currentPageNumber=2"
    ]
    custom_settings = {'LOG_LEVEL': 'INFO',}

    def start_requests(self):  #override de la fonction start_request pour que la premiere fonction lancé soit 'parse_countries' et pas 'parse' 
        yield scrapy.Request("https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=accountTypeCode+ASC&backList=%3CBack&resultList.currentPageNumber=2", callback=self.parse_pages)     

    def parse_pages(self,response):
        pages = response.css("td.bgpagecontent input:nth-child(5)::attr(value)").get()
        for page in range(2,int(pages)+2):
            url = f"https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=accountTypeCode+ASC&backList=%3CBack&resultList.currentPageNumber="+ str(page)
            yield response.follow(url, callback=self.parse,meta={'page': page-1})


    def parse(self, response): #extrait les données du tableau
        page = response.meta['page']
        print("page",page,"sur",response.css("td.bgpagecontent input:nth-child(5)::attr(value)").get())
        
        # Check if content is None and if a request has already been made for this URL
        if response.css("td.bgpagecontent input:nth-child(5)::attr(value)").get() is None:
            logging.warning(f"Page content is None for {response.url}, retrying...")
            yield response.follow(
                response.url,
                callback=self.parse,
                meta={'page': page+1}
                )
        else:
            for row in response.css('table#tblAccountSearchResult tr:nth-child(n+3)'):  # (n+3) car les infos sont pas pertinentes avant ça
                dico_table_data ={               
                    'National_Administrator':                   row.css('td:nth-child(1) span::text').get(default=None).strip(),
                    'Account_Type':                             row.css('td:nth-child(2) span::text').get(default=None).strip(),
                    'Account_Holder_Name':                      row.css('td:nth-child(3) span::text').get(default=None).strip(),
                    'Installation/Aircraft_ID':                 row.css('td:nth-child(4) span::text').get(default=None).strip(),
                    'Installation_Name/Aircraft_Operator_Code': row.css('td:nth-child(5) span::text').get(default=None).strip(),
                    'Company_Regustration_No':                  row.css('td:nth-child(6) span::text').get(default=None).strip(),
                    'Permit/Plan_ID':                           row.css('td:nth-child(7) span::text').get(default=None).strip(),
                    'Permit/Plan_Date':                         row.css('td:nth-child(8) span::text').get(default=None).strip(),
                    'Main_Activity_Type':                       row.css('td:nth-child(9) span::text').get(default=None).strip(),
                    'Latest_Compliance_Code':                   row.css('td:nth-child(10) span::text').get(default=None).strip()} 
                url = row.css('td:nth-child(11) td:nth-child(2) a::attr(href)').get()
                if url:
                    yield response.follow(url, self.parse_compliances, meta={'dico_table_data': dico_table_data})


            #permet de passer le dico en paramètre pour la fonction parse_compliance

    def parse_compliances(self, response):
        dico_table_data = response.meta['dico_table_data'] 



        #General Information
        dico_table_data['Account_Status']=                               response.css('table#tblAccountGeneralInfo tr:nth-child(3) td:nth-child(6) span::text').get(default='').strip()

        #Details on Contact Information
        dico_table_data['Type']=                                         response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(1) span::text').get(default='').strip()
        dico_table_data['Legal_Entity_Identifier']=                      response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(3) span::text').get(default='').strip()
        dico_table_data['Main_Adress_Line']=                             response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(4) span::text').get(default='').strip()
        dico_table_data['Secondary_Adress_Line']=                        response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(5) span::text').get(default='').strip()
        dico_table_data['Postal_Code']=                                  response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(6) span::text').get(default='').strip()
        dico_table_data['City']=                                         response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(7) span::text').get(default='').strip()
        dico_table_data['Country']=                                      response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(8) span::text').get(default='').strip()
        dico_table_data['Telephone_1']=                                  response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(9) span::text').get(default='').strip()
        dico_table_data['Telephone_2']=                                  response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(10) span::text').get(default='').strip()
        dico_table_data['E-Mail_Adress']=                                response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(11) span::text').get(default='').strip()
        
        #other General Information
        dico_table_data['Monitoring_plan—year_of_expiry']=               response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(5) span::text').get(default='').strip()
        dico_table_data['Name_of_Subsidiary_undertaking']=               response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(6) span::text').get(default='').strip()
        dico_table_data['Name_of_Parent_undertaking']=                   response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(7) span::text').get(default='').strip()
        dico_table_data['E-PRTR_identification']=                        response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(8) span::text').get(default='').strip()
        dico_table_data['Call_Sign_(ICAO_designator)']=                  response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(9) span::text').get(default='').strip()
        dico_table_data['First_Year_of_Emissions']=                      response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(10) span::text').get(default='').strip()                      
        dico_table_data['Last_Year_of_Emissions']=                       response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(11) span::text').get(default='').strip()

        #EU Compliance Information
        if response.css('[id=tblChildDetails] div:nth-child(2)') == []:
            for row in response.css('[id=tblChildDetails] div table tr:nth-child(n+3):not(:nth-last-child(-n+6))'): #(-n+6) car les 7dernieres lignes servent à rien (et provoquent des erreurs)
                key_year = row.css('td:nth-child(2) span::text').get().strip()  
                for cell in row.css('tr'):
                    dico_table_data["EU_Compliance_"+key_year+"_Allowances_in_Allocation"] =          cell.css('td:nth-child(3) span::text').get(default='').strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Verified_Emissions"] =                cell.css('td:nth-child(4) span::text').get(default='').strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Units_Surrendered"] =                 cell.css('td:nth-child(5) span::text').get(default='').strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Cumulative_Surrendered_Units"] =      cell.css('td:nth-child(6) span::text').get(default='').strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Cumulative_Verified_Emissions"] =     cell.css('td:nth-child(7) span::text').get(default='').strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Compliance_Code"] =                   cell.css('td:nth-child(8) span::text').get(default='').strip()
        
        else:
            
            for row in response.css('[id=tblChildDetails] div:nth-child(1) table tr:nth-child(n+3):not(:nth-last-child(-n+6))'): #(-n+6) car les 7dernieres lignes servent à rien (et provoquent des erreurs)
                key_year = row.css('td:nth-child(2) span::text').get().strip() 
                for cell in row.css('tr'):
                    dico_table_data["EU_Compliance_"+key_year+"_Allowances_in_Allocation"] =          cell.css('td:nth-child(3) span::text').get(default='').strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Verified_Emissions"] =                cell.css('td:nth-child(4) span::text').get(default='').strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Units_Surrendered"] =                 cell.css('td:nth-child(5) span::text').get(default='').strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Cumulative_Surrendered_Units"] =      cell.css('td:nth-child(6) span::text').get(default='').strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Cumulative_Verified_Emissions"] =     cell.css('td:nth-child(7) span::text').get(default='').strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Compliance_Code"] =                   cell.css('td:nth-child(8) span::text').get(default='').strip()

            #CH Compliance information - ONLY FOR AIRCRAFT OPERATOR ACCOUNT
            for row in response.css('[id=tblChildDetails] div:nth-child(2) table tr:nth-child(n+5):not(:nth-last-child(-n+4))'): #(-n+4) car les 7dernieres lignes servent à rien (et provoquent des erreurs)
                key_year = row.css('td:nth-child(2) span::text').get().strip()  
                for cell in row.css('tr'):
                    
                    dico_table_data["CH_Compliance_"+key_year+"_Allowances_in_Allocation"] =          cell.css('td:nth-child(3) span::text').get(default='').strip()
                    dico_table_data["CH_Compliance_"+key_year+"_Verified_Emissions"] =                cell.css('td:nth-child(4) span::text').get(default='').strip()
                    dico_table_data["CH_Compliance_"+key_year+"_Units_Surrendered"] =                 cell.css('td:nth-child(5) span::text').get(default='').strip()
                    dico_table_data["CH_Compliance_"+key_year+"_Cumulative_Surrendered_Units"] =      cell.css('td:nth-child(6) span::text').get(default='').strip()
                    dico_table_data["CH_Compliance_"+key_year+"_Cumulative_Verified_Emissions"] =     cell.css('td:nth-child(7) span::text').get(default='').strip()
                    dico_table_data["CH_Compliance_"+key_year+"_Compliance_Code"] =                   cell.css('td:nth-child(8) span::text').get(default='').strip()
        yield dico_table_data

'''
lignes de commande pour lancer scrapy / store data dans un cmd : 
scrapy crawl europa_spider -O data.csv    
ou             
scrapy runspider europa_spider.py -O ../../data.csv

"runspider" permet de lancer une spider à la fois, alors que "crawl" peut permettre d'en lancer plusieurs

pour lancer Crawl il faut etre n'importe ou dans le projet scrapy

pour lancer runspider il faut être dans le meme directory que la spider (ici europa_spider) 
'''