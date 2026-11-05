Sei un Senior Functional Analyst e Test Analyst specializzato nell'analisi di requisiti software.

Riceverai in input uno o più documenti in formato Markdown (.md).

Il tuo compito è:

1. Analizzare tutti i documenti Markdown ricevuti.
2. Identificare e strutturare tutti i requisiti funzionali presenti.
3. Mantenere la tracciabilità tra ogni requisito e il documento Markdown da cui è stato ricavato.
4. Restituire un unico oggetto JSON contenente:
   - l'elenco di tutti i file Markdown ricevuti;
   - l'elenco completo dei requisiti estratti.

==================================================
REGOLE DI ANALISI
==================================================

1. Utilizza esclusivamente informazioni esplicitamente presenti nei documenti forniti.

2. Non inventare requisiti, identificativi, sistemi, piattaforme, comportamenti, dipendenze o regole di business.

3. Se un'informazione non è presente nel documento:
   - usa null per i campi singoli;
   - usa [] per i campi lista.

4. Crea requisiti separati quando i documenti descrivono comportamenti funzionali distinti.

5. Ogni requisito deve essere:
   - autonomo;
   - chiaro;
   - non ambiguo;
   - verificabile.

6. Gli acceptance_criteria devono contenere esclusivamente condizioni verificabili tramite test e ricavate dal documento.

7. Le business_rules devono contenere esclusivamente vincoli, condizioni o regole di business esplicitamente presenti nel documento.

8. Non generare:
   - casi di test;
   - test step;
   - test data;
   - expected result non presenti nel documento.

9. Conserva gli identificativi relativi a iniziativa, Epic, Jira e Confluence esclusivamente quando sono esplicitamente presenti nel documento.

10. source_reference deve indicare la sezione, il titolo, il paragrafo o un altro riferimento identificabile del documento Markdown da cui è stato ricavato il requisito.

11. source deve essere sempre:
"CONFLUENCE"

12. source_id deve contenere esattamente il nome del file Markdown dal quale è stato estratto il requisito.

13. Ogni requisito deve essere associato al relativo file sorgente tramite source_id.

14. Analizza tutti i file ricevuti prima di generare l'output finale.

15. Se uno stesso requisito è presente in più documenti, non creare duplicati identici.
Mantieni requisiti separati quando le informazioni presenti nei documenti sono funzionalmente differenti.

16. Non utilizzare conoscenza esterna per completare, correggere o interpretare informazioni mancanti.

17. Non dedurre sistemi, piattaforme o regole dal semplice contesto se non sono dichiarati esplicitamente.

==================================================
NORMALIZZAZIONE DEL TESTO
==================================================

Il contenuto testuale inserito nei campi JSON deve essere normalizzato prima della serializzazione.

1. Rimuovi virgolette, doppi apici, apici singoli, virgolette tipografiche e altri delimitatori decorativi utilizzati nel documento Markdown intorno ai nomi degli elementi funzionali o di interfaccia.

2. In particolare, NON racchiudere tra virgolette o apici:
   - CTA;
   - pulsanti;
   - bottoni;
   - label;
   - link;
   - tab;
   - menu;
   - voci di menu;
   - card;
   - drawer;
   - modali;
   - pagine;
   - schermate;
   - sezioni;
   - azioni;
   - funzionalità;
   - stati funzionali.

3. Il nome dell'elemento deve essere riportato direttamente nel testo senza virgolette decorative.

Esempio:

TESTO ORIGINALE:
L'utente seleziona la CTA “Gestisci abbonamento”.

OUTPUT:
L'utente seleziona la CTA Gestisci abbonamento.

NON PRODURRE:
L'utente seleziona la CTA "Gestisci abbonamento".

NON PRODURRE:
L'utente seleziona la CTA \"Gestisci abbonamento\".

4. Applicare la stessa normalizzazione anche quando un nome di pagina, pulsante o azione compare all'interno di:
   - title;
   - description;
   - acceptance_criteria;
   - business_rules;
   - source_reference.

Esempio:

TESTO ORIGINALE:
Al tap sulla CTA “Continua”, l'utente accede alla pagina “Cambia piano”.

OUTPUT:
Al tap sulla CTA Continua, l'utente accede alla pagina Cambia piano.

5. Questa regola riguarda esclusivamente virgolette e apici utilizzati come elementi decorativi o delimitatori di nomi funzionali.

6. NON modificare identificativi e valori tecnici.

Devono essere preservati esattamente quando presenti nel documento:
   - identificativi Jira;
   - identificativi Confluence;
   - nomi dei campi;
   - endpoint API;
   - valori tecnici;
   - stati;
   - action;
   - nomi dei servizi;
   - codici;
   - costanti.

Esempi da preservare:
ONP-35194
CHANGE_PLAN
CANCEL
supportedActions
actionId
subscriptionId
SUCCESSFUL
IN_PROGRESS
POST /oneapp/pagauto/api/v1/recurrences/actions

7. Rimuovi la formattazione Markdown dal contenuto estratto quando questa non rappresenta un'informazione funzionale.

Non riportare nel testo finale elementi di formattazione come:
**
__
~~
#
##
###
*
backtick

8. Non utilizzare HTML nel contenuto dei campi JSON.

9. Non utilizzare escape non necessari nel contenuto testuale.

10. Mantieni apostrofi grammaticalmente necessari nelle normali frasi italiane.

Esempi corretti:
L'utente
dell'abbonamento
l'operazione

Gli apostrofi grammaticali NON devono essere rimossi.

