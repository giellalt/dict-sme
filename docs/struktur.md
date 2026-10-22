xml-strukturen og terminologien vi bruker
=======================


&lt;e&gt; : **entry** - Hovedelementet med all informasjon til hvert lemma.
Homonyme lemmaer som ikke har samme opprinnelse, skal ha egne entryer.  F.eks. 
- <i>vuovdi-vuovddit</i> (skog) og <i>vuovdi-vuovdit</i> (selger), 
- <i>vuorru-vuorut</i> (omgang) og <i>vuorru-vuorrut</i> (fisk). 
- Også homonymer som har samme morfologi, f.eks. <i>busse-busset</i> (buss) og <i>busse-busset</i> (pose)).
 
&lt;lg&gt; : **lemma group** med informasjon om **pos** (Part of Speech)
- &lt;l&gt; : lemma, og **type** hvis nødvendig.
- &lt;l&gt; : evt. flere lemmaer med ortografiske varianter av lemmaet, f.eks. vil  <i>girku kirku</i> være to lemmaer i samme lemma group

I &lt;l&gt;  legger vi til attributt, **type** eller **hid**, for å skille mellom homonyme lemmaer som har hver sin entry: 
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


