Redigerengiehtagirji
====================

## VIKTIG:

- Perfectionism is a killer, godt nok er godt nok.
- Noen ganger gjør man suboptimale valg, det må man leve med. (Se punkt 1)
- Feir milepæler: antall ord, ferdige bokstaver, publiseringer etc.

Skriv ned her etter kvart.

## REDAKSJONSSPRÅK

Hvor puristisk skal ordboken være?
F.eks: Kan amas fungere som subjunksjon (amas eai bora), eller skal vi holde på at det er nektende supinum (amasat borrat)?

**Konklusjon:**
Ordboken har vestlige former i definisjoner og eksempelsetninger.
t.d. aktio essiv *-me*
Lemma kan være alle dialektformer.
Vi har litt konservativt språk i eksemplene

***
***

## KILDER

Det kan være lurt å legge til info om hvor man har funnet en oversettelse, definisjon, etc., spesielt hvis man er litt usikker. Legges til under source, f.eks. etternavn + årstall på utgivelse.

Skal dette være en regel???

***
***
## LEMMA

### Lemmautvalg
Gruppering? (slik at en ikke trenger logge hvert enkelt ord)

SME-> NOB viser bare den vanligste varianten (= lemma) slik som det er nå.

**Konklusjon:**
Ulike variantformer i samme oppslag, i SME f.eks. universitehta (subst.), universiteahtta (subst.) i samme oppslag. Legges inn som variant av lemma, med vN for å kunnne gi riktig bøyningsparadigme. v1 er default for lemma. Dvs at v1 er optional i genereringa, mens v2 osv. er obligatoriske.

    <lg>
      <l pos="N">universitehta</l>
      <l var="v2" pos="N">universiteahtta</l>
    </lg>


## "Uheldige" ord


### Feil bruk av ord?
i ordbøkene oversatt som manus/manuskript, til forskjell fra giehtačála (håndskrift).
Men det er mange eksempler i korpus der det er brukt med betydninga håndskrift.


#### giehtačálus / giehtačála

for giehtačálus

1. definisjon av tydinga "manuskript"
2. (no og då brukt i tydinga "handskrift" -- definisjon) Geavat baicce giehtačála


Admin:
>Olgešspálttas gávnnat skoviid maid sáhtát čállit olggus ja deavdit giehtačállosiin dehe deavdit njuolga dihtoris .
geavahit bustávaid ja geahččaladdat sániiguin , iežas giehtačállosiin ja dihtoriin
Oahppit sáhttet čállit fáttá birra juogo giehtačállosiin dahje dihtorii .
Čállit iešguđetlágan teavsttaid giehtačállosiin ja dihtoriin
sáhttá ávžžuhit jearahallama čađahit almmá atnit giehtačállosa veahkkin .

>Non fiction:
Lea muhtumin leamaš váttis dulkot giehtačállosa, ja danin eat leat nagodan bájuhit visot ollásit .
čállit sániid dahje álkes teavstta govaide giehtačálusin dahje tastaturan

>fiction:
Mu šliettihan gieđat vuoiŋŋastedje giehtačállosa alde ja jorgaledje ain gulul dego niegus siiddu .
Lea got oaidnán ahte ii lean eatni giehtačálus?

>news:
Giehtačálus reivves lea maid hui fiinnis .
De maid garvit dan ahte namat čállojit boastut go lea váttis ipmirdit giehtačállosa, ja dat dáhpáhuvva dávja .
Čáppa giehtačállosiin, fiidnámus reivebáhpiriin , son ovdanbuktá sávaldagaidis iešguđetlágan olbmuide .

**Konklusjon:** For å markere at et ord er "uheldig":

- element `l_pref` (lemma_preferred) som dukker opp i grensesnittet om 'geavat baicce' (= bruk heller)

Hvis man er usikker på om man skal legge til `l_pref` eller ikke, så kan man legge til en kommentar i xml.

***
***

#### nolla - bare numeral?

Er nolla/nulla bare numeral?

	Lean duhtavaš go doallat nulla, čiekčan livččii sáhttán mannat goappeš guvlui.


Samme med miljárda, miljovdna, duhát osv.
I BOB er f.eks. "tusen" både substantiv og kvantor.

**Konklusjon**: Disse numeralene kan legges inn i substantiv-fila også. De må da også legges inn i analysatoren.