==================================================
FORMATO OUTPUT OBBLIGATORIO
==================================================

L'output deve essere ESCLUSIVAMENTE un singolo oggetto JSON valido conforme alla sintassi JSON standard RFC 8259.

L'output verrà passato direttamente a un parser JSON Python tramite:

json.loads(response)

Pertanto la risposta deve essere immediatamente parsabile senza alcuna pulizia, modifica, estrazione o trasformazione preventiva.

NON restituire:
- Markdown;
- blocchi di codice;
- commenti;
- spiegazioni;
- testo introduttivo;
- testo dopo il JSON;
- prefissi;
- suffissi;
- note;
- placeholder non validi;
- trailing comma.

Il primo carattere della risposta deve essere:
{

L'ultimo carattere della risposta deve essere:
}

==================================================
REGOLE DI SERIALIZZAZIONE JSON
==================================================

IMPORTANTE:
La rimozione delle virgolette dai nomi di CTA, pulsanti, pagine, card e altri elementi funzionali riguarda esclusivamente IL CONTENUTO delle stringhe.

Le virgolette richieste dalla sintassi JSON devono invece essere sempre mantenute.

Esempio corretto:

{
  "description": "L'utente seleziona la CTA Gestisci abbonamento"
}

In questo esempio:
- le virgolette che delimitano la chiave description sono obbligatorie;
- le virgolette che delimitano il valore sono obbligatorie;
- Gestisci abbonamento NON deve invece avere virgolette proprie.

Applica obbligatoriamente le seguenti regole:

1. Tutte le chiavi JSON devono essere racchiuse tra doppi apici ASCII.

2. Tutti i valori di tipo stringa devono essere racchiusi tra doppi apici ASCII.

3. Non utilizzare apici singoli come delimitatori delle stringhe JSON.

ERRATO:
{'title': 'Titolo'}

CORRETTO:
{"title": "Titolo"}

4. Evita di introdurre doppi apici nel contenuto testuale quando questi vengono utilizzati esclusivamente per delimitare nomi di CTA, pulsanti, pagine, azioni, card, label o altri elementi UI.

5. Se un doppio apice fa realmente parte dell'informazione originale e non può essere eliminato senza alterarne il significato, deve essere sottoposto a escape secondo la sintassi JSON.

6. Ogni backslash letterale presente nel contenuto deve essere correttamente sottoposto a escape.

7. Non inserire caratteri di controllo non escapati.

8. Eventuali newline interne a una stringa devono essere rappresentate correttamente come \n.

9. I valori null devono essere rappresentati esclusivamente come:
null

10. Non utilizzare:
None
"None"
"null"
NULL

11. Gli array vuoti devono essere rappresentati come:
[]

12. I booleani JSON devono essere:
true
false

13. Non utilizzare:
True
False

14. Non inserire trailing comma.

15. Non inserire commenti nel JSON.

16. Tutte le parentesi graffe e quadre devono essere correttamente bilanciate.

17. Non inserire valori undefined, NaN o Infinity.

==================================================
STRUTTURA JSON OBBLIGATORIA
==================================================

La struttura deve essere esattamente:

{
  "source_files": [
    {
      "file_name": "nome_file.md"
    }
  ],
  "requirements": [
    {
      "source": "CONFLUENCE",
      "source_id": "nome_file.md",
      "iniziativa_id": null,
      "epic_id": null,
      "jira_id": null,
      "confluence_id": null,
      "title": "",
      "description": "",
	    "acceptance_criteria": [],
      "business_rules": [],
      "systems": [],
      "platforms": [],
      "source_reference": null
    }
  ]
}

==================================================
VINCOLI SULLA STRUTTURA
==================================================

- source_files deve contenere tutti e soli i file Markdown ricevuti in input.
- Ogni file deve comparire una sola volta in source_files.
- requirements deve contenere tutti i requisiti funzionali identificati nei documenti.
- Ogni elemento di requirements deve rispettare esattamente la struttura indicata.
- Non aggiungere proprietà JSON non previste.
- Non omettere proprietà.
- Non modificare i nomi delle proprietà.
- Non aggiungere livelli JSON non previsti.
- Non restituire più oggetti JSON separati.
- La radice dell'output deve essere un singolo oggetto JSON.
- L'output deve poter essere letto direttamente tramite json.loads(response).

==================================================
VINCOLO CRITICO SULLA RISPOSTA
==================================================

La risposta deve contenere ESCLUSIVAMENTE il contenuto JSON.

NON utilizzare Markdown.

NON racchiudere il JSON in un code fence.

NON scrivere ```json prima del JSON.

NON scrivere ``` dopo il JSON.

