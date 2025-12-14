from kivi_paperi_sakset import KiviPaperiSakset


def main():
    while True:
        print(
            "Valitse pelataanko"
            "\n (a) Ihmistä vastaan"
            "\n (b) Tekoälyä vastaan"
            "\n (c) Parannettua tekoälyä vastaan"
            "\nMuilla valinnoilla lopetetaan"
        )

        vastaus = input()
        if vastaus:
            vastaus = vastaus.lower()[-1]
            vastaukset = ["a", "b", "c"]
            if vastaus not in vastaukset:
                break
            print(
                "Peli loppuu kun pelaaja antaa virheellisen siirron eli jonkun muun kuin k, p tai s"
            )
            KiviPaperiSakset().pelaa(vastaus)
        break


if __name__ == "__main__":
    main()
