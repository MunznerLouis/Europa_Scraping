import asyncio
import logging
import scrapy  # pip install scrapy  --> scrapy ver. > 2.4 pour utiliser asyncio

# lorsque la commande pour lancer la spider est lancé, c'est la fonction start_request qui sera lancé automatiquement en premier
class europa_spider(scrapy.Spider):
    """Une classe de spider pour collecter les Compliances du registre EU ETS.

    Cette classe de spider utilise le framework Scrapy pour collecter les données des Operator Holding account
    du registre EU ETS (European Union Emission Trading System). Elle utilise les
    bibliothèques asyncio et scrapy pour effectuer des requêtes asynchrones et
    parser les pages web. La classe est configurée pour gérer les requêtes,
    les réponses, et effectuer les actions nécessaires pour collecter les données
    de transaction et les stocker dans un fichier CSV.

    Attributes:
        name (str): Le nom du spider.
        start_urls (str): L'URL de départ pour la collecte des données des Operator Holding account.
        custom_settings (dict): Un dictionnaire de paramètres personnalisés pour la
            configuration du spider.

    Methods:
        start_requests(): Une méthode pour démarrer les requêtes du spider.
        parse_pages(response): Une méthode pour parser les pages de données des Operator Holding account.
        parse(response): Une méthode pour parser les données des Operator Holding account sur les pages web.
        parse_compliances(response): Une méthode pour parser les données des Operator Holding account de la 2eme pages.
    """
    name = "europa_spider"
    start_urls = "https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=accountTypeCode+ASC&backList=%3CBack&resultList.currentPageNumber=2"
    custom_settings = {
        "LOG_LEVEL": "INFO",
    }

    # override de la fonction start_request pour que la premiere fonction lancé soit 'parse_countries' et non 'parse'
    def start_requests(self):
        """Surcharger la fonction start_requests pour que la première fonction appelée soit 'parse_pages' au lieu de 'parse'.

        Yields:
            scrapy.Request: La requête à traiter par la fonction de rappel 'parse_pages'.
        """
        yield scrapy.Request(
            "https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=accountTypeCode+ASC&backList=%3CBack&resultList.currentPageNumber=2",
            callback=self.parse_pages,
        )

    # fonction pour connaitre le nombre de pages a scraper créer une requête pour chaque page
    def parse_pages(self, response):
        """Méthode de parsing pour extraire les données des pages du site web.

        Args:
            response (scrapy.http.Response): La réponse HTTP de la page web à analyser.

        Yields:
            scrapy.http.Request: Une requête HTTP pour suivre les liens des pages suivantes.
        """
        pages = response.css("td.bgpagecontent input:nth-child(5)::attr(value)").get()

        # permet de set up les colonnes du .csv .Bien que le contenu du csv soit rempli dynamiquement, le header est configuré statiquement
        yield response.follow(
            self.start_urls, callback=self.parse, meta={"page": 1}, priority=1
        )

        for page in range(3, int(pages) + 2):
            url = (
                f"https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=fr&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=accountTypeCode+ASC&backList=%3CBack&resultList.currentPageNumber="
                + str(page)
            )
            yield response.follow(url, callback=self.parse, meta={"page": page - 1})

    # extrait les données du tableau
    def parse(self, response):
        """Parse function pour extraire des données d'une réponse de requête http.

        Args:
            response (scrapy.http.Response): L'objet réponse recu de site web.

        Yields:
            dict: Un dictionnaire contenant les données récupérées du site.
        """
        page = response.meta["page"]
        print(
            "page",
            page,
            "sur",
            response.css("td.bgpagecontent input:nth-child(5)::attr(value)").get(),
        )

        # Si il y a eu une erreur lors du chargement de la page, relance une requête pour retenter une connexion
        if (
            response.css("td.bgpagecontent input:nth-child(5)::attr(value)").get()
            is None
        ):
            logging.warning(f"Page content is None for {response.url}, retrying...")
            yield response.follow(
                response.url, callback=self.parse, meta={"page": page + 1}
            )
        else:
            for row in response.css(
                "table#tblAccountSearchResult tr:nth-child(n+3)"
            ):  # on commance à tr:nth-child(n+3) car les infos sont pas pertinentes avant ça
                dico_table_data = {
                    "National_Administrator": row.css("td:nth-child(1) span::text")
                    .get(default=None)
                    .strip(),
                    "Account_Type": row.css("td:nth-child(2) span::text")
                    .get(default=None)
                    .strip(),
                    "Account_Holder_Name": row.css("td:nth-child(3) span::text")
                    .get(default=None)
                    .strip(),
                    "Installation/Aircraft_ID": row.css("td:nth-child(4) span::text")
                    .get(default=None)
                    .strip(),
                    "Installation_Name/Aircraft_Operator_Code": row.css(
                        "td:nth-child(5) span::text"
                    )
                    .get(default=None)
                    .strip(),
                    "Company_Regustration_No": row.css("td:nth-child(6) span::text")
                    .get(default=None)
                    .strip(),
                    "Permit/Plan_ID": row.css("td:nth-child(7) span::text")
                    .get(default=None)
                    .strip(),
                    "Permit/Plan_Date": row.css("td:nth-child(8) span::text")
                    .get(default=None)
                    .strip(),
                    "Main_Activity_Type": row.css("td:nth-child(9) span::text")
                    .get(default=None)
                    .strip(),
                    "Latest_Compliance_Code": row.css("td:nth-child(10) span::text")
                    .get(default=None)
                    .strip(),
                }
                url = row.css("td:nth-child(11) td:nth-child(2) a::attr(href)").get()
                if url:
                    # permet de passer à la fonction parse_Compliance, pour recuperer les données des Compliances
                    yield response.follow(
                        url,
                        self.parse_compliances,
                        meta={"dico_table_data": dico_table_data},
                    )

    def parse_compliances(self, response):
        """Méthode pour extraire les informations des données Compliances d'une réponse de requête.

        Args:
            response (scrapy.http.Response): La réponse de la requête à analyser.

        Yields:
            dict: Un dictionnaire contenant les informations des Compliances extraites de la réponse.
        """
        dico_table_data = response.meta["dico_table_data"]

        # General Information
        dico_table_data["Account_Status"] = (
            response.css(
                "table#tblAccountGeneralInfo tr:nth-child(3) td:nth-child(6) span::text"
            )
            .get(default="")
            .strip()
        )
        # La partie .strip() est obligatoire, sinon nous recuperons des données sous ce format '&nbsp;Operator Holding Account&nbsp;'
        # Details on Contact Information
        dico_table_data["Type"] = (
            response.css(
                "table#tblAccountContactInfo tr:nth-child(3) td:nth-child(1) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Legal_Entity_Identifier"] = (
            response.css(
                "table#tblAccountContactInfo tr:nth-child(3) td:nth-child(3) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Main_Adress_Line"] = (
            response.css(
                "table#tblAccountContactInfo tr:nth-child(3) td:nth-child(4) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Secondary_Adress_Line"] = (
            response.css(
                "table#tblAccountContactInfo tr:nth-child(3) td:nth-child(5) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Postal_Code"] = (
            response.css(
                "table#tblAccountContactInfo tr:nth-child(3) td:nth-child(6) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["City"] = (
            response.css(
                "table#tblAccountContactInfo tr:nth-child(3) td:nth-child(7) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Country"] = (
            response.css(
                "table#tblAccountContactInfo tr:nth-child(3) td:nth-child(8) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Telephone_1"] = (
            response.css(
                "table#tblAccountContactInfo tr:nth-child(3) td:nth-child(9) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Telephone_2"] = (
            response.css(
                "table#tblAccountContactInfo tr:nth-child(3) td:nth-child(10) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["E-Mail_Adress"] = (
            response.css(
                "table#tblAccountContactInfo tr:nth-child(3) td:nth-child(11) span::text"
            )
            .get(default="")
            .strip()
        )

        # other General Information
        dico_table_data["Monitoring_plan—year_of_expiry"] = (
            response.css(
                "table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(5) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Name_of_Subsidiary_undertaking"] = (
            response.css(
                "table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(6) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Name_of_Parent_undertaking"] = (
            response.css(
                "table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(7) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["E-PRTR_identification"] = (
            response.css(
                "table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(8) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Call_Sign_(ICAO_designator)"] = (
            response.css(
                "table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(9) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["First_Year_of_Emissions"] = (
            response.css(
                "table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(10) span::text"
            )
            .get(default="")
            .strip()
        )
        dico_table_data["Last_Year_of_Emissions"] = (
            response.css(
                "table#tblChildDetails table:nth-child(1) tr:nth-child(3) td:nth-child(11) span::text"
            )
            .get(default="")
            .strip()
        )

        # Recupère les informations lié aux EU_Compliance avec UN SEUL TABLEAU
        if response.css("[id=tblChildDetails] div:nth-child(2)") == []:
            for row in response.css(
                "[id=tblChildDetails] div table tr:nth-child(n+3)"
            ):  # (-n+6) car les 7dernieres lignes servent à rien (et provoquent des erreurs)
                key_year = row.css("td:nth-child(2) span::text").get(default="").strip()
                if len(key_year) == 4:
                    for cell in row.css("tr"):
                        dico_table_data[
                            "EU_Compliance_" + key_year + "_Allowances_in_Allocation"
                        ] = (
                            cell.css("td:nth-child(3) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "EU_Compliance_" + key_year + "_Verified_Emissions"
                        ] = (
                            cell.css("td:nth-child(4) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "EU_Compliance_" + key_year + "_Units_Surrendered"
                        ] = (
                            cell.css("td:nth-child(5) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "EU_Compliance_"
                            + key_year
                            + "_Cumulative_Surrendered_Units"
                        ] = (
                            cell.css("td:nth-child(6) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "EU_Compliance_"
                            + key_year
                            + "_Cumulative_Verified_Emissions"
                        ] = (
                            cell.css("td:nth-child(7) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "EU_Compliance_" + key_year + "_Compliance_Code"
                        ] = (
                            cell.css("td:nth-child(8) span::text")
                            .get(default="")
                            .strip()
                        )

        # Recupère les informations lié aux EU_Compliance ET CH_Compliance lorsqu'il y a DEUX TABLEAUX
        else:

            for row in response.css(
                "[id=tblChildDetails] div:nth-child(1) table tr:nth-child(n+3)"
            ):  # (-n+6) car les 7dernieres lignes servent à rien (et provoquent des erreurs)
                key_year = row.css("td:nth-child(2) span::text").get(default="").strip()
                if len(key_year) == 4:
                    for cell in row.css("tr"):
                        dico_table_data[
                            "EU_Compliance_" + key_year + "_Allowances_in_Allocation"
                        ] = (
                            cell.css("td:nth-child(3) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "EU_Compliance_" + key_year + "_Verified_Emissions"
                        ] = (
                            cell.css("td:nth-child(4) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "EU_Compliance_" + key_year + "_Units_Surrendered"
                        ] = (
                            cell.css("td:nth-child(5) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "EU_Compliance_"
                            + key_year
                            + "_Cumulative_Surrendered_Units"
                        ] = (
                            cell.css("td:nth-child(6) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "EU_Compliance_"
                            + key_year
                            + "_Cumulative_Verified_Emissions"
                        ] = (
                            cell.css("td:nth-child(7) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "EU_Compliance_" + key_year + "_Compliance_Code"
                        ] = (
                            cell.css("td:nth-child(8) span::text")
                            .get(default="")
                            .strip()
                        )

            # CH Compliance information - Seulement pour AIRCRAFT OPERATOR ACCOUNT
            for row in response.css(
                "[id=tblChildDetails] div:nth-child(2) table tr:nth-child(n+5):not(:nth-last-child(-n+4))"
            ):  # (-n+4) car les 7dernieres lignes servent à rien (et provoquent des erreurs)
                key_year = row.css("td:nth-child(2) span::text").get(default="").strip()
                if len(key_year) == 4:
                    for cell in row.css("tr"):

                        dico_table_data[
                            "CH_Compliance_" + key_year + "_Allowances_in_Allocation"
                        ] = (
                            cell.css("td:nth-child(3) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "CH_Compliance_" + key_year + "_Verified_Emissions"
                        ] = (
                            cell.css("td:nth-child(4) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "CH_Compliance_" + key_year + "_Units_Surrendered"
                        ] = (
                            cell.css("td:nth-child(5) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "CH_Compliance_"
                            + key_year
                            + "_Cumulative_Surrendered_Units"
                        ] = (
                            cell.css("td:nth-child(6) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "CH_Compliance_"
                            + key_year
                            + "_Cumulative_Verified_Emissions"
                        ] = (
                            cell.css("td:nth-child(7) span::text")
                            .get(default="")
                            .strip()
                        )
                        dico_table_data[
                            "CH_Compliance_" + key_year + "_Compliance_Code"
                        ] = (
                            cell.css("td:nth-child(8) span::text")
                            .get(default="")
                            .strip()
                        )

        # permet d'envoyer le dictionnaire en tant que nouvelle ligne dans le csv.
        yield dico_table_data


"""
lignes de commande à mettre dans un cmd pour lancer scrapy / stocker les données  : 
    scrapy crawl europa_spider -O data.csv    
ou             
    scrapy runspider europa_spider.py -O ../../data.csv

"runspider" permet de lancer une spider à la fois, alors que "crawl" peut permettre d'en lancer plusieurs

pour lancer Crawl il faut etre n'importe ou dans le projet scrapy

pour lancer runspider il faut être dans le meme directory que la spider (ici europa_spider) 
"""