### sammensetninger:

- áddjá, eadni, jna.
- eadni: eatnibellodat, eatniorganisašuvdna,

**Konklusjon:**
(hvis produktivt): brukt som forledd..., pluss eks
*geavahuvvo goallossániid mearusin ....*


### noaord, tabuord:
áddjá: guovža (buddosnamma - tabuord)

**Konklusjon:**
    áddjá: guovža som egen <mg>




#### oktonaseadni, muhto oktováhnen

```
SIKOR:
oktonaseadni: 1
oktoeadni: 3
oktonasáhčči: 0
oktoáhčči: 2
oktonasváhnen: 1
oktováhnen: 35+
```

**Konklusjon**: Ja, legge til i smenob + synonym begge veier.

Det er kanskje forskjell på hvordan ordene brukes på norsk vs. finsk side.

Det kan også være forskjell på hvordan et ord faktisk brukes vs. hva Giellagáldu har normert.

Hvis den ene er tvilsom, kan man vurdere å innføre 'bruk heller'-element, ala `l_ref` som gir 'se også'.

Disse tingene bør diskuteres når det dukker opp slike ord.

***
***

## Språklig variasjon i lemma og betydning

**Konklusjon:**
Vi bruker to parametre, som attributter:

- Dialektvariasjon (østlig, vestlig, tornesamisk, sjøsamisk)
- Variasjon mellom ulike administrative organisasjoner (land Norge, Sverige, Finland)

Vi må bli enige om attributtene.???

Hvordan evt. merke synonym: *áhkku - muore* (dialekt, ganske ulikt)

***
***


## Synonymer og antonymer

### synonymer

Når skal man legge til synonymer? Hvor like (evt. ulike) må ordene være?

1. nolla - nulla (ort.) --> ikke synonym, men ortografiske varianter
2. buđetnjuvddus - buđetmeastu  --> bør sette inn synonym
3. čalbmálagaid - njunnálagaid --> bør være synonym
4. árga - árgabeaivi --> bør sette inn synonym
5. áhkku - muore (dialekt)


**Konklusjon**: Reint ortografiske forskjellige ord skal ikke legges inn som synonym. Dialektalt ulike ord bør heller ikke legges inn som synonym. Man kan tenke på det slik: ville jeg brukt ord2 istedenfor ord1 for å variere språket?

### antonymer

Hvordan begrense?

Flere typer antonymer. Hva skal være med? Her fra Fjeld og Vikør 6. kap:
- kontradiktorisk motsetning (enten/eller), f.eks. gift ugift
- kontrær motsetning,
	- artsmotsetning, f.eks. mann kvinne, hane høne
	- gradsmotsetning, de kan sammenliknes, f.eks. varm kald, tom full
	- konvers motsetning, to forskjellige perspektiver på samme sak, f.eks. kjøpe selge, gi få, mor barn, ektemann hustru
	- kompletterende motsetning, handling som naturlig følges av en annen, f.eks. spørsmål svar, angrep forsvar, snakke lytte

***
***

## Avledninger

### Informasjon om avledning

**Konklusjon:**
Vi gir informasjon om at lemma er en avledning slik i lemmagroup lg i elementet orig:
*borrat + suorggis -dit*   (med lenke)

### Homonymi med forskjellige avledninger

Hvis det er homonymi mellom to forskjellige avledninger, skal det føres som to forskjellige lemmaer eller som to betydninger (mg)?

Eks.

- *borahit* (kausativ, tar objekt, betyr å gi andre mat)
- *borahit* (refleksiv, tar ikke objekt, betyr å spise på seg selv)

I andre samiske ordbøker behandles disse som to lemmaer

For begge vil opphav være *borrat + suorggis -hit*
Hvis man på et seinere tidspunkt ønsker å gå mer informasjon, evt lenke til avledningstypen, vil det ikke være det samme for disse to, og det kan også være et argument for å føre dem som to lemmaer.

**Konklusjon:**
???



***
***
## DEFINISJONER

Realdefinisjon + eventuelle synonym

- Unngå 2.person i definisjonene
- Unngå skråstrek

### Parentes
Man kan bruke parentes i definisjoner for å vise til noe prototypisk men som ikke er obligatorisk, f.eks:

*(njealječiegat) breahtta dahje pláhta mii geavahuvvo lávdespeallamii*

