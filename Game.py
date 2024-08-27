## Importieren der benötigten Bibliotheken
import random
from textual import on
from textual.app import App, ComposeResult
from textual.dom import DOMNode
from textual.widgets import Label, Footer, Button, Static, Header
import sys
import os
from Player_Logger import Logger
from IPC import SpielIPC
import argparse
import time
import atexit


## Beginn des Bingo Spiels markieren
print(100*"\n"+"<......Bingo Game......>")


## Spielnamen wählen und IPC spielspezifisch erstellen
while(True):
    spielname = input("Bitte geben Sie den Spielnamen ein, mit dem Sie sich verbinden wollen: ")
    IPC= SpielIPC(spielname,str(os.getpid()))
    if(IPC.checkIfStarted()):
        eingabe=input("Das Spiel läuft bereits.\nSie werden dem Spiel \""+spielname+"\" beitreten.\n\nBestätigen Sie mit Enter.\n\"exit\" wird den Prozess beenden. Jede andere Eingabe lässt Sie einen neuen Spielnamen eingeben.")
        if(eingabe==""):
            break
        elif(eingabe=="exit"):
            IPC.verbindungTrennen()
            sys.exit()
        else:
            IPC.verbindungTrennen()
            continue
    else:
        eingabe=input("Das Spiel existiert noch nicht.\nSie werden das Spiel \""+spielname+"\" erstellen und hosten.\n\nBestätigen Sie mit Enter.\n\"exit\" wird den Prozess beenden. Jede andere Eingabe lässt Sie einen neuen Spielnamen eingeben.")
        if(eingabe==""):
            break
        elif(eingabe=="exit"):
            IPC.speicherFreigeben()
            sys.exit()
        else:
            IPC.speicherFreigeben()
            continue

## Logger Prozessspezifisch erstellen
logger = Logger(os.getpid()) 


## Start des Spiels: Unterscheidung zwischen Startprozess und Joinprozess
logger.logGameStart()
if(IPC.checkIfStarted()):
    size=IPC.getGroesse()
    dateipfad=IPC.getDateipfad()
    istStartProzess=False
    buzzword_Wörter = []
    with open(dateipfad, 'r') as file:
        buzzword_Wörter = [zeile.strip() for zeile in file]
else:
    size=0
    while(True):
        try:
            size=int(input("Bitte gebe die Spielfeldgröße ein: "))
        except ValueError:
            None
        if(size < 3 or size > 7 ):
            print("Ungültige Größe: Erlaubt ist eine Größe von 3 - 7 und sie darf keine Dezimalzahl sein")
        else:
            break
    while (True):
        try:
            eingabe=input("Möchtest du die standard Buzzwords-Datei verwenden, drücke Enter. Sonst gib den Pfad an.")
            if(eingabe==""):
                dateipfad="buzzwords.txt"
            else:
                dateipfad=eingabe
            buzzword_Wörter = []
            with open(dateipfad, 'r') as file:
                buzzword_Wörter = [zeile.strip() for zeile in file]
            if(len(buzzword_Wörter)<size*size):
                print("Die Anzahl der Wörter in der Datei ist zu gering!")
                continue
            break
        except Exception:
            print("Der Dateipfad ist ungültig!")
    IPC.setDateipfad(dateipfad)
    IPC.setGroesse(size)
    IPC.startGame()
    istStartProzess=True


