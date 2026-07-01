import os
import time
import random
from playwright.sync_api import sync_playwright

FICHIER_ORDRES = "whatsapp_ordres.txt"

def frappe_humaine_avancee(page, selecteur, texte):
    """
    Amélioration 2 : Simule une frappe humaine réaliste.
    - Vitesse variable entre chaque lettre.
    - Pauses plus longues sur la ponctuation (virgules, points).
    - Micro-pauses aléatoires (simulation de réflexion).
    """
    page.click(selecteur)
    
    for caractere in texte:
        page.type(selecteur, caractere)
        
        # Rythme de base : entre 40ms et 150ms par lettre
        delai = random.uniform(0.04, 0.15)
        
        # Si c'est une fin de phrase ou une pause, l'humain s'arrête un peu plus
        if caractere in [".", ",", "!", "?", ";"]:
            delai += random.uniform(0.3, 0.6)
            
        # 5% de chance que l'humain fasse une micro-pause de réflexion au milieu d'un mot
        if random.random() < 0.05:
            delai += random.uniform(0.4, 0.9)
            
        time.sleep(delai)

def executer_saisie(nom_contact, texte_a_saisir):
    profile_dir = os.path.join(os.getcwd(), "whatsapp_session")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=True # Totalement invisible
        )
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")
        
        try:
            print(f"[WhatsApp] Recherche de : {nom_contact}...")
            search_box = '[data-testid="chat-list-search"]'
            page.wait_for_selector(search_box, timeout=20000)
            page.fill(search_box, nom_contact)
            time.sleep(1.5) # Temps de filtrage visuel de WhatsApp
            page.keyboard.press("Enter")
            
            print("[WhatsApp] Discussion ouverte. Début de la saisie réaliste...")
            input_box = '[data-testid="conversation-compose-box-input"]'
            page.wait_for_selector(input_box, timeout=10000)
            
            # Utilisation de la frappe humaine avancée
            frappe_humaine_avancee(page, input_box, texte_a_saisir)
            
            # On laisse le statut "typing..." actif 3 secondes de plus après la fin pour faire naturel
            time.sleep(3)
            print("[WhatsApp] Saisie terminée avec succès !")
            
        except Exception as e:
            print(f"[Erreur] Impossible d'exécuter l'ordre : {e}")
        finally:
            browser.close()

def surveiller_fichier():
    """
    Amélioration 3 : Surveille le fichier texte pour exécuter les ordres à la demande.
    """
    # Création du fichier s'il n'existe pas
    if not os.path.exists(FICHIER_ORDRES):
        with open(FICHIER_ORDRES, "w", encoding="utf-8") as f:
            f.write("# Format: Nom du Contact | Votre message ici\n")
            f.write("# Exemple: Jean Dupont | Salut, comment ça va ?\n")
    
    print(f"[*] Agent en arrière-plan actif. Modifiez le fichier '{FICHIER_ORDRES}' pour déclencher une saisie.")
    print("[*] Pour arrêter l'agent, faites Ctrl+C dans ce terminal.")

    while True:
        try:
            with open(FICHIER_ORDRES, "r", encoding="utf-8") as f:
                lignes = f.readlines()
            
            # On cherche une ligne qui ne commence pas par un commentaire '#' et qui n'est pas vide
            ordre_trouve = None
            for ligne in lignes:
                if ligne.strip() and not ligne.strip().startswith("#"):
                    ordre_trouve = ligne.strip()
                    break
            
            if ordre_trouve and "|" in ordre_trouve:
                # Extraction du contact et du texte
                contact, message = ordre_trouve.split("|", 1)
                contact = contact.strip()
                message = message.strip()
                
                print(f"\n[!] Nouvel ordre détecté pour '{contact}'")
                
                # Exécution de l'automatisation WhatsApp
                executer_saisie(contact, message)
                
                # On vide le fichier d'ordre pour ne pas le répéter en boucle
                with open(FICHIER_ORDRES, "w", encoding="utf-8") as f:
                    f.write("# Ordre exécuté. En attente du prochain...\n")
                    
            time.sleep(2) # Vérifie le fichier toutes les 2 secondes
            
        except KeyboardInterrupt:
            print("\n[*] Arrêt de l'agent d'arrière-plan.")
            break
        except Exception as e:
            print(f"[Erreur boucle] {e}")
            time.sleep(5)

if __name__ == "__main__":
    # RAPPEL : Lors du TOUT PREMIER lancement, assurez-vous d'avoir déjà scanné le QR code.
    # Si ce n'est pas fait, changez temporairement 'headless=True' par 'headless=False' à la ligne 34.
    surveiller_fichier()
