I. Manuel

L'exécutable s'appelle de la manière suivante :

$python3 main.py -f <fichiers de données> -c chunk(s) analysé(s) -i ID de
monitors

-f : Les fichiers de trace du flux.
	Le premier fichier est le point de départ.
	Le DEUXIÈME fichier est le point d'arrivée.
	La suite constitue les traces intermédiaires dans l'ordre du départ
	vers l'arrivée.

-c : Le(s) chunk(s) ciblés:
	Le PREMIER chunk est le seul dont TOUS les paquets seront inclus dans
	les statistiques.
	Les chunks suivants ne sont utilisés que pour compléter les
	statistiques des paquets précédemment chargés.

-i : (optionnel) Les identifiants des points de capture dans l'ordre du début à
	la fin. Nécessaire à la génération d'un nom par segment.

Fonctionnement du code


II. Code

L'extraction des statistiques se déroule en 2 étapes :
	1. Lecture des fichiers dans l'ordre imposé par le flux et génération
	d'un objet 'Tab', contenant les informations sur tous les paquets, agrégées
	2. Génération d'un objet 'GlobalStats' ne contenant plus que les
	statistiques sur chaque flux.

Workflow du code :

MA4.dat		MA3.dat	   MA5.dat
      \         |        /
	\       |      /
	chunks_loader.py
	     |
	     |
	OBJET : Tab
	     |
	stats.py
	     |
	p_analyzer.py
	     |
	OBJET GlobalStats


Présentation des fichiers :
	- demo.sh :
		contient une commande d'exemple d'utilisation
	- tests.py :
		contient tous les tests du code. 
		Pour effectuer les tests :
			$python3 tests.py
		Doit afficher un message du type :
			.............
			----------------------------------------------------------------------
			Ran 13 tests in 0.021s

			OK
		En cas d'erreur affiche :
			.....F.......
			----------------------------------------------------------------------
			Ran 13 tests in 0.020s

			FAILED (failures=1)
					 ^
					 Nombre de test échoués
	- chunks_loader.py:
		contient les fonctions/objects nécessaires au chargement d'un
		fichier	dans l'objet Tab.
		Exemple :
          		  self.full_tab = Tab()
          		  self.full_tab.bounds = [5.0,20.0]
          		  self.full_tab.chunk_id = "0"
          		  self.f_data ={
          		          "mpls:22":
          		          OrderedDict([
          		           ["8",Packet(2.2,12.2,[11.2],10)],
          		           ["6",Packet(3.3,13.3,[12.3],20)],
          		           ["4",Packet(4.4,None,None,30)],
          		           ["2",Packet(4.9,14.9,[13.9],40)]
          		                  ])
          		              }
          		  self.full_tab.data = self.f_data

	- stats.py :
		contient tous les objets permettant de stocker les
		statistiques. Chaque statistique a son objet :
		JitterStats, BwStats, DelayStats...
		Ils sont regroupés en FlowStats pour un flux donné.
		Les FlowStats sont regroupés pour un flux dans des SegStats.
		Enfin, toutes les SegStats sont regroupées au sein de l'objet
		GlobalStats.

	- p_analyzer.py :
		Permet de passer de l'objet Tab à l'objet GlobalStats. Contient
		la métthode add_packet(self,packet) qui, appelée dans une boucle,
		effectue le traitement de chaque paquet.

	- main.py :
		Le main du fichier.
	- mcorr_logger.py :
		Contient de quoi initialiser un logger pout l'application
	- aggregator.py :
		Gestionnaire des chunks chargés/à charger/à effacer


