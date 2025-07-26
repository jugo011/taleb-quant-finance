# taleb-quant-finance
0 │ Warum wir überhaupt ein „eigenes“ Universum bauen
Wir haben keine Live-Datenquellen wie Bloomberg.

Trotzdem wollen wir zeigen, wie man – methodisch sauber, eine Zinskurve rekonstruiert,
damit einen Swap bewertet,und anschließend das tägliche Markt­risiko misst.

Dafür erfinden wir uns „Spielplatz-Zahlen“, weil das Vorgehen (die Schritte) wichtiger ist als der exakte Datensatz.

1 │ Eine „Zinskurve“ von Hand anlegen
Was ist eine Zinskurve?
Stell dir für jedes Jahr 1 … 10 kleine Sparbücher vor.
– Jedes Buch sagt: „Wenn du mir heute 100 € gibst, bekommst du in n Jahren so viel zurück.“

Unsere erfundenen Jahres-Sätze (Par-Swap-Sätze)yaml

Jahr 1: 2.10 %
Jahr 2: 2.30 %
…  
Jahr10: 3.00 %
Mehr Fantasie brauchen wir zunächst nicht.

2 │ Bootstrapping – aus Sparbuch-Sätzen echte „heutige Preise“ machen
Ziel Finde für jedes Jahr den Diskontfaktor
𝑃(0,𝑇)
P(0,T) = „Wie viel kostet 1 € heute, der sicher erst in T Jahren fällig wird?“

Warum kompliziert? – Ein Par-Swap-Satz ist kein Zinssatz einer Einmal-Zahlung, sondern ein Mischsatz aus mehreren Kupons. Wir müssen die Gleichung deshalb aufdröseln.

Vorgehen (Rekursion)

Jahr 1 Par-Swap 2,1 % heißt:

ich zahle einmal 2,1 € Kupon, bekomme 100 € zurück, sollte heute 100 € wert sein.

→ 𝑃(0,1)=11+0,021≈0,979
P(0,1)= 1+0,021 ≈0,979

Jahr 2 gleiches Prinzip, aber jetzt steckt 
𝑃(0,1)
P(0,1) schon drin; Formel auflösen ⇒ P(0,2).
Und so weiter bis Jahr 10.

Am Ende haben wir zehn Zahlen, z. B.P(0,5)=0,884 (heute 0,884 € zahlen → in 5 Jahren 1 € zurück).

3 │ Was ist unser Produkt? – ein 5-Jahres-Zins-Swap
Nominalgröße: 100 Mio €

Fixe Seite: wir zahlen jedes Jahr 2,50 %.

Variable Seite: wir bekommen jedes Jahr den dann gültigen „Geldmarktzins“.

Warum so beliebt? Banken sichern sich damit gegen Zins­bewegungen ab.

4 │ Wie viel ist der Swap heute wert?
Fixed-Leg
Jedes Jahr zahlen wir 2,5 % × 100 Mio = 2,5 Mio.
Wir diskontieren jeden Kupon mit seinem P(0,T) und summieren.

Float-Leg
Für einen neu abgeschlossenen Swap ist die Float-Leg so konstruiert,
dass heute ihr Barwert ≈ Nominal – letzter Diskontfaktor ist 100Mio(1−P(0,5))).
So gleicht sich das Ganze (theoretisch) aus.

Die Differenz Fixed − Float = aktueller Marktwert.
Mit unseren Spielzahlen kommt z. B. ≈ 30 000 € heraus – fast null, wie erwartet.

5 │ Wie empfindlich ist der Swap, wenn Zinsen sich bewegen? (DV01 & Gamma)
DV01 = Euro-Änderung des Marktwerts, wenn alle Zinsen um +0,01 % (=1 bp) steigen.
Messen: wir schieben die ganze Kurve einmal +1 bp, rechnen Swap neu,
schieben –1 bp, rechnen neu → mittlere Differenz / 2.

Gamma = Wie stark ändert sich die DV01 selbst bei großen Moves?
(zweites Bump nach oben/unten).

Mit 100 Mio-Swap erhält man DV01 vielleicht ≈ 90 000 €/bp; Gamma kleiner.

6 │ Wir lassen die Zinsen „zittern“ – Monte Carlo
Normale Alltagsschwankung Wir würfeln jeden Tag ein Δr aus einer Normal­verteilung mit σ = 0,05 % (= 5 bp).

Taleb-Schock Mit 0,004 % Tages-Chance addieren wir zusätzlich +2,00 % (=200 bp) – Black Swan.

Für jeden Tag (insgesamt 10 000) rechnen wir den Verlust als
−
(DV01×Δ𝑟×10000+1/2Gamma(Δ𝑟×10000)²

(×10 000, weil wir von % in bp umrechnen.)

—

7 │ Risiko­zahlen draus ziehen
Value-at-Risk 99 %
Sortiere alle Tagesverluste; nimm die 99-Prozent-Schwelle.

Expected Shortfall 99 %
Durchschnitt aller Verluste schlimmer als diese Schwelle.

Stress-Loss (+200 bp)
Einmal deterministisch: DV01×200 bp + Gamma-Term.

Mit unseren Parametern kommt (Beispiel):
VaR99  ≈ 1 000 000 €
ES99   ≈ 1 250 000 €  (Taleb höher)
Stress ≈ 15 000 000 €
—

8 │ Bilder malen
Zoom-Histogramm (–0,5 … +1 Mio)
zeigt, dass 99 % Verluste „klein“ sind und Gaussian ≈ Taleb.

Log-Histogramm (–1 … +16 Mio)
zeigt den rechten „Schwanz“ – nur Taleb hat dort Balken, Gaussian praktisch nichts.

—

9 │ Was wir damit gelernt haben
Im Tagesgeschäft wirken Taleb-Sprünge fast unsichtbar (VaR kaum höher).

Aber: Expected-Shortfall und Stress-Loss steigen massiv – wenn der Sprung eintritt, sind die Verluste zig-fach größer als das, was ein glattes Normal­modell suggeriert.

Genau das ist Talebs Botschaft: „Die Katastrophen sitzen im Schwanz, nicht im Bauch der Verteilung.“
