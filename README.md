# Europa_Scraping


## A propos du projet

Ce repository sert à mettre en commun notre code pour le projet science_po pour le projetS2

Le projet est de scraper des données sur le site : https://ec.europa.eu/clima/ets/welcome.do?languageCode=fr


### language utilisé

Python - Projet Scrapy


<br><br>
<!-- GETTING STARTED -->
## Pour commencer

1.Cloner le dépôt du projet : git clone https://github.com/votre-utilisateur/votre-projet.git

2.Naviguer dans le répertoire du projet : cd votre-projet

3.Installer les dépendances : pip install -r requirements.txt


### Pré-requis

- pip install scrapy 
- pip install asyncio (pas sûre d'être utile)
- pip install pandas
- pip install logging
- pip install datetime

### Installation

1.Cloner le dépôt du projet : git clone https://github.com/MunznerLouis/Europa_Scraping
2.Naviguer dans le répertoire du projet : cd votre-projet
3.Installer les dépendances : pip install -r requirements.txt



<br><br>
<!-- USAGE EXAMPLES -->
## Utilisation

Pour lancer une Spider contenu dans le dossier 'spiders' du projet : 

1. Avec un terminale, naviguer jusqu'au dossier où se trouve les spiders
exemple :  ~/Desktop\Projet sciencepo\Europa_Scraping\scrapy_scraper\scrapy_scraper\spiders>

2. lancer la commande suivante : 
scrapy runspdier [fichier spider qu'on veut lancer] exemple:
scrapy runspider europa_spider.py
ça aura pour effet de scraper le site, mais les données seront sauvegardé nullpart
pour sauvegarder les données quelque part, suivre l'étape 3 : 

3. lancer la commande suivante : 
scrapy runspider [fichier de la classe spider] -O [nom de fichier avec son extension]
le 'o' peut etre en majuscule si on veut Override le fichier du même nom 
exemple
scrapy runspider europa_spider.py -O ../../data.csv

PS : l'étape . remplace l'étape 2 dans le cas ou on veut sauvegarder les données scrapées



<br><br>
<!-- ROADMAP -->
## Roadmap

- [ ] Un dashboard plus complet avec une relation avec d'autre database.



<br><br>
<!-- CONTRIBUTING -->
## Contribution
(pas encore publique)

1. Forker le dépôt

2. Créer une branche pour la fonctionnalité ou le correctif que vous souhaitez ajouter : git checkout -b ma-branche
 
3. Effectuer les modifications nécessaires et les valider : git commit -m "Description de la modification"

4. Pousser les modifications vers votre fork : git push origin ma-branche

5. Créer une pull request pour proposer les modifications au projet d'origine.



<br><br>
<!-- LICENSE -->
## License



<br><br>
<!-- CONTACT -->
## Contact

- Münzner Louis - munzner.louis@gmail.com 

- Brise Quentin - brisequent@cy-tech.fr 

- Zeddam Hatem - zeddamhate@cy-tech.fr  

- Noyes Enzo - noyesenzo@cy-tech.fr  

Project Link: [https://github.com/MunznerLouis/Europa_Scraping](https://github.com/MunznerLouis/Europa_Scraping)


