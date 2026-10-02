TEKNISK for leksikograf
=======================


## Redigering i XMLmind

### Pass på!

**Aldri opne tildefiler!**

Dei ser slik ut, med `~` til slutt: `N_sme.xml~`
Dette er backupfiler som kan redde dagen din, men du skal **aldri**
redigere i dei.

**Ikkje ha xmlmind open når du oppdaterer katalogen**

(når du skriv git pull). Problemet er at du
risikerer å lagre din gamle versjon

> Documnmet .. seems to have been modified using an external
  application. "Do you still want to save this document to its current
  location?
  
Viss du svarer **OK** på dette vil du overskrive det kollegaen din har
gjort.

Måter å ordne dette på:

1. Lukk dokumentet i xmlmind **før** du oppdaterer (før git pull)
2. Viss du glømte det: Gje fila eit nytt namn (sukk), hent den nye, og
   kopier over frå det nye namnet. Hugs å slette den nye.
3. Viss du glømte det også får du ein **konflikt**. Det tar vi opp
   seinare.


### Navigering i "treet":

| Funksjon | Mac | Windows | Lenes huskeregler |
|----------|-----|---------|-------------------|
| Opp i hierarkiet | cmd+↑ | ctrl+↑ | - |
| Ned i hierarkiet | cmd+↓ | ctrl+↓ | - |
| Legg til etter | cmd+j | ctrl+J | Jälkeen / Jetter :-) |
| Legg til før | cmd+b | ctrl+h | Before / Høyere |
| Legg til attributt | cmd+e | ctrl+e | Ekspander |
| Legg til lenke | cmd+i| ctrl+i | Insert |
| Kopier | cmd+c | ctrl+c | Copy |
| Lim inn | cmd+v | ctrl+v | Vlim inn :-) |
| Angre | cmd+z | ctrl+z | - |
| Angre det du angret | cmd+y | ctrl+y | - |
| Lagre | cmd+s | ctrl+s | Save |
| Finn dette ordet | cmd+f | ctrl+f | Finn   |
| Søk | cmd+g | ctrl+g | Gå ned for å finne ordet |
| Søk | cmd+G | ctrl+G | Gå opp for å finne ordet |


## xml-strukturen og terminologien vi bruker

&lt;e&gt; : **entry** (hovedelementet med all informasjon til hvert lemma.
 
&lt;lg&gt; : **lemma group** Vi legger til attributt for å skille mellom homonyme lemmaer, med NomAg, f.eks. vuovdi (skog) og vuovdi NomAg (selger), eller G3, f.eks. vuorri (omgang) og vuorri G3 (fisk). For homonymer har samme morfologi, bruker vi hid=1, hid=2, f.eks. busse (buss) og busse (pose)).

- &lt;l&gt; : lemma, med informasjon om **pos** (Part of Speech). 


&lt;dg&gt;: **definition group** (ikke obligatorisk), som inneholder:
- &lt;d&gt; : definition


&lt;sg&gt;: **synonym group** (ikke obligatorisk), som inneholder en eller flere:
- &lt;s&gt; : synonym

&lt;antg&gt;: **antonym group** (ikke obligatorisk), som inneholder en eller flere:
- &lt;ant&gt; : synonym


&lt;xg&gt; : **example group** (hver xg inneholder bare ett eksempel)
- &lt;x&gt; : eksempel på kildespråk

Etter siste &lt;dg&gt;, kan det legges til

&lt;ig&gt; : **idiom group**, som inneholder
- &lt;i&gt; : idiom eller fast uttrykk
- &lt;id&gt; : forklaring til idiomet
- &lt;xg&gt; : **example group** (ikke obligatorisk)
