import posix_ipc
import mmap
import pickle
import random
from IPC_Logger import IPCLogger


class SpielIPC:
      # Konstruktor für unterschiedliche Spiele
    def __init__(self, SpielName,ProzessID):
        self.SpielName = SpielName
        self.ProzessID = ProzessID
        self.Connection = self._connect()
        self.IPCLogger=IPCLogger(SpielName,self.getIPC_ID())

    # Funktion zum Verbinden mit dem Shared Memory
    def _connect(self):
        # Erzeugen des Shared Memory Objekts mit dem Namen "BuzzWordBingo" und einer Größe von 1024 Bytes
        shared_memory = posix_ipc.SharedMemory(name="BuzzWordBingo_"+self.SpielName, size=1024, flags=posix_ipc.O_CREAT)

        try: # Check, ob bereits ein list-Objekt im Shared Memory vorhanden ist, sonst wird ein leeres list-Objekt erzeugt
            # Erzeugen einer mmap-Instanz, um auf den Shared Memory zuzugreifen
            shared_memory_mmap = mmap.mmap(shared_memory.fd, shared_memory.size, mmap.MAP_SHARED, mmap.PROT_READ)
            # Lesen der Daten aus dem Shared Memory und Umwandeln in eine Liste
            listeAlsCode = shared_memory_mmap.read(shared_memory.size)
            shared_memory_mmap.close()
            speicherListe = pickle.loads(listeAlsCode)
        except pickle.UnpicklingError:
            # Falls ein Fehler beim Entpacken der Daten auftritt, weil keine Liste da ist, wird eine leere Liste erzeugt und in den Shared Memory geschrieben
            listeAlsCode = pickle.dumps(["", "", "", "","",str(random.randint(0,1000000))])
            shared_memory_mmap = mmap.mmap(shared_memory.fd, shared_memory.size, mmap.MAP_SHARED, mmap.PROT_WRITE)
            shared_memory_mmap.write(listeAlsCode)
            shared_memory_mmap.close()

        return shared_memory

    # Funktion zum Lesen der Daten aus dem Shared Memory
    def _read(self):
        shared_memory = self.Connection
        shared_memory_mmap = mmap.mmap(shared_memory.fd, shared_memory.size, mmap.MAP_SHARED, mmap.PROT_READ)
        listeAlsCode = shared_memory_mmap.read(shared_memory.size)
        speicherListe = pickle.loads(listeAlsCode)
        shared_memory_mmap.close()
        return speicherListe

    # Funktion zum Schreiben der Daten in den Shared Memory
    def _write(self,speicherListe):
        listeAlsCode = pickle.dumps(speicherListe)
        shared_memory = self.Connection
        shared_memory_mmap = mmap.mmap(shared_memory.fd, shared_memory.size, mmap.MAP_SHARED, mmap.PROT_WRITE)
        shared_memory_mmap.write(listeAlsCode)
        shared_memory_mmap.close()

    def verbindungTrennen(self):
        self.Connection.close_fd()
        self.IPCLogger.logVerbindungTrennen(self.ProzessID)
        return None

    # Funktion zum Löschen des Shared Memory
    def speicherFreigeben(self):
        shared_memory = self.Connection
        try:
            shared_memory.unlink()
            self.IPCLogger.logGameDeletion(self.ProzessID)
        except posix_ipc.ExistentialError:
            pass
        finally:
            self.verbindungTrennen()

    # Funktion zum Überprüfen, ob ein Bingo erreicht wurde
    def checkIfBingo(self):
        speicherListe = self._read()
        self.IPCLogger.logCheckIfBingo(self.ProzessID)
        if speicherListe[0] == "Bingo":
            return True
        else:
            return False
        
    # Funktion zum Abrufen der IPC-ID
    def getIPC_ID(self):
        speicherListe = self._read()
        return speicherListe[5]

    # Check, ob das Spiel gestartet wurde
    def checkIfStarted(self):
        speicherListe = self._read()
        self.IPCLogger.logReadStartStatus(self.ProzessID)
        if speicherListe[4] == "started":
            return True
        else:
            return False

    # Funktion zum Abrufen des Dateipfads
    def getDateipfad(self):
        speicherListe = self._read()
        self.IPCLogger.logGetDateipfad(self.ProzessID)
        return speicherListe[1]

    # Funktion zum Abrufen der Größe des Spielfeldes
    def getGroesse(self):
        speicherListe = self._read()
        self.IPCLogger.logGetGröße(self.ProzessID)
        return speicherListe[2]

    # Funktion zum Abrufen der Wortliste als String
    def getWortString(self):
        speicherListe = self._read()
        self.IPCLogger.logReadWortliste(self.ProzessID)
        return speicherListe[3]

    # Funktion zum Abrufen der Wortliste als Liste
    def _getWortListe(self):
        wortString = self.getWortString()
        wortListe = wortString.split(";")
        return wortListe

    # Funktion zum Abrufen des letzten Wortes
    def getLastWort(self):
        wortListe = self._getWortListe()
        self.IPCLogger.logReadLastWord(self.ProzessID)
        return wortListe[-1]

    # Funktion zum Setzen des Bingo-Status
    def bingo(self):
        position0 = "Bingo"
        position1 = self.getDateipfad()
        position2 = self.getGroesse()
        position3 = self.getWortString()
        if self.checkIfStarted():
            position4 = "started"
        else:
            position4 = ""
        position5 = self.getIPC_ID()
        speicherListe = [position0, position1, position2,position3,position4,position5]
        self._write(speicherListe)
        self.IPCLogger.logBingo(self.ProzessID)


    # Funktion zum Setzen des Dateipfads
    def setDateipfad(self,dateipfad):
        if self.checkIfBingo():
            position0 = "Bingo"
        else:
            position0 = ""
        position1 = dateipfad
        position2 = self.getGroesse()
        position3 = self.getWortString()
        if self.checkIfStarted():
            position4 = "started"
        else:
            position4 = ""
        position5 = self.getIPC_ID()
        speicherListe = [position0, position1, position2,position3,position4,position5]
        self._write(speicherListe)
        self.IPCLogger.logSetDateipfad(self.ProzessID,dateipfad)

    # Funktion zum Setzen der Größe des Spielfeldes
    def setGroesse(self,groesse):
        if self.checkIfBingo():
            position0 = "Bingo"
        else:
            position0 = ""
        position1 = self.getDateipfad()
        position2 = groesse
        position3 = self.getWortString()
        if self.checkIfStarted():
            position4 = "started"
        else:
            position4 = ""
        position5 = self.getIPC_ID()
        speicherListe = [position0, position1, position2,position3,position4,position5]
        self._write(speicherListe)
        self.IPCLogger.logSetGröße(self.ProzessID,groesse)

    # Funktion zum Hinzufügen eines Wortes zur Wortliste
    def addWord(self,wort):
        if self.checkIfBingo():
            position0 = "Bingo"
        else:
            position0 = ""
        position1 = self.getDateipfad()
        position2 = self.getGroesse()
        if(len(self.getWortString()) > 0):
            wort = ";" + wort
        else:
            wort = wort
        position3 = self.getWortString() + wort
        if self.checkIfStarted():
            position4 = "started"
        else:
            position4 = ""
        position5 = self.getIPC_ID()
        speicherListe = [position0, position1, position2,position3,position4,position5]
        self._write(speicherListe)
        self.IPCLogger.logAddWord(self.ProzessID,wort)

    # Funktion zum Starten des Spiels
    def startGame(self):
        if self.checkIfBingo():
            position0 = "Bingo"
        else:
            position0 = ""
        position1 = self.getDateipfad()
        position2 = self.getGroesse()
        position3 = self.getWortString()
        position4 = "started"
        position5 = self.getIPC_ID()
        speicherListe = [position0, position1, position2,position3,position4,position5]
        self._write(speicherListe)
        self.IPCLogger.logGameCreation(self.ProzessID)