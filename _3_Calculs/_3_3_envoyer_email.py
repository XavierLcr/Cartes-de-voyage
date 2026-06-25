################################################################################
# Projet de cartes de voyage                                                   #
# _3_Calculs/                                                                  #
# 3.3 – Script permettant l'envoi d'un e-mail                                  #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from clefs_et_mots_de_passe import mdp_google


# 1 -- Fonction d'envoi d'un e-mail --------------------------------------------


def envoyer_email_avec_piece_jointe_smtp(
    email_destinataire: str,
    sujet: str,
    contenu: str,
    chemin_fichier: str | None = None,
    nom_fichier_destinataire: str | None = None,
):
    """
    Envoie un e-mail avec une pièce jointe via SMTP (ex: Gmail).

    Args:
        email_destinataire (str): E-mail du destinataire.
        sujet (str): Sujet de l'e-mail.
        contenu (str): Contenu de l'e-mail (texte brut).
        chemin_fichier (str): Chemin local vers le fichier à joindre.
        nom_fichier_destinataire (str, optionnel): Nom du fichier tel qu'il apparaîtra pour le destinataire.
                                               Si None, utilise le nom du fichier d'origine.
    """

    # Configuration SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "mes.voyages.app@gmail.com"
    smtp_password = mdp_google

    # if nom_fichier_destinataire is None:
    #     nom_fichier_destinataire = os.path.basename(chemin_fichier)

    # Crée le message
    message = MIMEMultipart()
    message["From"] = smtp_user
    message["To"] = email_destinataire
    message["Subject"] = sujet
    message.attach(MIMEText(contenu, "plain"))

    # Ajoute la pièce jointe
    if chemin_fichier is not None and nom_fichier_destinataire is not None:

        with open(
            os.path.join(chemin_fichier, nom_fichier_destinataire), "rb"
        ) as attachment:
            # Utilise MIMEImage pour les images
            png = MIMEImage(attachment.read(), name=nom_fichier_destinataire)
        png.add_header(
            "Content-Disposition", "attachment", filename=nom_fichier_destinataire
        )
        message.attach(png)

    # Envoie l'e-mail
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, email_destinataire, message.as_string())
        return True
    except Exception as e:
        return e