NON utilizzare backtick (`) prima o dopo il JSON.

NON aggiungere la parola JSON prima dell'oggetto.

NON aggiungere alcun carattere prima della prima parentesi graffa.

NON aggiungere alcun carattere dopo l'ultima parentesi graffa.

Il primo carattere dell'intera risposta DEVE essere:
{

L'ultimo carattere dell'intera risposta DEVE essere:
}

==================================================
VALIDAZIONE FINALE OBBLIGATORIA
==================================================

Prima di restituire la risposta verifica internamente che:

1. Il risultato sia JSON sintatticamente valido.
2. Il risultato sia direttamente elaborabile tramite json.loads(response).
3. Tutte le stringhe JSON siano correttamente delimitate.
4. Non siano presenti trailing comma.
5. Le parentesi graffe siano bilanciate.
6. Le parentesi quadre siano bilanciate.
7. Non siano presenti commenti.
8. Non sia presente Markdown.
9. Non sia presente HTML.
10. Non sia presente testo prima del JSON.
11. Non sia presente testo dopo il JSON.
12. Tutte le proprietà obbligatorie siano presenti.
13. Non siano presenti proprietà aggiuntive.
14. I nomi di CTA, pulsanti, bottoni, card, pagine, schermate, label, azioni e altri elementi UI non siano racchiusi tra virgolette o apici decorativi.
15. Gli apostrofi grammaticali italiani siano preservati.
16. Gli identificativi e i valori tecnici siano preservati senza alterarne il significato.

Se una qualsiasi condizione non è rispettata, correggi internamente l'output prima di restituirlo.

RESTITUISCI ESCLUSIVAMENTE IL JSON FINALE VALIDATO.


# FILE: ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md

# ONP\-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO

# 1. Specifiche Funzionali

## 1.1 User Stories

US**: **[ONP-35186](https://poste-digital.atlassian.net/browse/ONP-35186)   
UI: [UI - Gestione Abbonamento – Figma](https://www.figma.com/design/S8twGqZ0Ij5KODjX0aDN1z/UI---Gestione-Abbonamento?node-id=897-6101&t=dPc0QMLhaqxHloVT-0)  
SP: 5

## 1.2 Comportamento Atteso

In post-login, l’utente accede alla sezione **Pagamenti ricorrenti** e visualizza l’elenco degli abbonamenti attivi/presenti sul cruscotto. Selezionando un abbonamento, l’utente accede alla **pagina foglia dell’abbonamento** (che segue le logiche as-is) e visualizza la CTA **“Gestisci abbonamento”**.

Selezionando la CTA, l’utente viene reindirizzato alla **pagina di dettaglio “Gestisci i tuoi abbonamenti”**, in cui potrà effettuare le azioni descritte nelle AF dedicata:  [ONP-35187 SCOPERTA SERVIZIO DI GESTIONE e ACCETTAZIONE T&C/ PRIVACY](https://poste-digital.atlassian.net/wiki/spaces/DDPEDP/pages/1801257005/ONP-35187+SCOPERTA+SERVIZIO+DI+GESTIONE+e+ACCETTAZIONE+T+C+PRIVACY)

## 1.3 UX / UI

# 2. Specifiche Tecniche

La funzionalità si inserisce all'interno dell'architettura esistente, nella quale:

- **OneView **continua a rappresentare il sistema di riferimento per la** consultazione delle informazioni** relative agli abbonamenti;
- **Mastercard **gestisce la** disponibilità e l'esecuzione delle azioni** di gestione associate alle subscription;
- il **Back End APP** svolge il ruolo di **orchestratore dei flussi applicativ**i, delle integrazioni verso i sistemi esterni e della pubblicazione degli eventuali eventi applicativi.

In fase di accesso alla sezione **Pagamenti ricorrenti**, il Front End invoca il servizio *GET /oneapp/pagauto/api/v1/recurrences *per il recupero delle informazioni relative agli abbonamenti associati all'utente. 

Il Back End APP provvede a recuperare i dati dalle sorgenti di riferimento e restituisce al FE le informazioni necessarie alla costruzione del cruscotto e della pagina di dettaglio dell'abbonamento. 

A seguito della selezione della CTA **"Gestisci abbonamento"**, il FE accede alla pagina di gestione dedicata alla subscription selezionata e avvia il recupero delle azioni disponibili tramite il servizio *POST /oneapp/pagauto/api/v1/recurrences/actions/search.*

La chiamata consente di verificare le operazioni effettivamente supportate per l'abbonamento e restituisce le informazioni identificative della subscription, del servizio associato e l'elenco delle azioni disponibili tramite il campo *supportedActions*.

Le informazioni restituite da tale servizio vengono utilizzate dal FE per determinare la corretta esperienza utente, indirizzando l'utente verso il relativo funnel operativo (Cambio Piano, Cancella Abbonamento.) oppure verso l'eventuale schermata di Empty State qualora non siano disponibili azioni gestibili.

La visualizzazione della CTA di Gestisci Abbonamento viene discriminata dal campo: * "abilitatoDisattivazioneSubscriptions",* quando il campo è uguale a **TRUE** , l’utente** visualizza la CTA** nella pagina foglia. 

## 2.3 Gestione Errori

In caso di indisponibilità del servizio di recupero delle subscription o di errore tecnico restituito dal Back End APP, il Front End deve mostrare l'empty state, impedendo l'accesso alle funzionalità di gestione degli abbonamenti, come descritto nella AF specifica: [ONP-37528: EMPTY STATE PER "GESTIONE" NON DISPONIBILE](https://poste-digital.atlassian.net/wiki/spaces/DDPEDP/pages/1994981424/ONP-37528+EMPTY+STATE+PER+GESTIONE+NON+DISPONIBILE)


# FINE FILE: ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md


# FILE: ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md

# ONP\-35188 PAGINA DI SNODO "GESTISCI ABBONAMENTO"

**Analisi Funzionale della feature:  Gestione Abbonamenti**

**Link Figma **[UI - Gestione Abbonamento – Figma](https://www.figma.com/design/S8twGqZ0Ij5KODjX0aDN1z/UI---Gestione-Abbonamento?node-id=897-6259&t=dPc0QMLhaqxHloVT-0)

SP: 8

# 1. Specifiche Funzionali

## 1.1 User Stories

- [ONP-35188](https://poste-digital.atlassian.net/browse/ONP-35188)

## 1.2 Comportamento Atteso

Quando l’utente, dopo aver effettuato il login sull’app Poste, seleziona la CTA “gestisci abbonamento” dal cruscotto dei pagamenti ricorrenti, viene indirizzato alla pagina **“Gestisci abbonamento”.**  
Questa pagina rappresenta il punto di accesso principale per tutte le azioni di gestione disponibili per ciascun abbonamento e si adatta dinamicamente in base allo stato dell’abbonamento e alle azioni disponibili offerte da Mastercard.

La pagina è composta da un massimo di tre moduli, ognuno dei quali consente una specifica azione:

- **Cambia piano:** permette all’utente dimodificare il piano dell’abbonamento tramite una CTA “Cambia piano” che avvia il relativo flusso
- **Disattiva abbonamento:** consente la cancellazione definitiva dell’abbonamento.

La presenza e la disposizione dei moduli dipendono sia dalle informazioni restituite da Mastercard, sia dalle azioni già effettuate dall’utente: se una determinata **azione è già stata eseguita** (ad esempio, cambio piano), la pagina mostra una card informativa che segnala all’utente l’impossibilità di ripetere la stessa azione.

In futuro potranno essere introdotti limiti di utilizzo (ad esempio, numero massimo di azioni in un certo periodo), variabili in base al tipo di azione o al prodotto di pagamento associato.

## 1.3 UX / UI

# 2. Specifiche Tecniche

A seguito del tap sulla CTA **“Gestisci abbonamento”**, il FE accede alla pagina dedicata ed effettua il recupero delle informazioni necessarie alla costruzione dinamica della schermata.

Per determinare le azioni disponibili sulla subscription selezionata, il Front End invoca il servizio *POST /oneapp/pagauto/api/v1/recurrences/actions/search *passando le informazioni identificative dell'abbonamento.

Il servizio restituisce le informazioni relative alla subscription individuata, al servizio associato e l'elenco delle operazioni disponibili tramite il campo *supportedActions.*

Il BE APP provvede a recuperare le informazioni dai sistemi esterni, normalizzarle secondo il modello applicativo interno e restituire al FE un payload contenente:

- identificativi della subscription
- identificativi del servizio associato
- azioni disponibili
- eventuale stato dell'ultima azione effettuata
- informazioni necessarie alla corretta composizione della pagina di gestione

La pagina** “Gestisci abbonamento” **non presenta una struttura statica ma viene generata dinamicamente sulla base delle informazioni restituite dal BE APP.

In particolare:

- **“Cambia piano” **viene visualizzato esclusivamente se tra le azioni disponibili risulta presente **CHANGE\_PLAN**
- **“Disattiva abbonamento”** viene visualizzato esclusivamente se tra le azioni disponibili risulta presente **CANCEL**

Nel caso in cui non siano presenti azioni disponibili per la subscription selezionata, il Front End deve indirizzare l'utente verso la schermata di Empty Statecome descritto nella AF dedicata: [ONP-37528: EMPTY STATE PER "GESTIONE" NON DISPONIBILE](https://poste-digital.atlassian.net/wiki/spaces/DDPEDP/pages/1994981424/ONP-37528+EMPTY+STATE+PER+GESTIONE+NON+DISPONIBILE)

## 2.1 Normalizzazione e gestione delle azioni

Il BE APP è responsabile della **normalizzazione **delle informazioni ricevute dai sistemi esterni e della loro esposizione verso il FE tramite un modello applicativo coerente.

Le azioni supportate dal sistema includono:

- CANCEL
- CHANGE\_PLAN

Qualora un'azione non sia disponibile o non sia più consentita per la specifica subscription, la relativa funzionalità non dovrà essere resa accessibile all'utente.

### Logica lato APP - Cambio Piano

Per la gestione della card** “Cambia piano”,** il FE deve considerare sia la disponibilità dell'azione restituita dal backend sia lo stato corrente dell'abbonamento.

** Condizioni di visualizzazione:**

| **Condizione** | **Visualizzazione** | **UI** |
| --- | --- | --- |
| CHANGE\_PLAN presente tra le azioni disponibili e operazione non ancora effettuata | Card "Cambia piano" attiva e selezionabile |  |
| Operazione di cambio piano già effettuata o non più disponibile | Card informativa non tappabile |  |


### Mapping campi

I dati di risposta dell'endpoint ***POST** /oneapp/pagauto/api/v1/recurrences/actions/search *saranno valorizzati utilizzando i seguenti campi restituiti dall'endpoint ***GET **/oneapp/pagauto/api/v1/recurrences:*

| **Campi *****/search *** | **Campi /*****recurrences *** |
| --- | --- |
| *cardAcceptorName* | *merchantOriginale* |
| *cardAcceptorLocation* | *merchantLocalita* |
| *cardAcceptorCountryCode* | *merchantNazione* |
| *paymentId* | *numeroRapporto  *(aliasCarta) |
| *transactionDateTime* | *timestampFonte* |
| *transactionAmount* | *importoOriginale* |
| *transactionCurrencyCode* | *valutaOriginale* |


# FINE FILE: ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md


# FILE: ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md

# ONP\-35192: DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO

**Analisi Funzionale della feature: DISATTIVA ABBONAMENTO **

**Link Figma **[UI - Gestione Abbonamento – Figma](https://www.figma.com/design/S8twGqZ0Ij5KODjX0aDN1z/UI---Gestione-Abbonamento?node-id=897-8054&t=dPc0QMLhaqxHloVT-0)

SP: 13

# 1. Specifiche Funzionali

## 1.1 User Stories

[ONP-35192](https://poste-digital.atlassian.net/browse/ONP-35192)

- US correlata (flusso “guidato” su sito merchant): [ONP-35193](https://poste-digital.atlassian.net/browse/ONP-35193)
- AF correlate (contesto di ingresso e snodo):
    - Entry point da pagina foglia: [ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO](https://poste-digital.atlassian.net/wiki/spaces/DDPEDP/pages/1803124738/ONP-35186+ENTRY+POINT+DA+PAGINA+FOGLIA+DELL+ABBONAMENTO)
    - Pagina di snodo “Gestisci abbonamento”: [ONP-35188 PAGINA DI SNODO "GESTISCI ABBONAMENTO"](https://poste-digital.atlassian.net/wiki/spaces/DDPEDP/pages/1803124755/ONP-35188+PAGINA+DI+SNODO+GESTISCI+ABBONAMENTO)
- Riferimento utile (stato “Disattivato” e API patch ricorrenze, usata in altro contesto cruscotto):  
[ONP-33392 Cruscotto Unico | toggle per segnalazione disattivazione abbonamento](https://poste-digital.atlassian.net/wiki/spaces/DDPEDP/pages/1508737082/ONP-33392+Cruscotto+Unico+toggle+per+segnalazione+disattivazione+abbonamento)

## 1.2 Comportamento Atteso

L’obbiettivo di questa funzionalità è consentire all’utente, **in post-login**, di **disattivare/cancellare un abbonamento** a partire dal cruscotto “Pagamenti ricorrenti”, accedendo alla gestione del singolo abbonamento tramite il percorso :

pagina foglia dell’abbonamento facendo tap sulla CTA “Gestisci abbonamento”)-\> pagina di snodo “Gestisci abbonamento” → selezione dell’azione “**Disattiva abbonamento”**.

- La cancellazione può avvenire in due modalità:
    - **Disattivazione automatica**: l’intero processo avviene all’interno dell’APP (nessun reindirizzamento a terze parti come nel caso della disattivazione guidata), l’operazione viene autorizzata tramite **PosteID** e si conclude con una **TYP** il cui contenuto è determinato dal risultato restituito dal partner/merchant tramite API.
    - **Disattivazione guidata**: l’utente viene reindirizzato al sito del merchant per completare la cancellazione (US dedicata: <https://poste-digital.atlassian.net/browse/ONP-35193).>


la scelta tra “automatica” e “guidata” **non dipende dall’utente**; è determinata e proposta di default in base alla tipologia di operatività resa disponibile dal merchant e comunicata all’App tramite Mastercard.

L’APP deve mostrare **solo il flusso coerente** con quanto indicato dai dati restituiti via API.


## 1.3 UX / UI

L’utente, autenticato in **App Poste**, entra nel **cruscotto dei pagamenti ricorrenti**, seleziona un abbonamento e, dalla relativa pagina foglia, accede alla sezione **“Gestisci abbonamento”**. 

Nella pagina di snodo, tra le azioni disponibili, sceglie **“Disattiva abbonamento”**.

Se per quel merchant è prevista la **disattivazione automatica** (in base a quanto comunicato via API dal partner), l’APP mostra la pagina dedicata con:

- i **dati principali dell’abbonamento** (merchant e strumento di addebito utilizzato)
- una **card con i dati dell’intestatario** (nome, email e numero di cellulare), precompilati con le informazioni note all’App e modificabili tramite icona matita (dove consentito)
- un insieme di **campi aggiuntivi** richiesti dal merchant (fino a un massimo di 25), che l’utente deve verificare e completare, rispettando obbligatorietà, vincoli di editabilità ed eventuali helper
- una **card informativa** che indica fino a quale data il servizio può restare fruibile anche dopo la richiesta di disattivazione, se tale informazione è disponibile

Dopo aver verificato e compilato quanto richiesto, l’utente prosegue con **“Continua”**, inserisce il codice PosteID e, in caso di esito positivo, l’APP inoltra la richiesta di disattivazione automatica al backend, che la propaga al partner/merchant.

### Gestione disattivazione non real-time

La disattivazione potrebbe **non essere immediata** (es. aggiornamenti asincroni tra sistemi). In questi casi l’abbonamento viene gestito con uno stato intermedio **“In corso di disattivazione”**, che indica che la richiesta è stata presa in carico ma l’allineamento non è ancora concluso. Finché permane questo stato:

- l’APP mostra una label informativa che chiarisce l’attesa di aggiornamento
- le azioni potenzialmente in conflitto (es. “Cambia piano”, se presente) risultano **disabilitate**.

A completamento dell’allineamento, lo stato passa a **“Disattivato”** e l’abbonamento viene rappresentato tra le **ricorrenze non più attive** secondo le regole di cruscotto.

Quando l’allineamento tra sistemi si completa, lo stato dell’abbonamento viene aggiornato a **“Disattivato”** e l’abbonamento viene rappresentato tra le **ricorrenze non più attive**, secondo le regole di visualizzazione previste.

# 2*. Specifiche Tecniche*


Al tap sulla CTA**"Disattiva abbonamento"**, il Front End verifica preliminarmente che per la subscription selezionata sia disponibile l'azione di cancellazione.

La verifica viene effettuata tramite il servizio di ricerca delle azioni disponibili, che restituisce l'elenco delle operazioni supportate per la specifica subscription attraverso il campo *supportedActions.*  L'azione risulta disponibile in presenza del valore ***CANCEL***.

A seguito della selezione della funzionalità, il Front End invoca il servizio *POST /oneapp/pagauto/api/v1/recurrences/actions *passando l'identificativo della subscription e l'azione ***CANCEL***.

Il servizio restituisce le informazioni necessarie all'avvio del processo, tra cui:

- l'identificativo univoco dell'operazione (*actionId*)
- lo stato iniziale dell'azione
- l'eventuale survey contenente i campi richiesti dal merchant (*actionSurvey*)

Il Front End utilizza le informazioni ricevute per costruire dinamicamente la schermata di disattivazione, esponendo i campi richiesti e applicando le regole di obbligatorietà, editabilità e validazione restituite dai sistemi a valle. 

Una volta completata la compilazione dei dati richiesti, il Front End invia le informazioni raccolte tramite il servizio *POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} *trasmettendo:

- l'identificativo della survey, 
- le risposte fornite dall'utente
- gli eventuali dati di contesto richiesti dal merchant

Il servizio restituisce il *challenge *necessario per l'esecuzione dell'operazione e, a valle del completamento dellaSCA tramite PosteID, il Front End richiama *PUT /oneapp/pagauto/api/v1/recurrences/actions/{actionId} *per finalizzare la richiesta di cancellazione. 

A seguito dell'aggiornamento dello stato dell'operazione, il BE APP pubblica l'evento applicativo destinato ai sistemi di notifica e Bacheca, come da AF specifica: [ONP-37197: COMUNICAZIONI UTENTE](https://poste-digital.atlassian.net/wiki/spaces/DDPEDP/pages/1990098980/ONP-37197+COMUNICAZIONI+UTENTE)


# FINE FILE: ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md


# FILE: ONP-35194- CAMBIO PIANO.md

# ONP\-35194: CAMBIO PIANO

**Analisi Funzionale della feature: CAMBIO PIANO**

**Link Figma **[UI - Gestione Abbonamento – Figma](https://www.figma.com/design/S8twGqZ0Ij5KODjX0aDN1z/UI---Gestione-Abbonamento?node-id=897-7177&t=dPc0QMLhaqxHloVT-0)

SP: 13

# 1. Specifiche Funzionali

## 1.1 User Stories

- [ONP-35194](https://poste-digital.atlassian.net/browse/ONP-35194)

## 1.2 Comportamento Atteso

La funzionalità di **cambio piano** consente a un utente **autenticato in App** di modificare il piano associato a un abbonamento, partendo dal funnel “**Gestisci abbonamento**”.  
L’operazione si svolge in uno **scenario guidato a step**, che accompagna l’utente dalla scelta dell’azione fino alla conferma, mantenendo coerenza con le regole del singolo merchant.

Gli elementi chiave, tutti **determinati dinamicamente** dai sistemi esterni, sono:

- la **disponibilità del cambio piano** per il singolo abbonamento
- la **lista dei piani selezionabili**
- l’eventuale **raccolta di dati aggiuntivi** durante il flusso

## 1.3 UX / UI

L’utente accede al flusso di **cambio piano** dalla **pagina di snodo** degli abbonamenti, selezionando l’azione “**Cambia piano**” sul singolo abbonamento di interesse. Il percorso è guidato a step e mostra solo le informazioni necessarie alla scelta e alla conferma del nuovo piano; il dettaglio puntuale delle API è riportato nelle **Specifiche Tecniche**.

La **disponibilità **dell’azione, i campi richiesti all’utente e la lista dei piani selezionabili sono **determinati dinamicamente **dai sistemi esterni. Il FE deve quindi gestire un flusso configurabile, senza assumere a priori quali dati o piani saranno presenti per la singola subscription.

### Pagina iniziale step 1/3  

La pagina è composta da:

- **Titolo**
- **Dati dell’abbonamento**, per chiarire su quale subscription si sta operando
- **Card “Intestatario”** con i dati utente **precompilati** e non modificabili:
    - nome e cognome
    - beneficiario
    - strumento di pagamento
    - dati del piano attualmente associato all’abbonamento, se disponibili nel contesto della subscription
- **CTA “Continua”** per avviare l’operazione di cambio piano

Al tap sulla CTA “**Continua**”, viene avviata l’operazione di cambio piano e vengono recuperate le eventuali informazioni necessarie alla costruzione dello step successivo.

### 2/3 “Dati”

 Il FE APP espone i campi richiesti dal merchant sulla base delle regole ricevute: i campi possono essere precompilati, obbligatori, opzionali, modificabili o in sola lettura.

- Nome e Cognome dell’intestatario, NON modificabili

- Dati dell’intestatario modificabili, ove previsti dalla survey:
    - indirizzo e-mail
    - numero di cellulare
- Eventuali altri campi dinamici richiesti dal merchant fino a un massimo di 25, gestiti secondo le regole di visibilità, obbligatorietà e modificabilità ricevute
- **CTA “Continua”**

Al tap sulla CTA “Continua”, i dati confermati dall’utente vengono inviati per la validazione. Se la validazione ha esito positivo, il flusso prosegue con la pagina “Cambia piano”, alimentata con i piani effettivamente disponibili per la subscription.

### Pagina “Cambia piano” step 3/3

Questa pagina consente all’utente di selezionare il nuovo piano tra quelli disponibili per l’abbonamento selezionato.

La pagina è composta come segue:

- **Card dei piani disponibili**, generate in modo dinamico sulla base dei dati restituiti dai servizi
- Ogni card rappresenta un **piano selezionabile** e può contenere, in funzione di quanto restituito dal merchant:
    - nome del piano
    - importo e periodicità
    - eventuali dettagli o descrizioni del piano
- L’utente può **selezionare un solo piano** tra quelli proposti.
- **CTA “Continua”** per proseguire, abilitata solo dopo aver selezionato uno dei piani disponibili

### Pagina “Riepilogo”

La pagina riepiloga ciò che verrà effettivamente inviato ai sistemi per il cambio piano.

Sezioni principali:

- **Operazione** (es. “Cambio piano abbonamento”)
- **Intestatario** con i dati raccolti e confermati nello step “Dati”
- **Esercente** → nome esercente
- **Piano** → nome del nuovo piano selezionato
- **Importo** → importo associato al nuovo piano
- **CTA “Continua”** per aprire il drawer modale di conferma dell’operazione

A valle della pagina di riepilogo, l’utente visualizza un **drawer modale di conferma** dell’operazione. La conferma dal drawer avvia la fase autorizzativa SCA tramite PosteID.

Dopo l’autorizzazione, l’App mostra la **TYP di esito**: conferma/presa in carico in caso di esito positivo, oppure schermata KO in caso di errore. 

Consulta la sezione **Specifiche tecniche** per i dettagli sulle API.

### Approfondimento sui sistemi BE APP

Dopo la TYP di cambio piano, in caso di esito OK, nella **pagina foglia dell’abbonamento** i campi:

- **“Data di attivazione”**
- **“Importo”**

si aggiornano in funzione del verificarsi o meno del **pagamento del nuovo piano contestualmente al cambio**:

1. **Pagamento avvenuto contestualmente al cambio piano**
    - “Data di attivazione” e “Importo” si aggiornano in modo asincrono
    - **Fino all’aggiornamento effettivo**, ci sarà uno** stato intermedio nei sistemi di OneView** e, lato FE APP, nella pagina “Gestisci abbonamento” la card di azione è inibita ed informa l’utente che:
        - il piano è stato cambiato
        - i dati si aggiorneranno a breve
    - La card **torna attiva **quando i dati risultano aggiornati nella pagina foglia e lo stato cambia nei sistemi di OneView
2. **Pagamento non avvenuto contestualmente al cambio piano**
    - “Data di attivazione” e “Importo” si aggiornano **al primo pagamento/addebito periodico** del nuovo piano
    - **Fino all’aggiornamento**, è presente la **stessa card informativa** in “Gestisci abbonamento”
    - Anche in questo caso, la card **non deve più essere visibile** una volta allineati i dati in pagina foglia

# 2. Specifiche Tecniche

Il cambio stato è **SINCRONO** dal **Mercant → Mastercard → APP Poste**

le informazioni (importo, nome piano ecc.) sono **ASINCRONE** tra **BE APP → One View → Data Office **che non espone i dati in maniera sincrona, per la natura stessa del data office, basata sul *BATCH.*

Al tap sulla voce **“Cambia piano”** presente nella pagina di gestione dell’abbonamento, il FE verifica preliminarmente che l’azione sia tra quelle supportate per la subscription selezionata. 

La disponibilità dell’operazione viene determinata tramite il servizio:

 *POST /oneapp/pagauto/api/v1/recurrences/actions/search*

Il servizio restituisce le informazioni identificative della subscription e l’elenco delle operazioni consentite attraverso il campo *supportedActions*.    
L’azione di cambio piano risulta disponibile esclusivamente nel caso in cui l’elenco delle azioni supportate contenga il valore: ***CHANGE\_PLAN***.

Il flusso di cambio piano si articola secondo la seguente sequenza di chiamate tra **FE APP** e **BE APP**:

Una volta selezionata l’azione nella pagina di snodo, il FE invoca il servizio *POST /oneapp/pagauto/api/v1/recurrences/actions *passando le informazioni identificative della subscription (*subscriptionId*, *serviceId*) e l’azione richiesta (action: "*CHANGE\_PLAN*").    
Il servizio restituisce le informazioni necessarie all’avvio del processo, tra cui:

- l’identificativo univoco dell’operazione (*actionId*)
- l’eventuale survey contenente i campi richiesti dal merchant (*actionSurvey*) con le relative regole di visibilità, editabilità e obbligatorietà (anagrafica, email, cellulare ed eventuali campi dinamici aggiuntivi fino a 25)

Il **BE APP** associa l’*actionId* restituito da Mastercard alla relativa *subscriptionId*, mantenendo il contesto per le fasi successive del processo.    
Il Front End utilizza tali informazioni per costruire dinamicamente la schermata di compilazione dati dello Step 2 di 3 invocando il servizio* POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} *trasmettendo nel payload le risposte fornite dall’utente ai campi della survey.    
Il servizio valida i dati e restituisce al Front End l’elenco di tutti i piani effettivamente selezionabili per quell’abbonamento, comprensivi di:

- identificativo della survey
- le risposte fornite dall'utente
- gli eventuali dati di contesto richiesti dal merchant

Il Front End utilizza queste informazioni per popolare dinamicamente le card di selezione nella schermata **“Cambia piano” (Step 3 di 3)** e nel successivo **Riepilogo**.

A valle della pagina di riepilogo, al tap sulla CTA **“Conferma”** all’interno del drawer modale informativo (*"Vuoi cambiare il piano del tuo abbonamento?"*), il FE invoca il servizio *POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId}/challenges*trasmettendo l’identificativo del piano selezionato dall’utente.  

Il servizio predispone la transazione autorizzativa verso i sistemi a valle e restituisce il *challenge* necessario per l'avvio della SCA. Il Front End riceve la challenge firmata e attiva la schermata per l'inserimento del codice **PosteID**.

A valle del corretto inserimento e validazione del codice PosteID da parte dell’utente, il Front End invoca nuovamente il servizio *POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId}*  
inviando una **request alleggerita** contenente esclusivamente il dato autorizzativo firmato:

```json
{
  "signedChallenge": 
}
```

Il **BE APP** verifica la validità del challenge firmato ed esegue la transazione dispositiva verso il merchant.  
A seguito dell'esecuzione dell'operazione, il BE APP recepisce lo stato restituito da Mastercard tramite l’oggetto *actionState* e lo rende disponibile al FE per la corretta gestione dell'esito del processo:

- in caso di esito positivo/preso in carico (status = *SUCCESSFUL *o *IN\_PROGRESS*), il FE reindirizza l'utente alla **TYP di conferma**
- in caso di errore, viene presentata la schermata di errore dedicata

Per la mappatura degli stati possibili, fare riferimento a quanto descritto nella AF: [ONP-35208: POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO](https://poste-digital.atlassian.net/wiki/spaces/DDPEDP/pages/1975386275/ONP-35208+POSSIBILI+ESITI+DELLE+OPERAZIONI+e+CARD+DI+CAMBIO+STATO).

  
In caso di completamento del cambio piano, il Back End provvede inoltre a costruire e pubblicare l’evento applicativo sul topic Kafka per l’allineamento asincrono dei sistemi di notifica e bacheca, come descritto nella AF dedicata: [ONP-37197: COMUNICAZIONI UTENTE](https://poste-digital.atlassian.net/wiki/spaces/DDPEDP/pages/1990098980/ONP-37197+COMUNICAZIONI+UTENTE)

Per la funzionalità di **change plan**, la documentazione Mastercard indica una gestione **sincrona** dell’esito.

Il **frontend**, se* status = COMPLETATO,* mostra la **TYP di conferma operazione** con esito OK;

# 3 Gestione Errori

Se, la chiamata verso Mastercard fallisce, il **BE App**:

- restituisce un errore tecnico al FE (es. 400 o codice interno dedicato)
- non persiste alcun mapping *actionId ↔ subscriptionId*

Il **FE**:

- mostra una pagina/messaggio di errore coerente con la UI


- *In caso di mancata disponibilità dell'azione * (*CHANGE\_PLAN *non presente in *supportedActions*) o di errore nella verifica preliminare, la CTA non viene abilitata e non viene avviata alcuna azione di cambio piano.


# FINE FILE: ONP-35194- CAMBIO PIANO.md


# FILE: ONP-35208- POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO.md

# ONP\-35208: POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO

**Analisi Funzionale della feature: ESITO OPERAZIONI - FEEDBACK ALL’UTENTE**

**Link Figma **[UI - Gestione Abbonamento – Figma](https://www.figma.com/design/S8twGqZ0Ij5KODjX0aDN1z/UI---Gestione-Abbonamento?node-id=897-9562&t=dPc0QMLhaqxHloVT-0)

SP: 8

# 1. Specifiche Funzionali

## 1.1 User Stories

[ONP-35208](https://poste-digital.atlassian.net/browse/ONP-35208)

## 1.2 Comportamento Atteso

L’obiettivo della funzionalità è gestire in modo **dinamico le TYP **dell’APP in seguito a un’operazione di gestione dell’abbonamento, mostrand**o messaggi personalizzati sulla base della risposta del Merchant.**

Il sistema dovrà mappare le risposte provenienti dai sistemi di BE e tradurle in una card visibile, contenente un messaggio specifico per ciascun scenario.

Per il **dettaglio dei possibili esiti,** si rimanda al file Excel allegato:



## 1.3 UX / UI

### Stati delle Card

| **Scenario** | **Stato BE APP ** | **UI** | **Stato FE APP ** |
| --- | --- | --- | --- |
| Cambio piano | ATTIVO |  | ATTIVO |
| Cambio piano in corso | CAMBIATO |  | ATTIVO |
| ~~Disattivazione abbonamento in corso~~ | ~~IN CORSO DI SOSPENSIONE~~ |  | IN CORSO |
| Disattivazione abbonamento – automatica | ATTIVO |  | ATTIVO |
| Disattivazione abbonamento – automatica | IN CORSO DI SOSPENSIONE |  | IN CORSO DI DISATTIVAZIONE |
| Disattivazione abbonamento – automatica | DISATTIVATO |  | DISATTIVATO |
| ~~Disattivazione abbonamento – guidata~~ |  |  | COMPLETATO |

### Thank you pages

| **Scenario** | **UI** | **Stato** |
| --- | --- | --- |
| **Cambio piano ** |  | COMPLETATO |
| **Cambio piano ** |  | KO |
| **Disattivazione abbonamento in corso** |  | IN CORSO |
| **Disattivazione abbonamento ** |  | COMPLETATO |
| **Disattivazione abbonamento ** |  | KO |
| **Recesso del Servizio** |  | COMPLETATO |


**IN ATTESA DI MAPPATURA ESATTA DEGLI STATI LATO ONE VIEW**


# FINE FILE: ONP-35208- POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO.md
