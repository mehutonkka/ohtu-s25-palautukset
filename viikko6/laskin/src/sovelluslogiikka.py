class Sovelluslogiikka:
    def __init__(self, arvo=0):
        self._arvo = arvo
        # simple history stack for undo
        self._history = []

    def miinus(self, operandi):
        self._history.append(self._arvo)
        self._arvo = self._arvo - operandi

    def plus(self, operandi):
        self._history.append(self._arvo)
        self._arvo = self._arvo + operandi

    def nollaa(self):
        self._history.append(self._arvo)
        self._arvo = 0

    def aseta_arvo(self, arvo):
        self._history.append(self._arvo)
        self._arvo = arvo

    def kumoa(self):
        if self._history:
            self._arvo = self._history.pop()

    def arvo(self):
        return self._arvo
