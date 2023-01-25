# Europa_Scraping
Ce repository sert à mettre en commun notre code pour le projet science_po pour le projetS2

Le projet est de scraper des données sur le site : https://ec.europa.eu/clima/ets/welcome.do?languageCode=fr

- Language utilisé : Python

- techno utilisé : Scrapy, asyncio

- méthode de stockage des fichiers : .csv


On va revenir en détail sur les précédents points :

- Language utilisé : Python car c'est le language avec lequel on a le plus de facilité et sur lequel il existe énormement de ressources et d'aides disponibles en cas de besoin.

- techno utilié : Pour ce qui est de la techno utilisé on avait d'abord pensé a BeautifulSoup, à Selenium et enfin à Scrapy.
Une premiere version d'un scraper avait été fait avec BeautifulSoup, et cet outil semblait plutôt prometteur même si les requêtes http pouvait être plutôt lentes, surtout lorsqu'elles depassaient un certains nombres, le programme devenait très lent. 
  Pour ce qui est du Selenium le choix à été très rapidement fait. On s'est aperçu que c'était plus un outil d'automatisation que de scraping, et nous ne pouvions pas nous baser sur ça pour scraper des centaines/miliers d'url différents.
  Scrapy est venu en dernier et s'est demarqué par sa rapidité, notamment grace aux  requête asynchrone qui ont permis de nous faire gagner beaucoup de temps, même si cette technologie était nouvel pour nous.

- méthode de stockage : Le choix est encore a faire, ce n'est pas une priorité pour l'instant. Mais de ce qu'on a pu voir il est préférable de choisir un type de stockage tel que .csv ou .xlsx puisque l'usage de ces données est d'être utilisé par des data scientists ou des economistes, et qu'un type de données comme .json et .xml supportant des données hiérarchisées pouvait être trop complexe