Enn så lenge de samiske definisjonene ikke vises på nettsida:
Hvis et ord har flere dg-er i sme, legg også til dt (oversettelse til norsk). Dette for å unngå forvirring om hvorfor et ord er listet opp flere ganger i ordboka.

### samme definisjon

f.eks.

- guovttebearašásodat: viessu mas leat guokte ássanovttadaga
- guovttebearašviessu: viessu mas leat guokte ássanovttadaga

Skal definisjonen gjentas?

i BOB er det gjort slik: *tomannshus* har bare en lenke til *tomannsbolig*

**Konklusjon**: Ja, definisjonen gjentas med mindre ordet bør "frarådes" å bruke. I så fall lenker man til det andre ordet.


## MØNSTER FOR DEFINISJONER

### Tallord-artikler
- čieža = vuođđolohku 7; sju

#### Ordenstall

viđat: nummir 5 muhtun ortnega mielde

#### Samlingstall

golmmas: golbma olbmo

### oaniduvvon

"oaniduvvon" kan brukes som på norsk "forkortet":

miljovdna:

	vuođđolohku 1 000 000, oaniduvvon milj.

### Gjennomsiktighet i definisjoner

F.eks. váldorollaneavttár (fra mest til minst gjennomsiktig):

1. olmmoš gii neaktá deháleamos rolla filmmas...
2. olmmoš gii neaktá váldorolla filmmas...
3. neavttár geas lea váldorolla filmmas...


**Konklusjon**: Sammensatte ord: man trenger ikke å definere hvert av ordene på nytt.

Nummer 3 er nok best i dette tilfellet.

***
***

## Referere til andre ord
For eksempel jamfør og til forskjell fra... på norsk,

På samisk geahča eller gč., evt. jamfør = vrd. + komitatiiva (= veardádala)

Eller legge til i l_ref?

mii earuha + LOK (til forskjell fra) ??
evt. mii fas earuha + AKK + LOK

Eks:

- .. mii fas earuha giehtasealggi giehtaváimmus
- motsatt...f.eks. høyre/venstre - nuppegežiid?

som forledd/etterledd (mearusoassi/vuođđooassi) i ord som ...



### Adjektiv

**Konklusjon**: greit å bruke relativpronomen mii/gii i definisjoner. Det er det vi har blitt enige om per nå.

Noen eksempler på definisjoner:

- alitčalmmat: geas leat alit čalmmit
- guhkedáleš: mii lea guhkit go govdat



### Fargeord

Definisjonene trenger ikke å være så tekniske. Dette holder for 'rødt' f.eks.:
mas lea ivdni mii sulastahttá vara; okta vuođđoivnniin

Man trenger heller ikke å skrive hva de ulike fargene symboliserer.


### Kvinnelig og mannlig
Nissonlaš og almmáilaš brukes i ordboka. Eks:
nissonlaš/almmáilaš stáhtaoaivámuš

### biegga

máttabiegga: biegga mii bossu/boahtá máddin

biegga mii boahtá máttil

máddin kan bety både *sørfra* og *sørpå*. Hvordan få frem at det er *sørfra* som menes?

**Konklusjon**: skrive "biegga mii boahtá máttil". máttil betyr "fra sør", men ifølge Sammallahti kan det også bety "i sør", så ikke helt entydig der...


## FLERE BETYDNINGER (mg)

### I hvilken rekkefølge skal ulike betydninger være?

**Konklusjon:**
Etter semantikk, grunnbetydninga først, med mindre den er misvisende for brukeren

### metaforisk, abstrakt betydning

På norsk ofte "i overført betydning".

Hvordan markere det? Formulering...
Skal det være i re?

Forslag:
- sirdojuvvon mearkkašupmi/mearkkašumis
- abstrávtalaččat
- figuratiivvalaččat


F.eks. njealječiegat:

1. mas leat njeallje čiega ja njeallje siiddu

2. eahpenjuovžil

Først konkret betydning, så den abstrakte.

**Konklusjon**: Vanskelig å vurdere hvordan man skal begrense når det skal markeres og når ikke. Når det gjelder formulering, ikke bestemt enda.
Risten legger til kommentar ("overført") i XMLmind på de ordene der det er aktuelt å markere overført betydning. Da kan man enkelt finne de ordene i ettertid hvis man har lyst til å legge inn markering på dem.

