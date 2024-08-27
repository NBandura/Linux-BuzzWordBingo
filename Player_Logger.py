import datetime  # Importieren des datetime Moduls zum Erfassen der Zeit
import os  # Importieren des os Moduls, um Dateien zu erstellen und zu verwalten

class Logger:
    
    def __init__(self, playerId):
        self.playerId = playerId
        self.file = self._logCreateFile() #automatisches Erstellen der Log-Datei beim Erstellen eines Logger Objektes

    def _logCreateFile(self):
        logsFolderName = "player_logs" #Festlegen des Log-Ordner Namens
        if not os.path.exists(logsFolderName): #Erstellen eines neuen Log-Ordners, falls dieser nicht vorhanden ist
            os.makedirs(logsFolderName)
        
        time = datetime.datetime.now()
        filename = time.strftime(f"{logsFolderName}/%Y-%m-%d-%H-%M-%S") + f"-bingo-{self.playerId}.txt"
        with open(filename, "w") as file: #"with open" um Datei nicht wieder schließen zu müssen
            pass #pass um Datei "nur" zu erstellen
        return filename #Rückgabe des Dateinamens um ihn im Objekt zu verwenden

    #Spielstart mit Zeitstempel der Log-Datei hinzufügen
    def logGameStart(self):#
        time = datetime.datetime.now()
        with open(self.file, "a") as file:
            file.write(time.strftime("%Y-%m-%d-%H-%M-%S ") + "Start des Spiels\n")

    #Spielende mit Zeitstempel der Log-Datei hinzufügen
    def logGameEnd(self):#
        time = datetime.datetime.now()
        with open(self.file, "a") as file:
            file.write(time.strftime("%Y-%m-%d-%H-%M-%S ") + "Ende des Spiels\n")

    #durchgestrichenes Wort mit Zeitstempel und Koordinaten der Log-Datei hinzufügen
    def logCrossedWord(self, word, buttonId):#
        time = datetime.datetime.now()
        with open(self.file, "a") as file:
            file.write(time.strftime("%Y-%m-%d-%H-%M-%S ") + word + " (crossed) " + buttonId + "\n")
    
    #entferntes Wort mit Zeitstempel und Koordinaten der Log-Datei hinzufügen
    def logUncrossedWord(self, word, buttonId):#
        time = datetime.datetime.now()
        with open(self.file, "a") as file:
            file.write(time.strftime("%Y-%m-%d-%H-%M-%S ") + word + " (uncrossed) " + buttonId + "\n")
    
    #Möglichkeit zum abschließen eines "Bingos" der Log-Datei hinzufügen
    def logBingoOpportunity(self):
        time = datetime.datetime.now()
        with open(self.file, "a") as file:
            file.write(time.strftime("%Y-%m-%d-%H-%M-%S ") + "Bingo Überprüfung (true)\n")

    #Spielende der Log-Datei hinzufügen
    def logGameResult(self, result):#
        time = datetime.datetime.now()
        with open(self.file, "a") as file:
            #Prüfen, welcher Status für den jeweiligen Spieler bei Spielende vorliegt (0 = Sieg, 1 = Abbruch)
            if result == 0:
                file.write(time.strftime("%Y-%m-%d-%H-%M-%S ") + "Sieg\n")
            elif result == 1:
                file.write(time.strftime("%Y-%m-%d-%H-%M-%S ") + "Niederlage\n")
