import asyncio      #pip install asyncio (pas sûre de l'utiliser)    
import scrapy       #pip install scrapy  --> scrapy ver. > 2.4 pour utiliser asyncio

class europa_spider(scrapy.Spider):

    name = "europa_spider"
    start_urls = [
        "https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes=AT&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber=1&nextList=Next%3E"
    ]
    custom_settings = {
        'LOG_LEVEL': 'WARNING',
    }

    def start_requests(self):  #override de la fonction start_request pour que la premiere fonction lancé soit 'parse_countries' et pas 'parse' 
        yield scrapy.Request("https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes=AT&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber=1&nextList=Next%3", callback=self.parse_countries)

    def parse_countries(self, response):
        countries = response.xpath("//table[@id='tblAccountSearchCriteria']//select[@name='account.registryCodes']/option/@value").extract()
        for country in countries:
            url = f"https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber=1&nextList=Next%3"
            yield scrapy.Request(url, callback=self.parse_pages, meta={'country': country})       

    def parse_pages(self,response):
        pages = response.css("td.bgpagecontent input:nth-child(5)::attr(value)").get()
        country = response.meta['country']
        for page in range(int(pages)):
            url = f"https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={page}&nextList=Next%3"
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response): #extrait les données du tableau
        for row in response.css('table#tblAccountSearchResult tr:nth-child(n+3)'):  # (n+3) car les infos sont pas pertinentes avant ça
            dico_table_data ={               
                'National_Administrator':                   None if not row.css('td:nth-child(1) span::text').get() else row.css('td:nth-child(1) span::text').get().strip(),
                'Account_Type':                             None if not row.css('td:nth-child(2) span::text').get() else row.css('td:nth-child(2) span::text').get().strip(),
                'Account_Holder_Name':                      None if not row.css('td:nth-child(3) span::text').get() else row.css('td:nth-child(3) span::text').get().strip(),
                'Installation/Aircraft_ID':                 None if not row.css('td:nth-child(4) span::text').get() else row.css('td:nth-child(4) span::text').get().strip(),
                'Installation_Name/Aircraft_Operator_Code': None if not row.css('td:nth-child(5) span::text').get() else row.css('td:nth-child(5) span::text').get().strip(),
                'Company_Regustration_No':                  None if not row.css('td:nth-child(6) span::text').get() else row.css('td:nth-child(6) span::text').get().strip(),
                'Permit/Plan_ID':                           None if not row.css('td:nth-child(7) span::text').get() else row.css('td:nth-child(7) span::text').get().strip(),
                'Permit/Plan_Date':                         None if not row.css('td:nth-child(8) span::text').get() else row.css('td:nth-child(8) span::text').get().strip(),
                'Main_Activity_Type':                       None if not row.css('td:nth-child(9) span::text').get() else row.css('td:nth-child(9) span::text').get().strip(),
                'Latest_Compliance_Code':                   None if not row.css('td:nth-child(10) span::text').get() else row.css('td:nth-child(10) span::text').get().strip()} 
            url = row.css('td:nth-child(11) td:nth-child(2) a::attr(href)').get()

            yield scrapy.Request(url, self.parse_compliances,meta={'dico_table_data': dico_table_data})

            #permet de passer le dico en paramètre pour la fonction parse_compliance

    def parse_compliances(self, response):
        dico_table_data = response.meta['dico_table_data'] 



        #General Information
        dico_table_data['Account_Status']=                               None if not response.css('table#tblAccountGeneralInfo tr:nth-child(3) td:nth-child(6) span::text').get() else response.css('table#tblAccountGeneralInfo tr:nth-child(3) td:nth-child(6) span::text').get().strip()

        #Details on Contact Information
        dico_table_data['Type']=                                         None if not response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(1) span::text').get() else response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(1) span::text').get().strip()
        dico_table_data['Legal_Entity_Identifier']=                      None if not response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(3) span::text').get() else response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(3) span::text').get().strip()
        dico_table_data['Main_Adress_Line']=                             None if not response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(4) span::text').get() else response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(4) span::text').get().strip()
        dico_table_data['Secondary_Adress_Line']=                        None if not response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(5) span::text').get() else response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(5) span::text').get().strip()
        dico_table_data['Postal_Code']=                                  None if not response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(6) span::text').get() else response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(6) span::text').get().strip()
        dico_table_data['City']=                                         None if not response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(7) span::text').get() else response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(7) span::text').get().strip()
        dico_table_data['Country']=                                      None if not response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(8) span::text').get() else response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(8) span::text').get().strip()
        dico_table_data['Telephone_1']=                                  None if not response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(9) span::text').get() else response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(9) span::text').get().strip()
        dico_table_data['Telephone_2']=                                  None if not response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(10) span::text').get() else response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(10) span::text').get().strip()
        dico_table_data['E-Mail_Adress']=                                None if not response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(11) span::text').get() else response.css('table#tblAccountContactInfo tr:nth-child(3) td:nth-child(11) span::text').get().strip()
        
        #other General Information
        dico_table_data['Monitoring_plan—year_of_expiry']=               None if not response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(5) span::text').get() else response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(5) span::text').get().strip()
        dico_table_data['Name_of_Subsidiary_undertaking']=               None if not response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(6) span::text').get() else response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(6) span::text').get().strip()
        dico_table_data['Name_of_Parent_undertaking']=                   None if not response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(7) span::text').get() else response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(7) span::text').get().strip()
        dico_table_data['E-PRTR_identification']=                        None if not response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(8) span::text').get() else response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(8) span::text').get().strip()
        dico_table_data['Call_Sign_(ICAO_designator)']=                  None if not response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(9) span::text').get() else response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(9) span::text').get().strip()
        dico_table_data['First_Year_of_Emissions']=                      None if not response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(10) span::text').get() else response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(10) span::text').get().strip()                      
        dico_table_data['Last_Year_of_Emissions']=                       None if not response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(11) span::text').get() else response.css('table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(11) span::text').get().strip()

        #EU Compliance Information
        if not(response.css('[id=tblChildDetails] div:nth-child(2)')):
            for row in response.css('[id=tblChildDetails] div table tr:nth-child(n+3):not(:nth-last-child(-n+6))'): #(-n+6) car les 7dernieres lignes servent à rien (et provoquent des erreurs)
                key_year = row.css('td:nth-child(2) span::text').get().strip()  
                for cell in row.css('tr'):
                    dico_table_data["EU_Compliance_"+key_year+"_Allowances_in_Allocation"] =          None if not cell.css('td:nth-child(3) span::text').get() else row.css('td:nth-child(3) span::text').get().strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Verified_Emissions"] =                None if not cell.css('td:nth-child(4) span::text').get() else row.css('td:nth-child(4) span::text').get().strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Units_Surrendered"] =                 None if not cell.css('td:nth-child(5) span::text').get() else row.css('td:nth-child(5) span::text').get().strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Cumulative_Surrendered_Units"] =      None if not cell.css('td:nth-child(6) span::text').get() else row.css('td:nth-child(6) span::text').get().strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Cumulative_Verified_Emissions"] =     None if not cell.css('td:nth-child(7) span::text').get() else row.css('td:nth-child(7) span::text').get().strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Compliance_Code"] =                   None if not cell.css('td:nth-child(8) span::text').get() else row.css('td:nth-child(8) span::text').get().strip()
        
        else:
        
            #EU Compliance Information
            for row in response.css('[id=tblChildDetails] div:nth-child(1) table tr:nth-child(n+3):not(:nth-last-child(-n+6))'): #(-n+6) car les 7dernieres lignes servent à rien (et provoquent des erreurs)
                key_year = row.css('td:nth-child(2) span::text').get().strip()  
                for cell in row.css('tr'):
                    dico_table_data["EU_Compliance_"+key_year+"_Allowances_in_Allocation"] =          None if not cell.css('td:nth-child(3) span::text').get() else row.css('td:nth-child(3) span::text').get().strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Verified_Emissions"] =                None if not cell.css('td:nth-child(4) span::text').get() else row.css('td:nth-child(4) span::text').get().strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Units_Surrendered"] =                 None if not cell.css('td:nth-child(5) span::text').get() else row.css('td:nth-child(5) span::text').get().strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Cumulative_Surrendered_Units"] =      None if not cell.css('td:nth-child(6) span::text').get() else row.css('td:nth-child(6) span::text').get().strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Cumulative_Verified_Emissions"] =     None if not cell.css('td:nth-child(7) span::text').get() else row.css('td:nth-child(7) span::text').get().strip()
                    dico_table_data["EU_Compliance_"+key_year+"_Compliance_Code"] =                   None if not cell.css('td:nth-child(8) span::text').get() else row.css('td:nth-child(8) span::text').get().strip()
            #CH Compliance information - ONLY FOR AIRCRAFT OPERATOR ACCOUNT
            for row in response.css('[id=tblChildDetails] div:nth-child(2) table tr:nth-child(n+5):not(:nth-last-child(-n+4))'): #(-n+4) car les 7dernieres lignes servent à rien (et provoquent des erreurs)
                key_year = row.css('td:nth-child(2) span::text').get().strip()  
                for cell in row.css('tr'):
                    dico_table_data["CH_Compliance_"+key_year+"_Allowances_in_Allocation"] =          None if not cell.css('td:nth-child(3) span::text').get() else row.css('td:nth-child(3) span::text').get().strip()
                    dico_table_data["CH_Compliance_"+key_year+"_Verified_Emissions"] =                None if not cell.css('td:nth-child(4) span::text').get() else row.css('td:nth-child(4) span::text').get().strip()
                    dico_table_data["CH_Compliance_"+key_year+"_Units_Surrendered"] =                 None if not cell.css('td:nth-child(5) span::text').get() else row.css('td:nth-child(5) span::text').get().strip()
                    dico_table_data["CH_Compliance_"+key_year+"_Cumulative_Surrendered_Units"] =      None if not cell.css('td:nth-child(6) span::text').get() else row.css('td:nth-child(6) span::text').get().strip()
                    dico_table_data["CH_Compliance_"+key_year+"_Cumulative_Verified_Emissions"] =     None if not cell.css('td:nth-child(7) span::text').get() else row.css('td:nth-child(7) span::text').get().strip()
                    dico_table_data["CH_Compliance_"+key_year+"_Compliance_Code"] =                   None if not cell.css('td:nth-child(8) span::text').get() else row.css('td:nth-child(8) span::text').get().strip()
        print("nouvelle ligne ID : ",dico_table_data['Installation/Aircraft_ID'])
        yield dico_table_data

'''
lignes de commande pour lancer scrapy / store data dans un cmd : 
scrapy crawl europa_spider -O data.csv    
ou             
scrapy runspider europa_spider.py -O ../../data.csv

"runspider" permet de lancer une spider à la fois, alors que "crawl" peut permettre d'en lancer plusieurs

pour lancer Crawl il faut etre n'importe ou dans le projet scrapy


pour lancer runspider il faut être dans le meme directory que la spider (ici europa_spider) 
c'est pour ça que le .csv se sauvegarde automatiquement a cet endroit
'''