## Die Bingo App
class Bingo(App):

    ## CSS-Datei für das Styling
    CSS_PATH = "BwB_Css.tcss"


    ## Allgemeine Funktionen für den späteren gebraucht der App
    # Erstellen der Bingo-Felder
    def bingo_felder_erstellen(self, size):
        self.grid_container.remove_children()  # Entfernt das alte Grid
        
        self.button_name_Liste = []  # Liste zum Speichern der Wörter
        self.button_status = {}  # Dictionary zum Speichern des Status der Buttons

        benutzte_wörter = []
        for y in range(size):
            for x in range(size):
                if size in {5, 7} and y == size // 2 and x == size // 2:
                    button_name = "Joker Feld"
                else:
                    while True:
                        button_name = random.choice(buzzword_Wörter)
                        if button_name not in benutzte_wörter:
                            benutzte_wörter.append(button_name)
                            break
                self.button_name_Liste.append(button_name)
                button_id = f"button_{y}_{x}"
                self.button_status[button_id] = False  # Initialer Status des Buttons ist False (nicht durchgestrichen)
                if size in {5, 7} and y == size // 2 and x == size // 2: 
                    self.button_status[button_id] = True # Joker Feld ist automatisch durchgestrichen
                    button = Button(button_name, id=button_id, classes="Joker")
                    button.disabled = True
                else:
                    button = Button(button_name, id=button_id, classes="bingo-button")
                self.grid_container.mount(button)
        
        self.grid_container.styles.grid_size_columns = size  # Formatiert in CSS
        self.grid_container.styles.grid_size_rows = size


    # Überprüft, ob ein Bingo vorliegt
    def überprüfe_bingo(self):
        # Horizontale Überprüfung
        for y in range(size):
            if all(self.button_status.get(f"button_{y}_{x}", False) for x in range(size)):
                self.bingo_confirm_button.add_class("bingoconf")  # Fügt die "bingoconf"-Klasse zum Button hinzu
                logger.logBingoOpportunity()
                return True
    
        # Vertikale Überprüfung
        for x in range(size):
            if all(self.button_status.get(f"button_{y}_{x}", False) for y in range(size)):
                self.bingo_confirm_button.add_class("bingoconf")  # Fügt die "bingoconf"-Klasse zum Button hinzu
                logger.logBingoOpportunity()
                return True
    
        # Diagonale Überprüfung (von links oben nach rechts unten)
        if all(self.button_status.get(f"button_{i}_{i}", False) for i in range(size)):
            self.bingo_confirm_button.add_class("bingoconf")  # Fügt die "bingoconf"-Klasse zum Button hinzu
            logger.logBingoOpportunity()
            return True
    
        # Diagonale Überprüfung (von rechts oben nach links unten)
        if all(self.button_status.get(f"button_{i}_{size-1-i}", False) for i in range(size)):
            self.bingo_confirm_button.add_class("bingoconf")  # Fügt die "bingoconf"-Klasse zum Button hinzu
            logger.logBingoOpportunity()
            return True
    
        self.bingo_confirm_button.remove_class("bingoconf")  # Entfernt die "bingoconf"-Klasse vom Button
        return False
    

    
    ## Methode zum Erstellen der GUI
    def compose(self):
        # Erstellen der Buttons und Labels
        self.zufallswort_label = Label("", id="zufallswort_label")
        self.error_message = Label("", id="error_message")
        self.zufallswort_button = Button("Wort generieren", id="zufallswort")
        self.grid_container = Static(classes="bingo-grid")
        self.gewonnen_label = Label("", id="gewonnen_label")
        self.bingo_confirm_button = Button("Bingo bestätigen", id="bingo_confirm") 
        self.quit_button = Button("Quit", id="quit", classes="quit-button")  # Neuer Quit-Button
        self.speicher_freigeben_button = Button("Spiel abbrechen", id="speicher_freigeben", classes="freigeben")  # speicher freigeben
        self.getWort = Label("", id="getWort")
        self.wortlisteTitel = Label("\nListe bisheriger Wörter:\n", id="wortlisteTitel",classes="wortlisteTitel")
        self.wortliste_label = Label("", id="wortliste_label")
        self.CheckBingo_label = Label("", id="CheckBingo_label")
        self.title = f"Spielname: {spielname} \t" + f"\tIPC_ID: {IPC.getIPC_ID()} \t" +f"\tSpielerID: {os.getpid()}"# Header
        
        # Der Anzeige Buttons und Labels hinzufügen
        yield Header("", id="header-ID", classes="header")
        yield self.error_message
        if(istStartProzess):
            yield self.zufallswort_label
            yield self.zufallswort_button
            yield self.speicher_freigeben_button
        else:
            yield self.getWort
        yield self.grid_container
        yield self.CheckBingo_label
        yield self.gewonnen_label
        yield self.bingo_confirm_button 
        yield self.quit_button 
        yield self.wortlisteTitel
        yield self.wortliste_label
        yield Footer()

        # Erstellen Prozess spezifischer Variablen bezüglich des Status des Spiels
        self.SiegerProzess=False
        self.SpielVorbei=False

        # Erstellen des Bingo-Feldes beim starten des Spiels
        self.bingo_felder_erstellen(size)

    
    ## Event-Methoden für den Button-Druck
    # Betrifft jeden Button im Grid
    @on(Button.Pressed) 
    def wort_streiche(self, event: Button.Pressed):
        buttonName = str(event.button.label)
        button_id = str(event.button.id)  # Damit man eben genau diesen Button anspricht, keinen anderen 
        if button_id.startswith("button_"):  # Nur die Buttons, die auch im Grid sind
            if button_id in self.button_status:
                self.button_status[button_id] = not self.button_status[button_id]  # Ändert den Status des Buttons
                if self.button_status[button_id]:
                    logger.logCrossedWord(buttonName, button_id)
                    event.button.add_class("strikethrough")  # Fügt dem Button die Klasse "strikethrough" hinzu
                else:
                    logger.logUncrossedWord(buttonName, button_id)
                    event.button.remove_class("strikethrough")  # Entfernt die Klasse "strikethrough" vom Button
                if self.überprüfe_bingo():
                    self.update_gewonnen_label("")

    # Betrifft den Button "Wort generieren"
    @on(Button.Pressed, "#zufallswort")
    def zufallswort_generieren(self):
        zufallswort = random.choice(buzzword_Wörter)
        IPC.addWord(zufallswort)
        self.zufallswort_label.update(zufallswort)

    # Betrifft den Button "Bingo bestätigen"
    @on(Button.Pressed, "#bingo_confirm")  
    def on_bingo_confirm(self, event):
        if self.überprüfe_bingo():
            self.update_gewonnen_label("") 
            IPC.bingo()
            self.SiegerProzess=True
        else:
            self.update_gewonnen_label("Noch kein Bingo. Versuche es weiter!")
    
    # Betrifft den Button "Quit"
    @on(Button.Pressed, "#quit") 
    def on_quit(self, event):
        IPC.verbindungTrennen()
        self.exit()

    # Betrifft den Button "Spiel abbrechen"
    @on(Button.Pressed, "#speicher_freigeben") 
    def speicher_freigeben(self):
        IPC.bingo()
        
    

    ## Update-Methoden für die Labels
    # Aktualisiert das Label für das Gewinnen
    def update_gewonnen_label(self, message):
        self.gewonnen_label.update(message)

    # Aktualisiert das Label für das aktuelle Wort
    def update_lastWort(self):
        if(not self.SpielVorbei):
            self.getWort.update("Aktuelles Wort: "+IPC.getLastWort())
    
    # Aktualisiert das Label für die Wortliste
    def update_Wortliste(self):
        if(not self.SpielVorbei):
            self.wortliste_label.update((IPC.getWortString()).replace(";", "\n"))

    # Aktualisiert das Label für das Bingo und deaktiviert die Buttons, wenn ein Bingo empfangen wird
    def update_checkBingo(self):
        if(not self.SpielVorbei):
            if IPC.checkIfBingo():
                self.bingo_confirm_button.disabled=True
                self.zufallswort_button.disabled=True
                self.speicher_freigeben_button.disabled=True
                self.grid_container.disabled=True
                self.SpielVorbei=True
                if(self.SiegerProzess==False):
                    logger.logGameResult(1)
                    self.CheckBingo_label.update("Du hast verloren!")
                else:
                    logger.logGameResult(0)
                    self.CheckBingo_label.update("Du hast gewonnen!")
                time.sleep(1)
                IPC.speicherFreigeben()  
                logger.logGameEnd()    
        elif(not self.SpielVorbei):
            self.CheckBingo_label.update("Es hat noch niemand gewonnen!")
    
    ## Interval-Methoden für die Aktualisierung der Labels
    def on_mount(self):
        self.set_interval(0.1, self.update_lastWort)
        self.set_interval(0.1, self.update_Wortliste)
        self.set_interval(0.1, self.update_checkBingo)
       

## Starten der Bingo App
if __name__ == "__main__": 
    Bingo().run()