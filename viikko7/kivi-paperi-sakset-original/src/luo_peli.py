from kps_parempi_tekoaly import KPSParempiTekoaly
from kps_tekoaly import KPSTekoaly
from kps_pelaaja_vs_pelaaja import KPSPelaajaVsPelaaja


class LuoPeli:
    @staticmethod
    def luo_peli(valinta):
        if valinta == "a":
            return KPSPelaajaVsPelaaja()
        if valinta == "b":
            return KPSTekoaly()
        if valinta == "c":
            return KPSParempiTekoaly()
        raise ValueError("Virheellinen valinta")
