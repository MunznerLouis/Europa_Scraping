import scrapy  # pip install scrapy  --> scrapy ver. > 2.4 pour utiliser asyncio
import logging
from datetime import datetime, timedelta


class transaction_spider(scrapy.Spider):
    """Une classe de spider pour collecter les transactions du registre EU ETS.

    Cette classe de spider utilise le framework Scrapy pour collecter les transactions
    du registre EU ETS (European Union Emission Trading System). Elle utilise les
    bibliothèques asyncio et scrapy pour effectuer des requêtes asynchrones et
    parser les pages web. La classe est configurée pour gérer les requêtes,
    les réponses, et effectuer les actions nécessaires pour collecter les données
    de transaction et les stocker dans un fichier CSV.

    Attributes:
        name (str): Le nom du spider.
        start_urls (str): L'URL de départ pour la collecte des transactions.
        custom_settings (dict): Un dictionnaire de paramètres personnalisés pour la
            configuration du spider.

    Methods:
        start_requests(): Une méthode pour démarrer les requêtes du spider.
        parse_checker(response): Une méthode pour vérifier si le fichier CSV est à jour.
        parse_pages(response): Une méthode pour parser les pages de transactions.
        parse(response): Une méthode pour parser les transactions sur les pages web.
    """
    name = "transaction_spider"

    start_urls = "https://ec.europa.eu/clima/ets/transaction.do?endDate=&suppTransactionType=-1&transactionStatus=4&originatingAccountType=-1&originatingAccountIdentifier=&originatingAccountHolder=&languageCode=en&destinationAccountIdentifier=&transactionID=&transactionType=-1&destinationAccountType=-1&search=Search&toCompletionDate=&originatingRegistry=-1&destinationAccountHolder=&fromCompletionDate=&destinationRegistry=-1&startDate=&TITLESORT-currentSortSettings-transactionDate-H=A&currentSortSettings=transactionDate%20ASC"

    custom_settings = {
        "LOG_LEVEL": "INFO",
    }

    def start_requests(self):  # override de la fonction start_request pour que la premiere fonction lancé soit 'parse_checker' et pas 'parse'
        """Surcharger la fonction start_requests pour que la première fonction appelée soit 'parse_checker' au lieu de 'parse'.

        Yields:
            scrapy.Request: La requête à traiter par la fonction de rappel 'parse_checker'.
        """
        yield scrapy.Request(self.start_urls, callback=self.parse_checker)

    # ------- PARTIE POUR VERIFIER SI NOTRE CSV EST DEJA A JOUR -------
    def parse_checker(self, response):
        """Vérifie les transactions les plus récentes dans le registre EU ETS.

        Cette fonction compare la date de la dernière mise à jour du fichier
        'transaction_check.txt' avec la date de la dernière transaction sur le site,
        et effectue des actions en conséquence.

        Args:
            response (scrapy.Response): La réponse HTTP de la page à parser.

        Yields:
            scrapy.Request: Une demande de suivi pour la page de transactions si
            certaines conditions sont remplies.
        """
        date_format = "%Y-%m-%d %H:%M:%S.%f"
        last_date = (
            response.css(
                "table#tblTransactionSearchResult tr:nth-child(3) td:nth-child(3) span::text"
            )
            .get(default="")
            .strip()
        )

        with open("../../transaction_check.txt", "r") as f:
            lines = f.readlines()
        date_verif = lines[3].split(" : ")[-1].strip()
        print("DATE", last_date, "==", date_verif, date_verif == last_date)

        with open("../../transaction_check.txt", "w") as f:
            f.write(
                f"Date du dernier lancement du script transaction_spider.py : {datetime.now()}\n"
            )
            if last_date != date_verif:
                f.write(
                    f"Date de la dernière update du fichier transaction_check.txt : {datetime.now()}\n\n"
                )
                f.write(f"Date de la dernière update du site : {last_date}\n")
                print("File updated.")
            else:
                f.write("".join(lines[1:]))
                print("File already up to date.")

        delta = datetime.now() - datetime.strptime(
            lines[1].split(" : ")[-1].strip(), date_format
        )
        print("écart entre les deux dates : ", delta)
        # on remet la meme condition car le script shell peut pas se lancer dans le 'with open():'
        if date_verif != last_date or delta >= timedelta(days=90):
            yield scrapy.Request(
                "https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=-1&destinationRegistry=-1&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&search=Search&currentSortSettings=",
                callback=self.parse_pages,
            )

    # ----- PARTIE SCRAPING ----- (si notre csv est pas à jour)
    async def parse_pages(self, response):
        """Parse les pages de transactions du registre EU ETS.

        Args:
            response (scrapy.Response): La réponse HTTP de la page à parser.

        Yields:
            scrapy.Request: Une demande de suivi pour chaque page de transactions.
        """
        pages = int(
            response.xpath("//input[@name='resultList.lastPageNumber']/@value").get()
        )
        for page in range(2, pages + 2):
            url = f"https://ec.europa.eu/clima/ets/transaction.do?languageCode=fr&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=-1&destinationRegistry=-1&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&currentSortSettings=&backList=%3CBack&resultList.currentPageNumber={page}"
            yield response.follow(url, callback=self.parse)

    async def parse(self, response):
        """Extracts data from a table in the response.

        Args:
        response (scrapy.http.Response): The response object containing the HTML page to parse.

        Yields:
        dict: A dictionary containing the extracted data from each row in the table. The keys in the dictionary
        represent the different columns in the table, such as 'Transaction_ID', 'Transaction_Type', etc.
        """
        total_pages = response.xpath(
            "//input[@name='resultList.lastPageNumber']/@value"
        ).get()
        page = response.xpath(
            "//input[@name='resultList.currentPageNumber']/@value"
        ).get()
        print(f"page {page} sur {total_pages}")

        if total_pages is None:
            logging.warning(f"Page content is None for {response.url}, retrying...")
            yield response.follow(response.url, callback=self.parse)
        else:
            for row in response.css(
                "table#tblTransactionSearchResult tr:nth-child(n+3)"
            ):  # on commande a n+3 car les infos sont pas pertinentes avant ça
                dico_data = {
                    "Transaction_ID": row.css("td:nth-child(1) span::text")
                    .get(default="")
                    .strip(),
                    "Transaction_Type": row.css("td:nth-child(2) span::text")
                    .get(default="")
                    .strip(),
                    "Transaction_Date": row.css("td:nth-child(3) span::text")
                    .get(default="")
                    .strip(),
                    "Transaction_Status": row.css("td:nth-child(4) span::text")
                    .get(default="")
                    .strip(),
                    "Transferring_Registry": row.css("td:nth-child(5) span::text")
                    .get(default="")
                    .strip(),
                    "Transferring_Account_Type": row.css("td:nth-child(6) span::text")
                    .get(default="")
                    .strip(),
                    "Transferring_Account_Name": row.css("td:nth-child(7) span::text")
                    .get(default="")
                    .strip(),
                    "Transferring_Account_Identifier": row.css(
                        "td:nth-child(8) span::text"
                    )
                    .get(default="")
                    .strip(),
                    "Transferring_Account_Holder": row.css("td:nth-child(9) span::text")
                    .get(default="")
                    .strip(),
                    "Acquiring_Registry": row.css("td:nth-child(10) span::text")
                    .get(default="")
                    .strip(),
                    "Acquiring_Account_Type": row.css("td:nth-child(11) span::text")
                    .get(default="")
                    .strip(),
                    "Acquiring_Account_Name": row.css("td:nth-child(12) span::text")
                    .get(default="")
                    .strip(),
                    "Acquiring_Account_Identifier": row.css(
                        "td:nth-child(13) span::text"
                    )
                    .get(default="")
                    .strip(),
                    "Acquiring_Account_Holder": row.css("td:nth-child(14) span::text")
                    .get(default="")
                    .strip(),
                    "Nb_of_Units": row.css("td:nth-child(15) span::text")
                    .get(default="")
                    .strip(),
                }
                yield dico_data
