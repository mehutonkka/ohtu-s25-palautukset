from tuomari import Tuomari


class KiviPaperiSakset:
    def pelaa(self, valinta):
        from luo_peli import LuoPeli

        tuomari = Tuomari()
        vastustaja = LuoPeli.luo_peli(valinta)
        ekan_siirto = self._ensimmaisen_siirto()
        tokan_siirto = vastustaja._toisen_siirto(ekan_siirto)

        while self._onko_ok_siirto(ekan_siirto) and self._onko_ok_siirto(tokan_siirto):
            tuomari.kirjaa_siirto(ekan_siirto, tokan_siirto)
            print(tuomari)

            ekan_siirto = self._ensimmaisen_siirto()
            tokan_siirto = vastustaja._toisen_siirto(ekan_siirto)

        print("Kiitos!")
        print(tuomari)

    def _ensimmaisen_siirto(self):
        return input("Ensimmäisen pelaajan siirto: ")

    def _onko_ok_siirto(self, siirto):
        return siirto == "k" or siirto == "p" or siirto == "s"
