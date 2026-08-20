################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.13 – LLM appelable en local                                                #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import json
import requests

# 1 -- Classe permettant d'appeler un petit LLM --------------------------------


class LLMClient:
    """
    Client générique pour communiquer avec un LLM local via Ollama.

    Exemple :
        llm = LLMClient(model="qwen3:4b")

        llm.set_data({
            "voyages": voyages
        })

        llm.set_prompt(
            "Décris le profil de voyageur à partir des données."
        )

        resultat = llm.generate()
    """

    def __init__(
        self,
        model="qwen3:4b",
        url="http://localhost:11434/api/generate",
        timeout=300,
        temperature=0.7,
        contexte=8192,
    ):
        self.model = model
        self.url = url
        self.timeout = timeout
        self.langue = "français"
        self.temperature = temperature
        self.contexte = contexte

        self.data = None
        self.prompt = None

    # --------------------------------------------------
    # Configuration
    # --------------------------------------------------

    def set_data(self, data):
        """
        Définit les données envoyées au modèle.

        Peut être :
        - dict
        - liste
        - texte
        """
        self.data = data

    def set_prompt(self, prompt):
        """
        Définit l'instruction donnée au modèle.
        """
        self.prompt = prompt

    def set_model(self, model):
        """
        Change le modèle utilisé.
        """
        self.model = model

    def set_langue(self, langue):
        """
        Change la langue utilisée.
        """
        self.langue = langue

    # --------------------------------------------------
    # Génération
    # --------------------------------------------------

    def creer_prompt_profil(self):

        contenu = self.prompt

        # Ajout de la langue
        contenu += (
            "\n\n"
            f"Langue de production du texte : {self.langue}. "
            "Utilise l'anglais si tu ne connais pas celle-ci."
        )

        if self.data is not None:
            contenu += (
                "\n\n"
                "Voici les données du voyageur à analyser :\n"
                "----- DÉBUT DES DONNÉES -----\n"
                f"{json.dumps(self.data, ensure_ascii=False, indent=2)}\n"
                "----- FIN DES DONNÉES -----\n\n"
                "Base ton analyse du profil du voyageur uniquement sur ces données."
            )

        self.prompt = contenu

    def generate(self, reflexion=False):
        """
        Génère une réponse du LLM.

        Retourne :
            str : texte généré

        Lève :
            RuntimeError en cas d'erreur.
        """

        if self.prompt is None:
            raise RuntimeError("Aucun prompt défini.")

        payload = {
            "model": self.model,
            "prompt": self.prompt,
            "stream": False,
            "think": reflexion,
            "options": {
                "num_ctx": self.contexte,
                "temperature": self.temperature,
            },
        }

        try:
            response = requests.post(self.url, json=payload, timeout=self.timeout)

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Impossible de contacter Ollama. " "Vérifiez qu'il est lancé."
            )

        except requests.exceptions.Timeout:
            raise RuntimeError("Le modèle a mis trop de temps à répondre.")

        if response.status_code != 200:
            raise RuntimeError(f"Erreur Ollama : {response.text}")

        resultat = response.json()

        return resultat.get("response", "")


# 2 -- Fonction de tests des disponibilités d'Ollama ---------------------------


def tester_ollama(url="http://localhost:11434"):
    """
    Teste la présence d'Ollama et récupère les modèles disponibles.

    Retourne :
        {
            "disponible": True/False,
            "modeles": [...],
            "erreur": "..."
        }
    """

    resultat = {"disponible": False, "modeles": [], "erreur": None}

    try:
        # Test du serveur Ollama
        reponse = requests.get(f"{url}/api/tags", timeout=3)

        if reponse.status_code != 200:
            resultat["erreur"] = f"Ollama répond avec le code {reponse.status_code}"
            return resultat

        donnees = reponse.json()

        resultat["disponible"] = True

        # Extraction des modèles
        resultat["modeles"] = [modele["name"] for modele in donnees.get("models", [])]

    except requests.exceptions.ConnectionError:
        resultat["erreur"] = "Ollama n'est pas lancé"

    except requests.exceptions.Timeout:
        resultat["erreur"] = "Ollama ne répond pas"

    except Exception as e:
        resultat["erreur"] = str(e)

    return resultat
