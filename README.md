# Europa_Scraping
Ce repository sert à mettre en commun notre code pour le projet science_po pour le projetS2

Le projet est de scraper des données sur le site : https://ec.europa.eu/clima/ets/welcome.do?languageCode=fr

- Language utilisé : Python

- techno utilisé : Scrapy, asyncio

- méthode de stockage des fichiers : .json ou .Xml (ou autre type de fichier permettant de saugareré des données suivant une hiérarchie)


On va revenir en détail sur les précédents points :

- Language utilisé : Python car c'est le language avec lequel on a le plus de facilité et sur lequel il existe énormement de ressources et d'aides disponibles en cas de besoin.

- techno utilié : Pour ce qui est de la techno utilisé on avait d'abord pensé a BeautifulSoup, à Selenium et enfin à Scrapy.
Une premiere version d'un scraper avait été fait avec BeautifulSoup, et cet outil semblait plutôt prometteur même si les requêtes http pouvait être plutôt lentes, surtout lorsqu'elles depassaient un certains nombres, le programme devenait très lent. 
  Pour ce qui est du Selenium le choix à été très rapidement fait. On s'est aperçu que c'était plus un outil d'automatisation que de scraping, et nous ne pouvions pas nous baser sur ça pour scraper des centaines/miliers d'url différents.
  Scrapy est venu en dernier et s'est demarqué par sa rapidité, notamment grace aux  requête asynchrone qui ont permis de nous faire gagner beaucoup de temps, même si cette technologie était nouvel pour nous.

- méthode de stockage : Le choix est encore a faire, ce n'est pas une priorité pour l'instant. Mais de ce qu'on a pu voir il est préférable de choisir un type de stockage supportant les données "hiérarchisé" comme json ou xml plutôt que .csv qui renvoi des erreurs dans ces cas là, même si par consequent les fichiers sauvegardé seraient plus lourd.
  De plus cette méthode de stockage (json et xml) est très peu user friendly, mais puisque nous voulons par la suite visualiser les données collectés sur un dashboard, ce n'est pas un problème de passer par ce type de fichier.