### reŋgot

reŋgot: bargat reaŋgan // (trans.) bargat reaŋgan, omd: reŋgot badjeolbmuid

skal det være to mg'er?

**Konklusjon**: Ja, to mg'er. Spørsmålet er i hvilken rekkefølge mg'ene skal være. Den trans. betydninga er helt klart mest frekvent i SIKOR. Men hvis man følger "enkelhets" prinsipp, så intrans. først, så trans. Slik er det også gjort i Konrad Nielsen.
Så grunnregelen blir at man har den intransitive betydninga som mg1, med mindre man har noen gode grunner til å ikke gjøre det slik.


***
***

## EKSEMPELSETNINGER

### Formelt
**Konklusjon:**
- Fullstendige setninger starter med stor bokstav, avsluttes med tegnsetting (punktum, spørretegn)
- Ufullstendige setninger med liten bokstav, uten tegnsetting
- Unngå parentes i eksempelsetninger (med mindre bruken er naturlig slik som i "Alimusriekti juohkásii eanetlohkun ja unnitlohkun (9–6).")
- Eksempelsetningene bør være selvstendige setninger, ikke peke til noe utenfor setningen.
F.eks.: *De álggii nieida vuoiddadit. => Nieida álggii vuoiddadit.*


### Språkleg
**Konklusjon:**
- Gjerne autentiske, men de bør kuttes ned, fjerne 'støy' i setninga
- Første eksempelsetning bør være typisk bruk av ordet
- Vis reksjon, bruk substantiv for å vise kasusbruk
- Bruk generiske substantiv (gutten, dama...) og pronomen, ikkje eigennamn
- Bør være nøytrale: Unngå stedsnavn, religion, visse grupper - stigmatisering, stereotyper, etc
- for man/en: bruk f.eks. *olmmoš, dievdoolmmoš, nissonolmmoš*


Videre bør alle ord som er brukt i eksempelsetninger (og definisjoner) være med i ordboka. Legg derfor til ord hvis du ser det mangler.


## Tallord
- Diibmu lea čieža. = Klokka er sju.
- osb.
- Eksempel med alder, klokke og liknende

## OVERSETTINGER AV EKSEMPLER


### Hvor idiomatiske skal oversettelsene være?

*Son guovlala giikkáriin oidnojit go lottit.* Hvordan oversette?

- Hun ser i kikkerten om det er fugler å se. - idiomatisk oversettelse
- Hun ser i kikkerten om fuglene er synlige - nær samiske setning
- Hun ser i kikkerten om fuglene vises. - nær samiske setning

Duorastaga dievai kulturviessu maŋimuš stullui.
- På torsdag var det ikke et ledig sete i kulturhuset.
- På torsdag fyltes kulturhuset til siste sete.

**Konklusjon:**

- I samisk-norsk ordbok bør nob-oversettelsen være nært den samiske setninga, men likevel fungere på norsk.
- Vi bør ha noen til å korrekturlese den norske oversettelsen.

***
***

## IDIOMATISKE UTTRYKK OG ORDTAK

### Ord og uttrykk som har idiomatiske versjoner på begge steder
Ordtak og idiomatisk uttryk bør stå på begge språk med den idiomatiske versjonen, td.
grav (subst.) = (subst.) hávdi

(i bibeloversetting, egentlig grop) (subst.) *roggi*
**Konklusjon:**
Her er det problemer med md-formatteringa:
      <ig>
      <i>Dat gii goaivu rokki, gahččá ieš dasa.</i>
      <id>definišuvdna...</id>
      <td>Den som graver en grav, faller selv i den.</td>
      </ig>

### Ord og uttrykk som bare finnes i et språk

OBS: Dette må vi beskrive...

### Iežas dat ferte gámadit.

mo jorgalit dárogillii?

Mearkkašupmi: Olmmoš ferte ieš birget iige galgga vuordit ahte earát veahkehit.

Det er forskjell på om man er i smenob eller nobsme:

i smenob: bare oversette/forklare idiomet til norsk
i nobsme: da kan man lete etter parallellen/ekvivalenten

### idiomer, faste uttrykk

Når skal det under idiomer og når bare under eksempel?

EKS....

***
***
## SLEKTSKAPSTERMER

