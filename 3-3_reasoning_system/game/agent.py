# Permet d'inferer qui est le meurtrier, quand, comment, où il a tué.
from aima.logic import *
import nltk
import json
import os
import random


class Agent:

    def __init__(self, board):
        self.board = board
        
        self.weapons = list(board.weapons)
        self.rooms = list(board.rooms)
        self.persons = list(board.suspects)
        
        # Liste de clauses (faits) qui seront stockées dans la base de connaissance.
        self.clauses = []        
        
        self.base_clauses()
        self.initialize_KB()
        self.inference_rules()
        
        # Charger les faits initiaux depuis initial_facts.json
        self.load_initial_facts()
        
        # Variables pour stocker la personne et l'arme de la pièce actuelle
        self.current_room_person = None
        self.current_room_weapon = None
        
        # Base de connaissances (First-order logic - FOL)
        self.crime_kb = FolKB(self.clauses)

    # Déclaration dans la logique du premier ordre
    def base_clauses(self):
        # Le paramètre est une arme
        self.arme_clause = 'Arme({})'
        
        # Le paramètre est une pièce
        self.piece_clause = 'Piece({})'
        
        # Le paramètre est une persone
        self.personne_clause = 'Personne({})'

        # paramètre 1 : arme; paramètre 2 : pièce
        # p.ex.: Le couteau se trouve dans la cuisine
        self.weapon_room_clause = 'Arme_Piece({},{})'

        # paramètre 1 : personne; paramètre 2 : pièce; paramètre 3 : heure
        # p.ex.: Mustart était dans la cuisine à 11h00
        self.person_room_hour_clause = 'Personne_Piece_Heure({}, {}, {})'

        # paramètre 1 : personne; paramètre 2 : piece
        # p.ex.: Mustard se trouve dans la cuisine
        self.person_room_clause = 'Personne_Piece({}, {})'

        # paramète 1 : personne
        # p. ex.: Mustard est mort
        self.dead_clause = 'EstMort({})'
        
        # paramète 1 : personne
        # p. ex.: Mustard est vivant
        self.alive_clause = 'EstVivant({})'

        # paramètre 1 : personne
        # p. ex.: Mustard est la victime
        self.victim_clause = 'Victime({})'

        # paramètre 1 : piece; paramètre 2 : piece
        self.room_different_clause = 'PieceDifferente({},{})'

        # paramètre 1 : piece; paramètre 2 : piece
        self.weapon_different_clause = 'ArmeDifferente({},{})'

        # paramètre 1 : personne; paramètre 2 : personne
        self.person_different_clause = 'PersonneDifferente({},{})'

        # paramètre 1 : heure
        self.crime_hour_clause = 'HeureCrime({})'

        # paramètre 1 : heure
        self.crime_hour_plus_one_clause = 'UneHeureApresCrime({})'

        # paramètre 1 : personne
        # p. ex.: Mustard a des marques au cou
        self.body_mark_clause = 'MarqueCou({})'

        # paramètre 1 : personne
        self.split_skull_clause = 'CraneFendu({})'

        # paramètre 1 : personne
        self.chest_wound_clause = 'PlaiePoitrine({})'

        # paramètre 1 : personne
        self.cut_leg_clause = 'JambeCoupee({})'

        # paramètre 1 : personne
        self.broken_arm_clause = 'BrasCasse({})'

        # paramètre 1 : personne
        self.chest_hole_clause = 'TrouPoitrine({})'

        # paramètre 1 : personne
        self.intoxication_clause = 'Intoxication({})'

        self.weapon_room_hour_clause = 'Arme_Piece_Heure({}, {}, {})'

    def initialize_KB(self):
        # Clause pour differencier les pièces
        for i in range(len(self.rooms)):
            for j in range(len(self.rooms)):
                if i != j:
                    # Le bureau est different de la cuisine = PieceDifferente(Bureau, Cuisine)
                    self.clauses.append(expr(self.room_different_clause.format(self.rooms[i], self.rooms[j])))

        # Clause pour differencier les armes
        for i in range(len(self.weapons)):
            for j in range(len(self.weapons)):
                if i != j:
                    # Le couteau est different de la corde = ArmeDifferente(Couteau, Corde)
                    self.clauses.append(expr(self.weapon_different_clause.format(self.weapons[i], self.weapons[j])))

        #Clause pour differencier les personnes
        for i in range(len(self.persons)):
            for j in range(len(self.persons)):
                if i != j:
                    # Mustard est different de Scarlett = PersonneDifferente(Mustard, Scarlett)
                    self.clauses.append(expr(self.person_different_clause.format(self.persons[i], self.persons[j])))

        # Initialiser KB sur Armes, Pieces, Personnes
        for weapon in self.weapons:
            # Le couteau est une arme = Arme(Couteau)
            self.clauses.append(expr(self.arme_clause.format(weapon)))

        for room in self.rooms:
            # La cuisine est une pièce = Piece(Cuisine)
            self.clauses.append(expr(self.piece_clause.format(room)))

        for person in self.persons:
            # Mustar est une personne = Personne(Mustard)
            self.clauses.append(expr(self.personne_clause.format(person)))
    
    # Expressions dans la logique du premier ordre permettant de déduire les caractéristiques du meurtre
    def inference_rules(self):
        # Determine la piece du crime
        self.clauses.append(expr('EstMort(x) & Personne_Piece(x, y) ==> PieceCrime(y)'))

        # Determiner l'arme potentielle du crime
        self.clauses.append(expr('PlaiePoitrine(x) & CauseBlessure(a, PlaiePoitrine) ==> ArmePossible(a)'))
        self.clauses.append(expr('CraneFendu(x) & CauseBlessure(a, CraneFendu) ==> ArmePossible(a)'))
        self.clauses.append(expr('MarqueCou(x) & CauseBlessure(a, MarqueCou) ==> ArmePossible(a)'))


        #Determiner arme crime ()
        self.clauses.append(expr('ArmePossible(a) & PieceCrime(r) & HeureCrime(h) & Arme_Piece_Heure(a, r, h) ==> ArmeCrime(a)'))


        # Si la personne est morte alors elle est la victime et ce n'est pas un suicide
        self.clauses.append(expr('EstMort(x) ==> Victime(x)'))

        # Si la personne est morte alors elle est innocente et ce n'est pas un suicide
        self.clauses.append(expr('EstMort(x) ==> Innocent(x)'))

        # Personne suspect (Prend en considération que le meutrier n'est pas rester dans la même pièce que la victime une heure après le crime)
        self.clauses.append(expr('EstVivant(p) & PieceCrime(r1) & UneHeureApresCrime(h1) & Personne_Piece_Heure(p, r2, h1) & ArmeCrime(a) & Arme_Piece(a, r2) & PieceDifferente(r1, r2) ==> Suspect(p)'))

        #Personnes innocente
        self.clauses.append(expr('Suspect(x) & EstVivant(y) & PersonneDifferente(x,y) ==> Innocent(y)'))

    # Ajouter des clauses, c'est-à-dire des faits, à la base de connaissances
    def add_clause(self, clause_string):
        self.crime_kb.tell(expr(clause_string))

    # Demander à la base de connaissances qui est la victime
    def get_victim(self):
        result = self.crime_kb.ask(expr('Victime(x)'))
        if not result:
            return False
        else:
            return result[x]
        
    # Demander à la base de connaissances la pièce du meurtre
    def get_crime_room(self):
        result = self.crime_kb.ask(expr('PieceCrime(x)'))
        if not result:
            return False
        else:
            return result[x]

    # Demander à la base de connaissances l'arme du meurtrier
    def get_crime_weapon(self):
        result = self.crime_kb.ask(expr('ArmeCrime(x)'))
        if not result:
            return result
        else:
            return result[x]

    # Demander à la base de connaissances l'heure du meurtre
    def get_crime_hour(self):
        result = self.crime_kb.ask(expr('HeureCrime(x)'))
        if not result:
            return result
        else:
            return result[x]

    def get_crime_hour_plus_one(self):
        result = self.crime_kb.ask(expr('UneHeureApresCrime(x)'))
        if not result:
            return result
        else:
            return result[x]
    
    # Demander à la base de connaissances le suspect
    def get_suspect(self):
        result = self.crime_kb.ask(expr('Suspect(x)'))
        if not result:
            return result
        else:
            return result[x]

    # Demander à la base de connaissances la liste d'innocents
    def get_innocent(self):
        result = list(fol_bc_ask(self.crime_kb, expr('Innocent(x)')))
        res = []

        for elt in result:
            if not res.__contains__(elt[x]):
                res.append(elt[x])
        return res
    

    def results_as_string(self, results):
        res = ''
        for result in results:
            # synrep = syntactic representation
            # semrep = semantic representation
            for (synrep, semrep) in result:            
                res += str(semrep)
        return res
    
    
    def to_fol(self, fact, grammar):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        grammar_path = os.path.join(current_dir, '..', grammar if grammar.startswith('grammars/') else f'grammars/{grammar}')
        with open(grammar_path, 'r', encoding='utf-8') as f:
            grammar_obj = nltk.grammar.FeatureGrammar.fromstring(f.read())
        sent = self.results_as_string(nltk.interpret_sents(fact, grammar_obj))
        return sent
    
    def begin_investigation(self):
        """Commencer l'enquête dans une pièce aléatoire et visiter les pièces jusqu'à trouver le corps"""
        print("\n=== DÉBUT DE L'ENQUÊTE ===\n")
        print("⚠️  L'enquête continue de pièce en pièce jusqu'à trouver le corps!\n")
        
        # Commencer dans une pièce aléatoire
        visited_rooms = set()
        victim_found = False
        
        # Choisir une première pièce aléatoire
        current_room = random.choice(self.board.rooms)
        visited_rooms.add(current_room)
        
        print(f"📍 Vous commencez l'enquête dans : {current_room}\n")
        print(f"Chargement des faits du {current_room}...\n")
        self.add_room_facts(current_room)
        
        # Poser les questions après avoir chargé les faits de la pièce
        self.ask_investigation_questions(current_room)
        
        # Vérifier si le corps est dans cette pièce
        if self._check_victim_in_room(current_room):
            print(f"\n💀 VOUS AVEZ TROUVÉ LE CORPS DANS : {current_room}")
            victim_found = True
        
        # Boucle d'enquête : continuer tant que le corps n'est pas trouvé
        while not victim_found:
            # Afficher les pièces non visitées
            unvisited = [r for r in self.board.rooms if r not in visited_rooms]
            
            if not unvisited:
                print("\n✓ Vous avez visité toutes les pièces!")
                break
            
            response = input(f"\nPièces non visitées : {', '.join(unvisited)}\nQuelle pièce visitez-vous ? (ou 'quit' pour quitter) : ").strip()
            
            if response.lower() == 'quit':
                print("✓ Enquête terminée.")
                break
            
            # Chercher la pièce (insensible à la casse)
            matching_room = None
            for room in self.board.rooms:
                if room.lower() == response.lower():
                    matching_room = room
                    break
            
            if matching_room:
                current_room = matching_room
                visited_rooms.add(current_room)
                print(f"\n📍 Vous êtes maintenant dans : {current_room}")
                print(f"Chargement des faits du {current_room}...\n")
                self.add_room_facts(current_room)
                
                # Poser les questions après avoir chargé les faits de la pièce
                self.ask_investigation_questions(current_room)
                
                # Vérifier si le corps est dans cette pièce
                if self._check_victim_in_room(current_room):
                    print(f"\n💀 VOUS AVEZ TROUVÉ LE CORPS DANS : {current_room}")
                    victim_found = True
            else:
                print(f"❌ Pièce inconnue. Les pièces disponibles sont : {', '.join(self.board.rooms)}")
    
    def _check_victim_in_room(self, room):
        """Vérifier si le corps est dans la pièce en cherchant 'EstMort' dans les clauses"""
        for clause in self.clauses:
            clause_str = str(clause).lower()
            if 'estmort' in clause_str and room.lower() in clause_str:
                return True
        return False
        
        
    def load_initial_facts(self):
        """Charger les faits initiaux depuis initial_facts.json"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        initial_facts_path = os.path.join(current_dir, '..', 'initial_facts.json')
        
        try:
            with open(initial_facts_path, 'r', encoding='utf-8') as f:
                initial_facts = json.load(f)
            
            for fact_obj in initial_facts:
                if isinstance(fact_obj, dict) and 'fact' in fact_obj and 'grammar' in fact_obj:
                    try:
                        fol_expr = self.to_fol([fact_obj['fact']], fact_obj['grammar'])
                        if fol_expr.strip():
                            self.clauses.append(expr(fol_expr))
                    except:
                        pass
            
            self.crime_kb = FolKB(self.clauses)
        except:
            pass
    
    def add_room_facts(self, room_name):
        """Charger et afficher les faits d'une pièce depuis room_facts.json"""
        # Trouver le chemin du fichier room_facts.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        room_facts_path = os.path.join(current_dir, '..', 'room_facts.json')
        
        # Réinitialiser les personnes et armes pour cette pièce
        self.current_room_person = None
        self.current_room_weapon = None
        
        try:
            with open(room_facts_path, 'r', encoding='utf-8') as f:
                room_facts = json.load(f)
            
            # Chercher les faits de la pièce
            room_key = room_name.lower()
            if room_key in room_facts:
                facts = room_facts[room_key]
                
                print(f"\n🏠 FAITS DE LA PIÈCE: {room_name.upper()}")
                print("=" * 50)
                
                facts_added = []
                
                # Ajouter person_location
                if 'person_location' in facts:
                    fact_text = facts['person_location']
                    print(f"  👤 {fact_text}")
                    # Extraire le nom de la personne
                    parts = fact_text.split(' est dans ')
                    if len(parts) == 2:
                        person = parts[0].strip()
                        self.current_room_person = person  # Stocker la personne
                        room = parts[1].strip().replace('le ', '').replace('la ', '').capitalize()
                        logic_fact = expr(self.person_room_clause.format(person, room))
                        self.clauses.append(logic_fact)
                        facts_added.append(logic_fact)
                
                # Ajouter weapon_location
                if 'weapon_location' in facts:
                    fact_text = facts['weapon_location']
                    print(f"  🔪 {fact_text}")
                    # Extraire le nom de l'arme
                    parts = fact_text.split(' est dans ')
                    if len(parts) == 2:
                        weapon = parts[0].replace('Le ', '').replace('La ', '').strip()
                        self.current_room_weapon = weapon  # Stocker l'arme
                        room = parts[1].strip().replace('le ', '').replace('la ', '').capitalize()
                        logic_fact = expr(self.weapon_room_clause.format(weapon, room))
                        self.clauses.append(logic_fact)
                        facts_added.append(logic_fact)
                
                # Ajouter crime_scene si disponible
                if 'crime_scene' in facts:
                    fact_text = facts['crime_scene']
                    print(f"  ⚠️ {fact_text}")
                    facts_added.append(fact_text)
                
                # Mettre à jour la KB
                self.crime_kb = FolKB(self.clauses)
                print(f"\n✓ {len(facts_added)} fait(s) ajouté(s) à la base de connaissances")
                print("=" * 50 + "\n")
            else:
                print(f"⚠️ Pièce '{room_name}' non trouvée dans room_facts.json")
        
        except FileNotFoundError:
            print(f"⚠️ Attention: {room_facts_path} non trouvé")
        except json.JSONDecodeError:
            print(f"⚠️ Erreur: le fichier {room_facts_path} n'est pas un JSON valide")
    
    def ask_investigation_questions(self, room_name):
        """Poser 2 questions dynamiques sur la pièce visitée basées sur la personne et l'arme trouvées"""
        # Générer les questions dynamiquement basées sur la personne et l'arme
        questions = []
        
        if self.current_room_person:
            questions.append({
                'question': f"Où se trouvait {self.current_room_person} à 17h ?",
                'grammar': 'grammars/personne_piece_heure.fcfg'
            })
        
        if self.current_room_weapon:
            questions.append({
                'question': f"Où était {self.current_room_weapon} à 16h ?",
                'grammar': 'grammars/arme_piece_heure.fcfg'
            })
        
        if questions:
            print("\n" + "=" * 50)
            print(f"❓ QUESTIONS POUR {room_name.upper()}")
            print("=" * 50)
            
            for i, q in enumerate(questions, 1):
                question = q['question']
                grammar = q['grammar']
                
                print(f"\n# {i} Question : {question}")
                response = input("-> Réponse : ").strip()
                
                if response:
                    # Convertir la réponse en expression logique
                    try:
                        fol_expr = self.to_fol([response], grammar)
                        if fol_expr.strip():
                            self.clauses.append(expr(fol_expr))
                            self.crime_kb = FolKB(self.clauses)
                            print(f"   ✓ Fait ajouté")
                    except Exception as e:
                        print(f"   ⚠️ Erreur lors de la conversion: {str(e)}")
            
            print("\n" + "=" * 50 + "\n")