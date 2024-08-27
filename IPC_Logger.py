import datetime  #Importieren des datetime Moduls zum Erfassen der Zeit
import os  #Importieren des os Moduls, um Dateien zu erstellen und zu verwalten

class IPCLogger:
    
    def __init__(self, gameName, gameId):
        self.gameName = gameName
        self.gameId = gameId
        self.file = self._logCreateFile() #automatisches Erstellen der Log-Datei beim erstellen eines Logger Objektes

    def _logCreateFile(self): 
        logsFolderName = "ipc_logs" #Festlegen des Log-Ordner Namens
        if not os.path.exists(logsFolderName): #Erstellen eines neuen Log-Ordners, falls dieser nicht vorhanden ist
            os.makedirs(logsFolderName)
        
        filename = f"{logsFolderName}/ipc-{self.gameName}-{self.gameId}.txt"
        with open(filename, "w") as file: #"with open" um Datei nicht wieder schließen zu müssen
            pass #pass um Datei "nur" zu erstellen
        return filename #Rückgabe des Dateinamens um ihn im Objekt zu verwenden

    #Methode um Grundkonstrukt einer Log-Zeile zu realisieren
    def log(self, message):
        time = datetime.datetime.now()
        with open(self.file, "a") as file:
            file.write(time.strftime("%Y-%m-%d-%H-%M-%S ") + message + "\n") #Grundkonstrukt einer Log-Zeile + Nachricht

    #Methoden um IPC-Ereignisse zu loggen (selbsterklärend über Namen)
    def logGameCreation(self, spielerId):
        self.log(f"Spiel von {spielerId} erstellt")

    def logAddWord(self, word,spielerId):
        self.log(f"Wort von {spielerId} hinzugefügt: {word}")

    def logBingo(self, spielerId):
        self.log(spielerId + " hat Bingo gerufen")

    def logSetDateipfad(self, spielerId, dateipfad):
        message=spielerId + " hat den Dateipfad "+ dateipfad +" gesetzt"
        message=str(message)
        self.log(message)

    def logSetGröße(self, spielerId, größe):
        message=spielerId + " hat die Spielgröße " + str(größe) + " gesetzt"
        message=str(message)
        self.log(message)

    def logReadLastWord(self, spielerId):
        self.log(spielerId + " hat das letzte Wort aus demShared Memory gelesen")

    def logReadWortliste(self, spielerId):
        self.log(spielerId + " hat die Wortliste aus demShared Memory gelesen")

    def logReadStartStatus(self, spielerId):
        self.log(spielerId + " hat den Start-Status aus demShared Memory gelesen")

    def logGetDateipfad(self, spielerId):
        self.log(spielerId + " hat den Dateipfad aus demShared Memory gelesen")

    def logGetGröße(self, spielerId):
        self.log(spielerId + " hat die Größe aus demShared Memory gelesen")

    def logCheckIfBingo(self, spielerId):
        self.log(spielerId + " hat den Bingo-Status aus demShared Memory gelesen")

    def logGameDeletion(self, spielerID):
        self.log(spielerID+ " hat den Shared Memory gelöscht (Spielende)")

    def logVerbindungTrennen (self, spielerID):
        self.log(spielerID+" hat (falls vorhanden) die Verbindung getrennt")