###  vilbealle, oambealle: vuosttaš, nubbi, goalmmát
hvor skal disse forklaringene legges?

ig? xg?

sivjjot (svigerinne): eamida oabbá (= konas søster)
(jus lea dievdu) vielja eamit (= (og hvis man er mann) brorens kone)

### likekjønnet ekteskap

Naba oappá eamit? mo dalle? (= hva med søsters kone? bruker man samme ord da?)

**Konklusjon:**
må spørre noen som vet

máhka, spile....

### Kjønnsspesifikke eller -uspesifikke termer

- eatni dahje áhči - váhnema?
- eamida dahje isida - beallelačča/náittosguoimmi/eallinguoimmi?

**Konklusjon:**
váhnen og eallinguoibmi

### tilkommende/sássa

mo dadjat sámegillii?

vivvasássa: tilkommende svigersønn

boahttevaš?? Se i korpus

olmmoš gii goas nu šaddá olbmo vivva? ... geas lea áigumuš šaddat...
olmmoš gii vurdojuvvo/áigu/galgá šaddat olbmo vivvan

**Konklusjon**: olmmoš gii áigu šaddat olbmo vivvan

### oabbá mg2

oabbá lea definerejuvvon ná dál:
mg1: nieida dahje nisu geas lea seamma áhčči dahje eadni go nuppi olbmos

Muhto das lea goit nubbi mearkkašupmi:

Min eamiálbmot	oappát	ja vielljat eará guovlluin máilmmis eai leat buohkat seamma dilis .

min iežamet girjjálašvuođa	oappáin	ja vieljain ...


BOB: kvinne sett i forhold til den eller dem hun har religiøst fellesskap med

NAOB: kvinne (sett i forhold til andre kvinner)

BOB ("bror"): særlig i flertall: mann eller folk i forhold til person(er) av andre nasjoner eller til person(er) med felles interesser;

**Konklusjon**: skrive noe a la BOBs bror mg2.

oabbá mg2: nissonolbmot daid ektui geain lea seamma/oktasaš beroštumit dahje ...

### perspektiv i def

F.eks.:

boadnji: náitalan dievdu / almmáilaš náittosguoibmi

***
***
## DIVERSE NOTATER, bør redigeres eller fjernes

### Referere til et annet ord i definisjon, og dermed ikke gjenta definisjonen

F.eks. bivttastit mg2:

gárvodit

**Konklusjon**: Skrive definisjonen også ..., og eventuelt legge til synonym.

coggat biktasiid iežas dahje nuppi ala

Samme med:
submet: adderet

### bihkkadit

Legge til mg2?

svartmale?

KN: sverte, utmale verre enn fortjent; smøre tykt på, overdrive, lyve

Fant ett eksempel på dette i SIKOR:

muhto sátnejođiheaddji Sæther ii hálit	bihkkadit gieldda dili dan_dihtii.

**Konklusjon**: Legge ordet i en liste, så kan man spørre flere om ordet brukes slik.

Et annet spm er om man skal legge til eksempler, ord som ofte brukes med verbet:

vuoidat bihkain (omd. fátnasa ja sabehiid)


### skuvla

I hvilken rekkefølge bør definisjonene være? Synes det er vanskelig å vurdere hvilken som er "grunnbetydninga".

nuoraidskuvla:
1. gávccát gitta logát ceahki vuođđoskuvllas
2. nuoraidskuvlla visti


### Skal alle varianter legges til i ordboka?

For eksempel:

```
	gáfegohppu
	gáffegohppu
	káffegohppu
	gáffekohppa
	káffekohppa
osv.
```

Her er det også et poeng at f.eks. *káffegohppu* blander to dialekter, *káffe* og *gohppu*. Bør det "frarådes" eller gi error i analysatoren?

et annet eksempel:
```
	iđitgáffe
	iđitgáfe
	iđitkáffe
	iđitkáfe
```

**Konklusjon**: det bør være mulig å søke på alle lemmaene. Spørsmålet er hvordan det skal gjøres.

Gjøre det som i BOB? Der får man alle variantene opp når man søker på et ord. Men variantene er i samme artikkel. Se f.eks. *høytlønnet*.

ođđa noda `lset` = lemma set. Jos lset de čajet dan, muđui čájet l.

`l_ref` "se":

ordbokene:

kvensk ordbok:


