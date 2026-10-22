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

1. Lukk dictfila i xmlmind **før** du oppdaterer (før git pull)
2. Viss du glømte det og **ikke har valgt yes** for å lagre dictfila: 
Kopier det som du har gjort til ei notatdokument og velg **no** for å lagre dictfila. Deretter legger du til det du har kopiert i dictfila.
3. Viss du glømte det og **valgte yes for å lagre fila**: da får du ein **konflikt**. Be om hjelp.  Ingenting er tapt, og vi tar opp hvordan du gjør dette teknisk seinare. 


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


### Hurtigtaster med vårt XML Mind tilleggsprogram
Vårt tilleggsprogram legger til en rekke nye hurtigtaster for redigering og navigering.
Se hvordan man setter det opp lenger ned.


| Command | Windows | Mac |
|---|---|---|
| Insert reference | Ctrl+Alt+R | Cmd+Option+R |
| Follow link | Ctrl+Alt+L | Cmd+Option+L |
| Go to entry | Ctrl+Alt+G | Cmd+Option+G |
| Go to entry in batch | Ctrl+Alt+B | Cmd+Option+B |
| New one of the same kind after (definition, synonym, example, …) | Ctrl+Enter | Cmd+Enter |
| New entry | Ctrl+Alt+N | Cmd+Option+N |
| New definition group | Ctrl+Alt+Enter | Cmd+Option+Enter |
| New synonym | Ctrl+Alt+S | Cmd+Option+S |
| New antonym | Ctrl+Alt+A | Cmd+Option+A |
| New example | Ctrl+Alt+E | Cmd+Option+E |
| New idiom | Ctrl+Alt+I | Cmd+Option+I |
| New comment | Ctrl+Alt+C | Cmd+Option+C |
| Move up | Alt+↑ | Option+↑ |
| Move down | Alt+↓ | Option+↓ |



## xml-strukturen og terminologien vi bruker

&lt;e&gt; : **entry** - Hovedelementet med all informasjon til hvert lemma.
Homonyme lemmaer som ikke har samme opprinnelse, skal ha egne entryer.  F.eks. 
- <i>vuovdi-vuovddit</i> (skog) og <i>vuovdi-vuovdit</i> (selger), 
- <i>vuorru-vuorut</i> (omgang) og <i>vuorru-vuorrut</i> (fisk). 
- Også homonymer som har samme morfologi, f.eks. <i>busse-busset</i> (buss) og <i>busse-busset</i> (pose)).
 
&lt;lg&gt; : **lemma group** med informasjon om **pos** (Part of Speech)
- &lt;l&gt; : lemma, og **type** hvis nødvendig.
- &lt;l&gt; : evt. flere lemmaer med ortografiske varianter av lemmaet, f.eks. vil  <i>girku kirku</i> være to lemmaer i samme lemma group

I &lt;l&gt;  legger vi til attributt for å skille mellom homonyme lemmaer som har hver sin entry: 
- vuovdi  og vuovdi type=NomAg
- vuorru og vuorru type=G3
- Homonymer som har samme morfologi, skilles med hid=1, hid=2
-- f.eks. busse hid=1 (buss) og busse hid=2 (pose).

&lt;dg&gt;: **definition group**, inneholder:
- &lt;d&gt; : definisjon


- &lt;syng&gt; : **synonym group**, (ikke obligatorisk), som inneholder en eller flere:
-- &lt;syn&gt; : synonym med definition refrence
- &lt;antg&gt;: **antonym group** (ikke obligatorisk), inneholder en eller flere:
-- &lt;ant&gt; : antonym med definition refrence
- &lt;d_ref&gt;: **definition refrence** - En link til en entry eller en
  spesifikk definisjon i en entry. Kan plasseres i en definisjonstekst, og
  må plasseres i synonymer og antonymer.

- &lt;xg&gt; : **example group**
--  &lt;x&gt; : eksempel setning eller fragment (gjerne flere). Hele setninger starter med stor bokstav og avsluttes med punktum (evt. spørsmålstegn), Skal ikke avsluttes med mellomrom.


&lt;ig&gt; : **idiom group**, (ikke obligatorisk) inneholder:
- &lt;i&gt; : idiom eller fast uttrykk
- &lt;idg&gt; : **idiom definition group**, som inneholder
    - &lt;id&gt; : forklaring til idiomet
    - &lt;ix&gt; : eksempel til idiomet (ikke obligatorisk)

&lt;cg&gt; : **comment group**, inneholder en eller flere:
- &lt;c&gt; : Kommentarer for leksikografene, vil ikke vises når ordboken publiseres.


## Sette opp vårt XML Mind tilleggsprogram
I mappen `xxe/` finnes vårt tilleggsprogram til XML Mind som legger til en haug
med nye funksjonaliteter og hurtigtaster.

**Viktig!**  
Før vi kan sette opp tilleggsprogrammet må vi skru av en instilling i XML Mind.
Gå til `Options` → `Preferences` → `Advanced` → `Cached data` og skru av 
"Quick Start cache". Gjøres ikke dette vil ikke nye endringer i tilleggsprogrammet
vises. Når instillingen er skrudd av trenger man bare restarte XML Mind for å see
endringer.

### Mac

1. Påse at både [Python3](https://www.python.org/downloads/) og [homebrew](https://brew.sh/)
   er installert. Dette kan sjekkes i terminalen ved å skrive følgene kommandoer:
   
   ```sh
   which python
   which brew
   ```

2. Lag en lenke fra `xxe/` mappa til XML Mind sin `addon` mappe. Fyll inn riktig sti til
   `xxe/` mappa i den andre kommandoen. 

    ```sh
    mkdir -p ~/Library/Application\ Support/XMLmind/XMLEditor11/addon
    ln -s ~/FYLL-INN/dict-sme/xxe ~/Library/Application\ Support/XMLmind/XMLEditor11/addon/dict-sme
    ```

3. For å kunne lage PDFer, installer programmet WeasyPrint: 
    ```sh
    brew install weasyprint
    ```

4. Restart XML Mind.


### Windows

1. Installer [Python install manager](https://apps.microsoft.com/detail/9nq7512cxl7t) 

2. Åpne ett terminalvindu (Command Prompt) og skriv in følgende (Fyll inn navn
   og riktig sti til `xxe/` mappa):

    ```ps1
    setx XXE_ADDON_PATH "C:\Users\NAVN\FYLL-INN\dict-sme\xxe;+"
    ```

3. For å kunne lage PDFer: last ned WeasyPrint for Windows fra
   <https://github.com/Kozea/WeasyPrint/releases> (`weasyprint-windows-onefile.zip`
   som ligger under "Assets" under latest release), ekstraher zip filen og putt `weasyprint.exe` i
   en ny mappe med navn `tools` inne i `dict-sme`.

4. Restart XML Mind.


### Linux
1. Lag en lenke fra `xxe/` mappa til XML Mind sin `addon` mappe. Fyll inn riktig sti til
   `xxe/` mappa. 

    ```sh
    ln -s "~/FYLL-INN/dict-sme/xxe" ~/.xxe11/addon/dict-sme
    ```

2. For å kunne lage PDFer, installer programmet WeasyPrint
    ```sh
    sudo apt install weasyprint
    ```

3. Restart XML Mind.