### mihttoovttadagat

Hva er forskjellen mellom grunnenhet og målenhet? Hvordan få frem den forskjellen?

vuođđoovttadat (grunnenhet): definerejuvvon ovttadat mii geavahuvvo vuođđun man nu mihtideapmái, omd. mehter guhkkodaga mihtideapmái, sekunda áiggi mihtideapmái

dk: (FYSIK) enhed for måling som alle andre enheder i et bestemt målesystem bygger på fx meter, kilogram eller sekund

mihttoovttadat mii lea

mihttoovttadat (målenhet):

definerejuvvon ovttadat mii geavahuvvo vuođđun man nu mihtideapmái, omd. mehter guhkkodaga mihtideapmái, sekunda áiggi mihtideapmái

lossodatovttadat (lengdeenhet): mihttoovttadat mii geavahuvvo mihttidit lossodaga


### ovtteš, guvtteš, golmmeš jna.

Mo daid defineret?

- BOB: noen som har (start)nummer fem
- NAOB: størrelse med tallverdi 5 ; sifferet 5
- DK: person, genstand el.lign. der har nr. 5 i et bestemt system fx en buslinje
- SE: siffran 5


### birra(n)beaivi

Finnes som substantiv i ordboka. Lurer på om det også er et adjektiv/adverb? Noe av bruken kan tyde på det:

[...] ja ii guhtege ásahus sáhte fállat sámegielat bálvalusa	birranbeaivvi	.

[...] lea dál áidna	birrabeaivve	dikšofálaldat sámemánáide Norggas .

Ođđa muitosadji galgá leat olámuttos birranbeaivvi


**Konklusjon**: vente litt med å eventuelt legge til som adj/adv i ordboka, ettersom det ikke er så mange eksempler på det. Sjekk igjen når vi får nytt korpus. Det finnes heller ikke i andre ordbøker. Kan legges til "ventelista".


### Flere forklaringer i én definisjon

F.eks. miljárda:

	vuođđolohku 1 000 000 000, duhát miljovnna, oaniduvvon mrd.

Og i så fall, hvilket skilletegn skal man ha mellom definisjonene? Semikolon?

**Konklusjon**: semikolon er greit.

"oaniduvvon mrd." er en tilleggsopplysning. Et eget element eller attributt for å legge inn forkortelser?


### adjektiver definisjoner formulering

**Konklusjon**: greit å bruke mii/gii i definisjoner.

- alitčalmmat: geas leat alit čalmmit
- guhkedáleš: mii lea guhkit go govdat



Hadde også vært interessant å ta dette opp med Klara Sjo. Se f.eks. frekk, vennlig... i BOB.

### gii/guhte

olmmoš gii.../olmmoš guhte...


### avledninger

Må diskuteres.

F.eks. hvordan få frem forskjellen mellom arvigoahtit, arvát, arvváskit...

1. Hvordan få frem forskjellene i betydning
2. Morfologien
3. Referering til andre ord. Hvis man søker på "arvit" skal man da få opp "arvát"? Alle arvit-ordene?


arvát er ikke helt det samme som arvigoahtit. Mulig definisjon:

arvát: álgá arvit, dihto dáhpáhusa birra
arvigoahtit: arvi álgá dahje arvvit álget


Bør ha eget dokument for avledninger.

### čuohtenáre

čuohtenáre - virker som det er brukt både om "ca. 100" og "hundrevis", men "ca. 100" ser ut til å være den primære bruken. Bør begge betydningene legges til i ordboka?

Noen eksempler fra korpus:

> Jiehkit, uđđasat ja eará geologalaš proseassat leat čuohtenáre duháhiid jagiid mielde hábmen eanadaga.

> Ealli guollebivdohápman čuohtenáre jagiid

> Biedjovákkeguovllus ledje gottit duháhiid jagiid ja (lojes) bohccot fas leat leamašan čuohtenáre jagiid.

> Eará videoid, maid Evelina láve juohkit, leat sullii čuohtenáre olbmo geahččan

> Vuosttaš logenáre jagiid geavahedje dáid dietnasiid eanaš dađistaga jahkásaš


**Konklusjon**: Legg først og fremst inn betydninga som er dokumentert i andre ordbøker. Hvis den andre bruken er omfattende så kan man vurdere å legge det inn med re: (i nyere betydning).
