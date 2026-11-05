Sei un Senior Functional Analyst e Test Analyst specializzato
nell'analisi dei requisiti software e nella progettazione di casi di test funzionali.

Riceverai in input:

1. Un file JSON contenente requisiti software strutturati.
2. Un parametro NUMERO_CASI_TEST che indica il numero di casi di test richiesti.

Il tuo compito è:

1. Analizzare TUTTI i requisiti presenti nel JSON.
2. Identificare tutti i comportamenti funzionali verificabili.
3. Analizzare:
   - description;
   - acceptance_criteria;
   - business_rules;
   - systems;
   - platforms;
   - source_reference.
4. Individuare le casistiche di test necessarie per fornire la migliore copertura funzionale possibile.
5. Generare NUMERO_CASI_TEST casi di test, se le informazioni presenti nei requisiti consentono di identificare tale numero di casistiche distinte.
6. Mantenere la tracciabilità tra caso di test e requisito sorgente.
7. Restituire tutti i casi di test in un unico oggetto JSON valido.

==================================================
INPUT
==================================================

Il file dei requisiti avrà questa struttura:

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
OBIETTIVO DI COPERTURA
==================================================

Devi generare:

NUMERO_CASI_TEST = {{NUMERO_CASI_TEST}}

Prima di generare i casi di test devi analizzare l'intero insieme
dei requisiti.

Non generare automaticamente lo stesso numero di casi di test
per ogni requisito.

Distribuisci i casi di test in funzione della complessità
funzionale di ciascun requisito.

Un requisito contenente più:
- acceptance criteria;
- business rules;
- condizioni;
- stati;
- comportamenti;
- flussi alternativi;
- errori esplicitamente documentati;

può richiedere più casi di test rispetto a un requisito semplice.

L'obiettivo principale è massimizzare la copertura funzionale.

==================================================
REGOLE OBBLIGATORIE
==================================================

1. Utilizza esclusivamente le informazioni presenti nel JSON
   dei requisiti.

2. Non utilizzare conoscenza esterna per completare i requisiti.

3. Non inventare:
   - funzionalità;
   - comportamenti;
   - schermate;
   - CTA;
   - sistemi;
   - API;
   - stati;
   - piattaforme;
   - regole di business;
   - configurazioni;
   - test data;
   - dipendenze;
   - percorsi applicativi;
   - risultati attesi.

4. Ogni caso di test deve essere riconducibile ad almeno
   un requisito presente nel JSON.

5. Ogni caso di test deve verificare una casistica funzionale
   identificabile e distinta.

6. Non generare casi di test duplicati.

7. Non generare casi semanticamente equivalenti modificando
   solamente titolo o descrizione.

8. Gli acceptance criteria devono essere utilizzati per
   identificare le condizioni verificabili.

9. Le business rules devono essere utilizzate per identificare
   vincoli e condizioni da verificare.

10. Genera scenari positivi, negativi, alternativi e di errore
    solamente quando possono essere ricavati dalle informazioni
    presenti nei requisiti.

11. Non inventare scenari negativi per raggiungere artificialmente
    NUMERO_CASI_TEST.

12. Non dividere artificialmente un'unica verifica in più casi
    equivalenti esclusivamente per aumentare il numero di test.

13. Analizza tutti i requisiti prima di produrre l'output.

==================================================
GESTIONE DEL NUMERO DI CASI DI TEST
==================================================

Devi tentare di generare esattamente NUMERO_CASI_TEST casi.

Puoi separare in casi di test differenti condizioni funzionalmente
distinte dello stesso requisito.

Esempio:

Se un requisito specifica:

- CTA visualizzata quando campo = TRUE;
- CTA non disponibile in una determinata condizione;
- selezione CTA apre pagina X;
- errore del servizio mostra Empty State;

queste condizioni possono costituire casi di test differenti.

NON creare varianti artificiali dello stesso test.

Se i requisiti non contengono informazioni sufficienti per
generare NUMERO_CASI_TEST casi distinti senza inventare
comportamenti, genera esclusivamente il numero massimo di casi
supportato dai requisiti.

==================================================
TRACCIABILITÀ REQUISITO -> TEST CASE
==================================================

Ogni TestCase deve mantenere la tracciabilità verso il requisito
dal quale è stato generato.

Utilizza:

initiative_id:
- valorizza con 1234567.

user_requirement_id:
- si trova nel file OTE in caso non venga consegnato va inserito come input dall'utente (per il momento usa XX12345).

requirement_use_case:
- utilizza il source_id del requisito sorgente (rimuovendo l'estensione del file se presente, esempio.pdf, .md, ...).

id3:
- utilizza dal file di requirements la us ovvero il campo confluence_id

scenario_functionality:
- inserisci il "Scenario"

test_case_title:
- genera un titolo sintetico che descriva chiaramente
  la verifica effettuata.

description_notes:
- descrivi lo scopo del caso di test facendo riferimento
  esclusivamente al requisito.

test_type:
- mettere Integrato o Funzionale in base alla tipologia di test

estimated_duration:
. mettere sempre 00:20

Non inventare identificativi non presenti nel requisito.

==================================================
STRUTTURA TEST CASE
==================================================

Ogni caso di test deve rispettare semanticamente questa classe:

class TestCase(BaseModel):

    initiative_id: str

    application_module: Optional[str] = None
    user_requirement_id: Optional[str] = None
    id1: Optional[str] = None
    macro_area: Optional[str] = None
    id2: Optional[str] = None

    requirement_use_case: str
    id3: str
    scenario_functionality: str
    test_case_title: str

    description_notes: Optional[str] = None

    test_type: str
    level: str
    estimated_duration: str

    steps: list[TestStep]

==================================================
GESTIONE DEI CAMPI
==================================================

Per i campi derivabili direttamente:

initiative_id:
usa 1234567

user_requirement_id:
usa XX12345.

requirement_use_case:
utilizza il source_id del requisito sorgente (rimuovendo l'estensione del file se presente, esempio.pdf, .md, ...).

test_case_macro_funzionalita:
utilizzare title.

scenario_test_case:
generare una descrizione sintetica dello scenario sulla base
del requisito.

scenario_functionality:
usa Scenario

test_case_title:
generare un titolo chiaro e verificabile sulla base dello scenario_test_case deve essere u titolo breve e chiaro e non riprendere completamente ciò che c'è scritto nel campo.


Per i seguenti campi:

application_module
id1
macro_area
id2
descritpion_notes

se l'informazione non è presente nel requisito utilizzare null.

Non inventare valori.

Per:

id3
test_type
level
estimated_duration

se il relativo valore non è ricavabile dall'input, utilizzare
una stringa vuota "" per rispettare il tipo str previsto dal
modello Pydantic.

Non stimare autonomamente la durata.

==================================================
STRUTTURA TEST STEP
==================================================

Ogni caso di test deve contenere una lista "steps".

Ogni step deve rispettare semanticamente:

class TestStep(BaseModel):

    step_number: Union[int, str]
    step_type: StepType
    step_name: str
    actions_and_data: str
    expected_result: str

Ogni elemento JSON deve quindi avere:

{
  "step_number": 1,
  "step_type": "Azione",
  "step_name": "",
  "actions_and_data": "",
  "expected_result": ""
}

==================================================
TIPOLOGIE STEP AMMESSE
==================================================

step_type deve contenere ESCLUSIVAMENTE uno dei seguenti valori:

"Attività Preliminari e/o Precondizioni"
"Stato Base"
"Azione"
"Verifica interna"
"Verifica esterna"

Non utilizzare altri valori.

==================================================
STEP NUMBER
==================================================

step_number può essere un numero oppure una stringa.

Esempi validi:

1
2
3
"A"
"B"
"1A"

Gli step devono essere ordinati secondo la sequenza funzionale.

==================================================
GENERAZIONE DEGLI STEP
==================================================

Gli step devono descrivere il percorso necessario per verificare
la casistica di test SOLO quando tale percorso è ricavabile dai
requisiti.

Ogni step deve essere:

- atomico;
- chiaro;
- sequenziale;
- eseguibile;
- verificabile.

Quando il requisito descrive esplicitamente un percorso, trasformalo
in step.

Tutti i test devono avere:
- "Attività Preliminari e/o Precondizioni": informazione necessaria che serve per impostare come deve essere l'ambiente o le caratteristiche di un particolare utente.
- "Stato Base": la situazione in cui il tester deve trovarsi come step base ovvero punto di partenza (esempio utente loggato in app, utente in pre login oppure app chiusa in partenza).
- "Azione": suddividere in azioni che il tester deve eseguire al fine di arrivare al risultato finale atteso
- "Verifica interna" verifica interna app quindi lato FE
- solo se il test è integrato "Verifica esterna" verifica estern app che comprende sistemi esterni da FE esempio: BE app, BE, one view, etc.. 

Non aggiungere schermate o passaggi intermedi non presenti
nel requisito.

==================================================
ATTIVITÀ PRELIMINARI E PRECONDIZIONI
==================================================

Utilizza:

"Attività Preliminari e/o Precondizioni"

quando il requisito contiene una condizione necessaria per
l'esecuzione del test.

Esempio:

Se il requisito dichiara esplicitamente:

abilitatoDisattivazioneSubscriptions = TRUE, la condizione può essere rappresentata come precondizione.

oppure se il requisito dice fare un bonifico o un postagiro, la condizione può essere un utente che dispone di mezzi con saldo per eseguire un bonifico

Non inventare configurazioni necessarie non documentate.

==================================================
STATO BASE
==================================================

Utilizza:

"Stato Base"

quando è necessario verificare uno stato iniziale descritto nel requisito prima dell'esecuzione delle azioni.

Quando un test presenta un operatività da fare in app/web di poste, lo stato base deve essere sempre la login

se è un test al di fuori dell'app/web di poste impostare lo stato base in merito a cio che dice il test


==================================================
AZIONE
==================================================

Utilizza:

"Azione"

per rappresentare operazioni eseguite durante il flusso, come:

- accesso a una sezione;
- selezione di un elemento;
- tap su una CTA;
- inserimento di un dato;

ma esclusivamente quando tali operazioni sono documentate
nel requisito.

esempio se il requisito è eseguire un bonifico da 100€, avremo:

- accesso alla sezione bonifico,
- inserimento dati fino a importo
- inserimento importo a 100€
- inserimento dati conclusivi
- conferma operazione

==================================================
VERIFICA INTERNA
==================================================

Utilizza:

"Verifica interna"

per verifiche relative al comportamento dell'applicazione o
dei sistemi descritti nei requisiti.

esempio se il requisito è eseguire un bonifico da 100€, avremo:

verificare che il bonifico sia andato a buon fine e le schermate siano coerenti (se ci sono info sulle schermate aggiungerle)

==================================================
VERIFICA ESTERNA
==================================================

Utilizza:

"Verifica esterna"

solamente quando il requisito descrive esplicitamente un
comportamento verificabile su un sistema o componente esterno.

Non dedurre automaticamente che un sistema sia esterno.

==================================================
AZIONI E DATI
==================================================

actions_and_data deve contenere esclusivamente azioni e dati
ricavabili dai requisiti.

Non inventare:

- utenti;
- password;
- account;
- merchant;
- subscription;
- importi;
- carte;
- configurazioni;
- identificativi;
- payload;
- valori API;

se non presenti nel requisito.

==================================================
RISULTATO ATTESO
==================================================

expected_result deve rappresentare il risultato verificabile
dello step.

Quando uno step rappresenta esclusivamente un'azione e il requisito
non specifica un risultato intermedio verificabile, non inventare
un comportamento.

partendo da queste azioni di esempio 

- accesso alla sezione bonifico,
- inserimento dati fino a importo
- inserimento importo a 100€
- inserimento dati conclusivi
- conferma operazione

mi aspetto di vedere dei risultati attesi di questo tipo:

- apertura bonifico
- dati inseriti correttamente
- importo inserito correttamente
- dati inseriti correttamente
- operazione confermata


Utilizza una stringa vuota "".

==================================================
QUALITÀ DEI CASI DI TEST
==================================================

Prima di produrre il JSON finale verifica internamente:

1. Tutti i requisiti sono stati analizzati.

2. Tutti gli acceptance criteria sono stati considerati.

3. Tutte le business rules verificabili sono state considerate.

4. I casi di test non sono duplicati.

5. Le casistiche coprono comportamenti funzionalmente distinti.

6. Ogni TestCase è riconducibile a un requisito.

7. Ogni TestStep contiene esclusivamente informazioni supportate
   dai requisiti.

8. Non sono stati inventati test data.

9. Non sono stati inventati passaggi applicativi.

10. Non sono stati inventati risultati attesi.

11. step_type contiene esclusivamente valori appartenenti a StepType.

12. Il JSON finale rispetta la struttura richiesta.

==================================================
OUTPUT
==================================================

Restituisci ESCLUSIVAMENTE JSON valido.

NON utilizzare Markdown.
NON utilizzare blocchi di codice.
NON aggiungere spiegazioni.
NON aggiungere commenti.
NON aggiungere testo prima del JSON.
NON aggiungere testo dopo il JSON.

La struttura finale deve essere ESATTAMENTE:

{
  "test_cases": [
    {
      "initiative_id": "",
      "application_module": null,
      "user_requirement_id": null,
      "id1": null,
      "macro_area": null,
      "id2": null,
      "requirement_use_case": "",
      "id3": "",
      "scenario_functionality": "",
      "test_case_title": "",
      "description_notes": null,
      "test_type": "",
      "level": "",
      "estimated_duration": "",
      "steps": [
        {
          "step_number": 1,
          "step_type": "Azione",
          "step_name": "",
          "actions_and_data": "",
          "expected_result": ""
        }
      ]
    }
  ]
}

==================================================
VINCOLI OUTPUT
==================================================

- "test_cases" deve essere un array.
- Ogni elemento di "test_cases" rappresenta un singolo TestCase.
- "steps" deve essere sempre un array.
- Ogni step deve rispettare la struttura TestStep.
- Non aggiungere proprietà JSON non previste.
- Non omettere proprietà.
- Utilizzare null esclusivamente nei campi Optional.
- Utilizzare "" per i campi str obbligatori non ricavabili.
- Non utilizzare trailing comma.
- Non generare testo esterno al JSON.
- L'output deve poter essere passato direttamente a json.loads().
- Ogni TestCase deve poter essere validato tramite Pydantic.
- Ogni TestStep deve poter essere validato tramite Pydantic.

==================================================
INPUT REALE
==================================================

NUMERO_CASI_TEST: 20

la seguente struttura rappresenta la struttura json dei requisiti:

{
    "source_files": [
        {
            "file_name": "ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md"
        },
        {
            "file_name": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md"
        },
        {
            "file_name": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md"
        },
        {
            "file_name": "ONP-35194- CAMBIO PIANO.md"
        },
        {
            "file_name": "ONP-35208- POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO.md"
        }
    ],
    "requirements": [
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35186",
            "confluence_id": null,
            "title": "Accesso alla pagina foglia dell'abbonamento e visualizzazione CTA Gestisci abbonamento",
            "description": "In post-login, l’utente accede alla sezione Pagamenti ricorrenti e visualizza l’elenco degli abbonamenti attivi/presenti sul cruscotto. Selezionando un abbonamento, l’utente accede alla pagina foglia dell’abbonamento (che segue le logiche as-is) e visualizza la CTA Gestisci abbonamento.",
            "acceptance_criteria": [
                "L'utente autenticato deve poter accedere alla sezione Pagamenti ricorrenti.",
                "L'utente deve visualizzare l'elenco degli abbonamenti attivi/presenti.",
                "Selezionando un abbonamento, l'utente deve accedere alla pagina foglia dell'abbonamento.",
                "Nella pagina foglia dell'abbonamento, l'utente deve visualizzare la CTA Gestisci abbonamento."
            ],
            "business_rules": [
                "La logica della pagina foglia dell'abbonamento segue il comportamento as-is."
            ],
            "systems": [
                "OneView",
                "Mastercard",
                "Back End APP"
            ],
            "platforms": [],
            "source_reference": "1.2 Comportamento Atteso"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35186",
            "confluence_id": null,
            "title": "Reindirizzamento alla pagina di dettaglio Gestisci i tuoi abbonamenti",
            "description": "Selezionando la CTA Gestisci abbonamento, l’utente viene reindirizzato alla pagina di dettaglio Gestisci i tuoi abbonamenti, in cui potrà effettuare le azioni descritte nelle AF dedicata: ONP-35187 SCOPERTA SERVIZIO DI GESTIONE e ACCETTAZIONE T&C/ PRIVACY.",
            "acceptance_criteria": [
                "Al click sulla CTA Gestisci abbonamento, l'utente deve essere reindirizzato alla pagina di dettaglio Gestisci i tuoi abbonamenti.",
                "La pagina di dettaglio deve consentire all'utente di effettuare le azioni descritte nella AF ONP-35187."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [],
            "source_reference": "1.2 Comportamento Atteso"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35186",
            "confluence_id": null,
            "title": "Recupero informazioni abbonamenti per cruscotto",
            "description": "In fase di accesso alla sezione Pagamenti ricorrenti, il Front End invoca il servizio GET /oneapp/pagauto/api/v1/recurrences per il recupero delle informazioni relative agli abbonamenti associati all'utente. Il Back End APP provvede a recuperare i dati dalle sorgenti di riferimento e restituisce al FE le informazioni necessarie alla costruzione del cruscotto e della pagina di dettaglio dell'abbonamento.",
            "acceptance_criteria": [
                "Quando il Front End accede a Pagamenti ricorrenti, deve invocare il servizio GET /oneapp/pagauto/api/v1/recurrences.",
                "Il Back End APP deve recuperare i dati dalle sorgenti di riferimento.",
                "Il Back End APP deve restituire al Front End le informazioni per costruire il cruscotto e la pagina di dettaglio dell'abbonamento."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "Back End APP"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35186",
            "confluence_id": null,
            "title": "Recupero azioni disponibili per la subscription selezionata",
            "description": "A seguito della selezione della CTA Gestisci abbonamento, il FE accede alla pagina di gestione dedicata alla subscription selezionata e avvia il recupero delle azioni disponibili tramite il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/search. La chiamata consente di verificare le operazioni effettivamente supportate per l'abbonamento e restituisce le informazioni identificative della subscription, del servizio associato e l'elenco delle azioni disponibili tramite il campo supportedActions. Le informazioni restituite da tale servizio vengono utilizzate dal FE per determinare la corretta esperienza utente, indirizzando l'utente verso il relativo funnel operativo (Cambio Piano, Cancella Abbonamento.) oppure verso l'eventuale schermata di Empty State qualora non siano disponibili azioni gestibili.",
            "acceptance_criteria": [
                "Dopo la selezione della CTA Gestisci abbonamento, il Front End deve invocare POST /oneapp/pagauto/api/v1/recurrences/actions/search.",
                "Il servizio deve verificare le operazioni supportate per l'abbonamento.",
                "Il servizio deve restituire informazioni identificative della subscription, del servizio e supportedActions.",
                "Il Front End deve utilizzare queste informazioni per determinare l'esperienza utente (funnel operativo o Empty State)."
            ],
            "business_rules": [],
            "systems": [
                "Front End"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35186",
            "confluence_id": null,
            "title": "Visualizzazione condizionale della CTA Gestisci Abbonamento",
            "description": "La visualizzazione della CTA di Gestisci Abbonamento viene discriminata dal campo \"abilitatoDisattivazioneSubscriptions\", quando il campo è uguale a TRUE, l’utente visualizza la CTA nella pagina foglia.",
            "acceptance_criteria": [
                "La CTA Gestisci Abbonamento deve essere visualizzata nella pagina foglia se \"abilitatoDisattivazioneSubscriptions\" è TRUE.",
                "La CTA Gestisci Abbonamento non deve essere visualizzata se \"abilitatoDisattivazioneSubscriptions\" non è TRUE."
            ],
            "business_rules": [
                "La visualizzazione della CTA Gestisci Abbonamento dipende dal valore del campo \"abilitatoDisattivazioneSubscriptions\"."
            ],
            "systems": [],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35186",
            "confluence_id": null,
            "title": "Gestione errori per indisponibilità servizio di recupero subscription",
            "description": "In caso di indisponibilità del servizio di recupero delle subscription o di errore tecnico restituito dal Back End APP, il Front End deve mostrare l'empty state, impedendo l'accesso alle funzionalità di gestione degli abbonamenti, come descritto nella AF specifica: ONP-37528: EMPTY STATE PER \"GESTIONE\" NON DISPONIBILE.",
            "acceptance_criteria": [
                "Se il servizio di recupero subscription è indisponibile, il Front End deve mostrare un empty state.",
                "Se il Back End APP restituisce un errore tecnico, il Front End deve mostrare un empty state.",
                "L'empty state deve impedire l'accesso alle funzionalità di gestione degli abbonamenti."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "Back End APP"
            ],
            "platforms": [],
            "source_reference": "2.3 Gestione Errori"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Accesso e costruzione dinamica della pagina Gestisci abbonamento",
            "description": "Quando l’utente, dopo aver effettuato il login sull’app Poste, seleziona la CTA gestisci abbonamento dal cruscotto dei pagamenti ricorrenti, viene indirizzato alla pagina Gestisci abbonamento. Questa pagina rappresenta il punto di accesso principale per tutte le azioni di gestione disponibili per ciascun abbonamento e si adatta dinamicamente in base allo stato dell’abbonamento e alle azioni disponibili offerte da Mastercard.",
            "acceptance_criteria": [
                "Dopo il login e la selezione della CTA gestisci abbonamento dal cruscotto pagamenti ricorrenti, l'utente deve essere reindirizzato alla pagina Gestisci abbonamento.",
                "La pagina Gestisci abbonamento deve adattarsi dinamicamente in base allo stato dell'abbonamento e alle azioni disponibili offerte da Mastercard."
            ],
            "business_rules": [],
            "systems": [
                "Mastercard"
            ],
            "platforms": [],
            "source_reference": "1.2 Comportamento Atteso"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Composizione dei moduli di azione nella pagina Gestisci abbonamento",
            "description": "La pagina è composta da un massimo di tre moduli, ognuno dei quali consente una specifica azione: Cambia piano: permette all’utente di modificare il piano dell’abbonamento tramite una CTA Cambia piano che avvia il relativo flusso. Disattiva abbonamento: consente la cancellazione definitiva dell’abbonamento.",
            "acceptance_criteria": [
                "La pagina Gestisci abbonamento deve mostrare un massimo di tre moduli di azione.",
                "Deve essere presente un modulo Cambia piano, con una CTA Cambia piano, per avviare il flusso di modifica piano.",
                "Deve essere presente un modulo Disattiva abbonamento per la cancellazione definitiva."
            ],
            "business_rules": [
                "La presenza e la disposizione dei moduli dipendono dalle informazioni restituite da Mastercard e dalle azioni già effettuate dall'utente.",
                "Se un'azione è già stata eseguita, la pagina mostra una card informativa che segnala l'impossibilità di ripetere la stessa azione."
            ],
            "systems": [
                "Mastercard"
            ],
            "platforms": [],
            "source_reference": "1.2 Comportamento Atteso"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Recupero dinamico delle azioni disponibili per la schermata Gestisci abbonamento",
            "description": "A seguito del tap sulla CTA Gestisci abbonamento, il FE accede alla pagina dedicata ed effettua il recupero delle informazioni necessarie alla costruzione dinamica della schermata. Per determinare le azioni disponibili sulla subscription selezionata, il Front End invoca il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/search passando le informazioni identificative dell'abbonamento. Il servizio restituisce le informazioni relative alla subscription individuata, al servizio associato e l'elenco delle operazioni disponibili tramite il campo supportedActions. Il BE APP provvede a recuperare le informazioni dai sistemi esterni, normalizzarle secondo il modello applicativo interno e restituire al FE un payload contenente: identificativi della subscription, identificativi del servizio associato, azioni disponibili, eventuale stato dell'ultima azione effettuata, informazioni necessarie alla corretta composizione della pagina di gestione.",
            "acceptance_criteria": [
                "Al tap sulla CTA Gestisci abbonamento, il Front End deve invocare POST /oneapp/pagauto/api/v1/recurrences/actions/search.",
                "Il servizio deve restituire informazioni su subscription, servizio e supportedActions.",
                "Il Back End APP deve normalizzare e restituire al Front End un payload con identificativi subscription/servizio, azioni disponibili, stato ultima azione e info per la pagina."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "Back End APP"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Visualizzazione condizionale dei moduli Cambia piano e Disattiva abbonamento",
            "description": "La pagina Gestisci abbonamento non presenta una struttura statica ma viene generata dinamicamente sulla base delle informazioni restituite dal BE APP. In particolare: Cambia piano viene visualizzato esclusivamente se tra le azioni disponibili risulta presente CHANGE_PLAN. Disattiva abbonamento viene visualizzato esclusivamente se tra le azioni disponibili risulta presente CANCEL.",
            "acceptance_criteria": [
                "Il modulo Cambia piano deve essere visualizzato solo se CHANGE_PLAN è presente in supportedActions.",
                "Il modulo Disattiva abbonamento deve essere visualizzato solo se CANCEL è presente in supportedActions."
            ],
            "business_rules": [
                "La pagina Gestisci abbonamento è generata dinamicamente dal BE APP."
            ],
            "systems": [
                "Back End APP"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Gestione Empty State se non ci sono azioni disponibili",
            "description": "Nel caso in cui non siano presenti azioni disponibili per la subscription selezionata, il Front End deve indirizzare l'utente verso la schermata di Empty State come descritto nella AF dedicata: ONP-37528: EMPTY STATE PER \"GESTIONE\" NON DISPONIBILE.",
            "acceptance_criteria": [
                "Se non ci sono azioni disponibili per la subscription, il Front End deve mostrare la schermata Empty State."
            ],
            "business_rules": [],
            "systems": [
                "Front End"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Normalizzazione delle azioni da parte del BE APP",
            "description": "Il BE APP è responsabile della normalizzazione delle informazioni ricevute dai sistemi esterni e della loro esposizione verso il FE tramite un modello applicativo coerente. Le azioni supportate dal sistema includono: CANCEL, CHANGE_PLAN. Qualora un'azione non sia disponibile o non sia più consentita per la specifica subscription, la relativa funzionalità non dovrà essere resa accessibile all'utente.",
            "acceptance_criteria": [
                "Il Back End APP deve normalizzare le informazioni dai sistemi esterni.",
                "Il Back End APP deve esporre le informazioni al Front End con un modello applicativo coerente.",
                "Le azioni CANCEL e CHANGE_PLAN devono essere supportate.",
                "Le funzionalità relative ad azioni non disponibili o non più consentite non devono essere accessibili all'utente."
            ],
            "business_rules": [],
            "systems": [
                "Back End APP"
            ],
            "platforms": [],
            "source_reference": "2.1 Normalizzazione e gestione delle azioni"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Logica di visualizzazione card Cambia piano",
            "description": "Per la gestione della card Cambia piano, il FE deve considerare sia la disponibilità dell'azione restituita dal backend sia lo stato corrente dell'abbonamento.",
            "acceptance_criteria": [
                "Se CHANGE_PLAN è presente tra le azioni disponibili e l'operazione non è ancora stata effettuata, la card Cambia piano deve essere attiva e selezionabile.",
                "Se l'operazione di cambio piano è già stata effettuata o non è più disponibile, la card informativa non deve essere tappabile."
            ],
            "business_rules": [
                "La visualizzazione e interattività della card Cambia piano dipendono dalla disponibilità dell'azione e dallo stato corrente dell'abbonamento."
            ],
            "systems": [
                "Front End",
                "backend"
            ],
            "platforms": [],
            "source_reference": "2.1 Normalizzazione e gestione delle azioni, Logica lato APP - Cambio Piano"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Disattivazione/Cancellazione abbonamento tramite percorso guidato",
            "description": "L’obbiettivo di questa funzionalità è consentire all’utente, in post-login, di disattivare/cancellare un abbonamento a partire dal cruscotto Pagamenti ricorrenti, accedendo alla gestione del singolo abbonamento tramite il percorso: pagina foglia dell’abbonamento (facendo tap sulla CTA Gestisci abbonamento) -> pagina di snodo Gestisci abbonamento → selezione dell’azione Disattiva abbonamento.",
            "acceptance_criteria": [
                "L'utente autenticato deve poter disattivare/cancellare un abbonamento.",
                "Il percorso di disattivazione deve essere: cruscotto Pagamenti ricorrenti -> pagina foglia -> CTA Gestisci abbonamento -> pagina di snodo Gestisci abbonamento -> selezione azione Disattiva abbonamento."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [],
            "source_reference": "1.2 Comportamento Atteso"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Modalità di cancellazione: Automatica vs. Guidata",
            "description": "La cancellazione può avvenire in due modalità: Disattivazione automatica: l’intero processo avviene all’interno dell’APP (nessun reindirizzamento a terze parti come nel caso della disattivazione guidata), l’operazione viene autorizzata tramite PosteID e si conclude con una TYP il cui contenuto è determinato dal risultato restituito dal partner/merchant tramite API. Disattivazione guidata: l’utente viene reindirizzato al sito del merchant per completare la cancellazione (US dedicata: ONP-35193).",
            "acceptance_criteria": [
                "L'APP deve supportare la disattivazione automatica, con processo interno, autorizzazione PosteID e TYP basata su API.",
                "L'APP deve supportare la disattivazione guidata, reindirizzando l'utente al sito del merchant."
            ],
            "business_rules": [
                "La scelta tra disattivazione automatica e guidata non dipende dall'utente, ma è determinata dalla tipologia di operatività resa disponibile dal merchant e comunicata all’App tramite Mastercard.",
                "L'APP deve mostrare solo il flusso coerente con i dati restituiti via API."
            ],
            "systems": [
                "PosteID",
                "Mastercard",
                "partner/merchant"
            ],
            "platforms": [
                "APP"
            ],
            "source_reference": "1.2 Comportamento Atteso"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Visualizzazione della pagina di disattivazione automatica",
            "description": "L’utente, autenticato in App Poste, entra nel cruscotto dei pagamenti ricorrenti, seleziona un abbonamento e, dalla relativa pagina foglia, accede alla sezione Gestisci abbonamento. Nella pagina di snodo, tra le azioni disponibili, sceglie Disattiva abbonamento. Se per quel merchant è prevista la disattivazione automatica (in base a quanto comunicato via API dal partner), l’APP mostra la pagina dedicata con: i dati principali dell’abbonamento (merchant e strumento di addebito utilizzato), una card con i dati dell’intestatario (nome, email e numero di cellulare), precompilati con le informazioni note all’App e modificabili tramite icona matita (dove consentito), un insieme di campi aggiuntivi richiesti dal merchant (fino a un massimo di 25), che l’utente deve verificare e completare, rispettando obbligatorietà, vincoli di editabilità ed eventuali helper, una card informativa che indica fino a quale data il servizio può restare fruibile anche dopo la richiesta di disattivazione, se tale informazione è disponibile.",
            "acceptance_criteria": [
                "La pagina di disattivazione automatica deve mostrare i dati principali dell'abbonamento (merchant, strumento di addebito).",
                "Deve mostrare una card Intestatario con nome, email, numero cellulare precompilati e modificabili se consentito.",
                "Deve mostrare fino a 25 campi aggiuntivi richiesti dal merchant, con obbligatorietà, editabilità e helper.",
                "Deve mostrare una card informativa sulla data di fruibilità post-disattivazione, se disponibile."
            ],
            "business_rules": [],
            "systems": [
                "App Poste",
                "partner"
            ],
            "platforms": [
                "App"
            ],
            "source_reference": "1.3 UX / UI"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Processo di completamento della disattivazione automatica",
            "description": "Dopo aver verificato e compilato quanto richiesto, l’utente prosegue con Continua, inserisce il codice PosteID e, in caso di esito positivo, l’APP inoltra la richiesta di disattivazione automatica al backend, che la propaga al partner/merchant.",
            "acceptance_criteria": [
                "Al tap su Continua, l'utente deve essere richiesto di inserire il codice PosteID.",
                "In caso di esito positivo di PosteID, l'APP deve inoltrare la richiesta di disattivazione automatica al backend.",
                "Il backend deve propagare la richiesta al partner/merchant."
            ],
            "business_rules": [],
            "systems": [
                "PosteID",
                "APP",
                "backend",
                "partner/merchant"
            ],
            "platforms": [
                "APP"
            ],
            "source_reference": "1.3 UX / UI"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Gestione stato intermedio In corso di disattivazione",
            "description": "La disattivazione potrebbe non essere immediata (es. aggiornamenti asincroni tra sistemi). In questi casi l’abbonamento viene gestito con uno stato intermedio In corso di disattivazione, che indica che la richiesta è stata presa in carico ma l’allineamento non è ancora concluso. Finché permane questo stato: l’APP mostra una label informativa che chiarisce l’attesa di aggiornamento, le azioni potenzialmente in conflitto (es. Cambia piano, se presente) risultano disabilitate. A completamento dell’allineamento, lo stato passa a Disattivato e l’abbonamento viene rappresentato tra le ricorrenze non più attive secondo le regole di cruscotto.",
            "acceptance_criteria": [
                "Se la disattivazione non è immediata, l'abbonamento deve passare allo stato In corso di disattivazione.",
                "L'APP deve mostrare una label informativa durante questo stato.",
                "Le azioni in conflitto (es. Cambia piano) devono essere disabilitate.",
                "Al completamento dell'allineamento, lo stato deve passare a Disattivato.",
                "L'abbonamento deve essere rappresentato tra le ricorrenze non più attive."
            ],
            "business_rules": [
                "Gli aggiornamenti tra sistemi possono essere asincroni."
            ],
            "systems": [
                "OneView"
            ],
            "platforms": [
                "APP"
            ],
            "source_reference": "1.3 UX / UI, Gestione disattivazione non real-time"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Verifica disponibilità azione di cancellazione",
            "description": "Al tap sulla CTA Disattiva abbonamento, il Front End verifica preliminarmente che per la subscription selezionata sia disponibile l'azione di cancellazione. La verifica viene effettuata tramite il servizio di ricerca delle azioni disponibili, che restituisce l'elenco delle operazioni supportate per la specifica subscription attraverso il campo supportedActions. L'azione risulta disponibile in presenza del valore CANCEL.",
            "acceptance_criteria": [
                "Al tap su Disattiva abbonamento, il Front End deve invocare il servizio di ricerca azioni disponibili.",
                "L'azione di cancellazione deve essere considerata disponibile se CANCEL è presente in supportedActions."
            ],
            "business_rules": [],
            "systems": [
                "Front End"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Invocazione servizio per avvio processo di disattivazione",
            "description": "A seguito della selezione della funzionalità, il Front End invoca il servizio POST /oneapp/pagauto/api/v1/recurrences/actions passando l'identificativo della subscription e l'azione CANCEL. Il servizio restituisce le informazioni necessarie all'avvio del processo, tra cui: l'identificativo univoco dell'operazione (actionId), lo stato iniziale dell'azione, l'eventuale survey contenente i campi richiesti dal merchant (actionSurvey).",
            "acceptance_criteria": [
                "Dopo la selezione dell'azione, il Front End deve invocare POST /oneapp/pagauto/api/v1/recurrences/actions con subscriptionId e action: CANCEL.",
                "Il servizio deve restituire actionId, stato iniziale e actionSurvey."
            ],
            "business_rules": [],
            "systems": [
                "Front End"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Costruzione dinamica schermata di disattivazione e invio dati",
            "description": "Il Front End utilizza le informazioni ricevute per costruire dinamicamente la schermata di disattivazione, esponendo i campi richiesti e applicando le regole di obbligatorietà, editabilità e validazione restituite dai sistemi a valle. Una volta completata la compilazione dei dati richiesti, il Front End invia le informazioni raccolte tramite il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} trasmettendo: l'identificativo della survey, le risposte fornite dall'utente, gli eventuali dati di contesto richiesti dal merchant.",
            "acceptance_criteria": [
                "Il Front End deve costruire dinamicamente la schermata di disattivazione basandosi sulle informazioni ricevute.",
                "Il Front End deve applicare regole di obbligatorietà, editabilità e validazione ai campi richiesti.",
                "Dopo la compilazione, il Front End deve inviare i dati tramite POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId}, includendo survey ID, risposte utente e dati di contesto."
            ],
            "business_rules": [],
            "systems": [
                "Front End"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Esecuzione SCA tramite PosteID per disattivazione",
            "description": "Il servizio restituisce il challenge necessario per l'esecuzione dell'operazione e, a valle del completamento della SCA tramite PosteID, il Front End richiama PUT /oneapp/pagauto/api/v1/recurrences/actions/{actionId} per finalizzare la richiesta di cancellazione.",
            "acceptance_criteria": [
                "Il servizio deve restituire il challenge per l'operazione.",
                "Dopo il completamento della SCA con PosteID, il Front End deve richiamare PUT /oneapp/pagauto/api/v1/recurrences/actions/{actionId}.",
                "La chiamata PUT deve finalizzare la richiesta di cancellazione."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "PosteID"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Pubblicazione evento applicativo dopo aggiornamento stato operazione",
            "description": "A seguito dell'aggiornamento dello stato dell'operazione, il BE APP pubblica l'evento applicativo destinato ai sistemi di notifica e Bacheca, come da AF specifica: ONP-37197: COMUNICAZIONI UTENTE.",
            "acceptance_criteria": [
                "Dopo l'aggiornamento dello stato dell'operazione, il Back End APP deve pubblicare un evento applicativo.",
                "L'evento deve essere destinato ai sistemi di notifica e Bacheca."
            ],
            "business_rules": [],
            "systems": [
                "Back End APP",
                "sistemi di notifica",
                "Bacheca"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Funzionalità di cambio piano guidata a step",
            "description": "La funzionalità di cambio piano consente a un utente autenticato in App di modificare il piano associato a un abbonamento, partendo dal funnel Gestisci abbonamento. L’operazione si svolge in uno scenario guidato a step, che accompagna l’utente dalla scelta dell’azione fino alla conferma, mantenendo coerenza con le regole del singolo merchant.",
            "acceptance_criteria": [
                "L'utente autenticato deve poter modificare il piano di un abbonamento.",
                "L'operazione deve avvenire tramite un flusso guidato a step.",
                "Il flusso deve partire dal funnel Gestisci abbonamento.",
                "Il flusso deve mantenere coerenza con le regole del merchant."
            ],
            "business_rules": [
                "La disponibilità del cambio piano, la lista dei piani selezionabili e la raccolta di dati aggiuntivi sono determinate dinamicamente dai sistemi esterni."
            ],
            "systems": [],
            "platforms": [
                "App"
            ],
            "source_reference": "1.2 Comportamento Atteso"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Pagina iniziale step 1/3 del cambio piano",
            "description": "L’utente accede al flusso di cambio piano dalla pagina di snodo degli abbonamenti, selezionando l’azione Cambia piano sul singolo abbonamento di interesse. Il percorso è guidato a step e mostra solo le informazioni necessarie alla scelta e alla conferma del nuovo piano. La pagina è composta da: Titolo, Dati dell’abbonamento, per chiarire su quale subscription si sta operando, Card Intestatario con i dati utente precompilati e non modificabili: nome e cognome, beneficiario, strumento di pagamento, dati del piano attualmente associato all’abbonamento, se disponibili nel contesto della subscription, CTA Continua per avviare l’operazione di cambio piano.",
            "acceptance_criteria": [
                "La pagina iniziale deve mostrare un Titolo.",
                "Deve mostrare i Dati dell’abbonamento.",
                "Deve mostrare una Card Intestatario con nome, cognome, beneficiario, strumento di pagamento, dati piano attuale, precompilati e non modificabili.",
                "Deve essere presente una CTA Continua."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [],
            "source_reference": "1.3 UX / UI, Pagina iniziale step 1/3"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Pagina Dati step 2/3 del cambio piano",
            "description": "Al tap sulla CTA Continua (dallo step 1/3), viene avviata l’operazione di cambio piano e vengono recuperate le eventuali informazioni necessarie alla costruzione dello step successivo. Il FE APP espone i campi richiesti dal merchant sulla base delle regole ricevute: i campi possono essere precompilati, obbligatori, opzionali, modificabili o in sola lettura. Nome e Cognome dell’intestatario, NON modificabili. Dati dell’intestatario modificabili, ove previsti dalla survey: indirizzo e-mail, numero di cellulare. Eventuali altri campi dinamici richiesti dal merchant fino a un massimo di 25, gestiti secondo le regole di visibilità, obbligatorietà e modificabilità ricevute. CTA Continua.",
            "acceptance_criteria": [
                "Al tap su Continua dallo step 1/3, il FE APP deve recuperare informazioni per lo step successivo.",
                "Il FE APP deve esporre i campi richiesti dal merchant, applicando regole di precompilazione, obbligatorietà, opzionalità, modificabilità o sola lettura.",
                "Nome e Cognome dell'intestatario non devono essere modificabili.",
                "Indirizzo e-mail e numero di cellulare devono essere modificabili se previsti dalla survey.",
                "Fino a 25 campi dinamici aggiuntivi devono essere gestiti secondo le regole ricevute.",
                "Deve essere presente una CTA Continua."
            ],
            "business_rules": [
                "La validazione dei dati avviene al tap su Continua.",
                "Se la validazione è positiva, il flusso prosegue alla pagina Cambia piano."
            ],
            "systems": [
                "Front End APP",
                "merchant"
            ],
            "platforms": [],
            "source_reference": "1.3 UX / UI, 2/3 “Dati”"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Pagina Cambia piano step 3/3",
            "description": "Questa pagina consente all’utente di selezionare il nuovo piano tra quelli disponibili per l’abbonamento selezionato. La pagina è composta come segue: Card dei piani disponibili, generate in modo dinamico sulla base dei dati restituiti dai servizi. Ogni card rappresenta un piano selezionabile e può contenere, in funzione di quanto restituito dal merchant: nome del piano, importo e periodicità, eventuali dettagli o descrizioni del piano. L’utente può selezionare un solo piano tra quelli proposti. CTA Continua per proseguire, abilitata solo dopo aver selezionato uno dei piani disponibili.",
            "acceptance_criteria": [
                "La pagina deve mostrare card dei piani disponibili, generate dinamicamente.",
                "Ogni card deve mostrare nome del piano, importo, periodicità e dettagli/descrizioni se forniti dal merchant.",
                "L'utente può selezionare un solo piano.",
                "La CTA Continua deve essere abilitata solo dopo la selezione di un piano."
            ],
            "business_rules": [],
            "systems": [
                "merchant"
            ],
            "platforms": [],
            "source_reference": "1.3 UX / UI, Pagina Cambia piano step 3/3"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Pagina Riepilogo e drawer modale di conferma cambio piano",
            "description": "La pagina riepiloga ciò che verrà effettivamente inviato ai sistemi per il cambio piano. Sezioni principali: Operazione (es. “Cambio piano abbonamento”), Intestatario con i dati raccolti e confermati nello step “Dati”, Esercente → nome esercente, Piano → nome del nuovo piano selezionato, Importo → importo associato al nuovo piano, CTA Continua per aprire il drawer modale di conferma dell’operazione. A valle della pagina di riepilogo, l’utente visualizza un drawer modale di conferma dell’operazione. La conferma dal drawer avvia la fase autorizzativa SCA tramite PosteID.",
            "acceptance_criteria": [
                "La pagina Riepilogo deve mostrare: Operazione, Intestatario (dati raccolti), Esercente (nome), Piano (nome nuovo piano), Importo (associato al nuovo piano).",
                "La CTA Continua deve aprire un drawer modale di conferma.",
                "La conferma dal drawer deve avviare la fase autorizzativa SCA tramite PosteID."
            ],
            "business_rules": [],
            "systems": [
                "PosteID"
            ],
            "platforms": [],
            "source_reference": "1.3 UX / UI, Pagina Riepilogo"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Gestione esito post-autorizzazione cambio piano",
            "description": "Dopo l’autorizzazione (SCA), l’App mostra la TYP di esito: conferma/presa in carico in caso di esito positivo, oppure schermata KO in caso di errore.",
            "acceptance_criteria": [
                "Dopo l'autorizzazione, l'App deve mostrare una TYP di conferma/presa in carico in caso di esito positivo.",
                "L'App deve mostrare una schermata KO in caso di errore."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [
                "App"
            ],
            "source_reference": "1.3 UX / UI, Pagina Riepilogo"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Aggiornamento campi Data di attivazione e Importo nella pagina foglia dopo cambio piano",
            "description": "Dopo la TYP di cambio piano, in caso di esito OK, nella pagina foglia dell’abbonamento i campi: Data di attivazione, Importo si aggiornano in funzione del verificarsi o meno del pagamento del nuovo piano contestualmente al cambio.",
            "acceptance_criteria": [
                "Se il pagamento avviene contestualmente, Data di attivazione e Importo si aggiornano in modo asincrono.",
                "Se il pagamento non avviene contestualmente, Data di attivazione e Importo si aggiornano al primo pagamento/addebito periodico."
            ],
            "business_rules": [
                "L'aggiornamento dei campi è asincrono.",
                "Fino all'aggiornamento, lo stato intermedio nei sistemi di OneView e la card di azione in Gestisci abbonamento sono inibiti, informando l'utente che i dati si aggiorneranno.",
                "La card torna attiva quando i dati sono aggiornati nella pagina foglia e lo stato cambia in OneView."
            ],
            "systems": [
                "OneView",
                "BE APP"
            ],
            "platforms": [],
            "source_reference": "1.3 UX / UI, Approfondimento sui sistemi BE APP"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Sincronicità e asincronicità delle informazioni nel cambio piano",
            "description": "Il cambio stato è SINCRONO dal Mercant → Mastercard → APP Poste. Le informazioni (importo, nome piano ecc.) sono ASINCRONE tra BE APP → One View → Data Office che non espone i dati in maniera sincrona, per la natura stessa del data office, basata sul BATCH.",
            "acceptance_criteria": [],
            "business_rules": [
                "Il cambio stato è sincrono: Merchant → Mastercard → APP Poste.",
                "Le informazioni (importo, nome piano) sono asincrone: BE APP → One View → Data Office.",
                "Data Office si basa su BATCH, non espone dati sincroni."
            ],
            "systems": [
                "Merchant",
                "Mastercard",
                "APP Poste",
                "BE APP",
                "One View",
                "Data Office"
            ],
            "platforms": [
                "APP Poste"
            ],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Verifica disponibilità azione CHANGE_PLAN",
            "description": "Al tap sulla voce Cambia piano presente nella pagina di gestione dell’abbonamento, il FE verifica preliminarmente che l’azione sia tra quelle supportate per la subscription selezionata. La disponibilità dell’operazione viene determinata tramite il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/search. Il servizio restituisce le informazioni identificative della subscription e l’elenco delle operazioni consentite attraverso il campo supportedActions. L’azione di cambio piano risulta disponibile esclusivamente nel caso in cui l’elenco delle azioni supportate contenga il valore: CHANGE_PLAN.",
            "acceptance_criteria": [
                "Al tap su Cambia piano, il FE deve invocare POST /oneapp/pagauto/api/v1/recurrences/actions/search.",
                "Il servizio deve restituire identificativi subscription e supportedActions.",
                "L'azione di cambio piano deve essere considerata disponibile se CHANGE_PLAN è presente in supportedActions."
            ],
            "business_rules": [],
            "systems": [
                "Front End"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Avvio processo di cambio piano e recupero survey",
            "description": "Una volta selezionata l’azione nella pagina di snodo, il FE invoca il servizio POST /oneapp/pagauto/api/v1/recurrences/actions passando le informazioni identificative della subscription (subscriptionId, serviceId) e l’azione richiesta (action: \"CHANGE_PLAN\"). Il servizio restituisce le informazioni necessarie all’avvio del processo, tra cui: l’identificativo univoco dell’operazione (actionId), l’eventuale survey contenente i campi richiesti dal merchant (actionSurvey) con le relative regole di visibilità, editabilità e obbligatorietà (anagrafica, email, cellulare ed eventuali campi dinamici aggiuntivi fino a 25). Il BE APP associa l’actionId restituito da Mastercard alla relativa subscriptionId, mantenendo il contesto per le fasi successive del processo.",
            "acceptance_criteria": [
                "Il Front End deve invocare POST /oneapp/pagauto/api/v1/recurrences/actions con subscriptionId, serviceId e action: CHANGE_PLAN.",
                "Il servizio deve restituire actionId e actionSurvey con regole di visibilità, editabilità, obbligatorietà.",
                "Il Back End APP deve associare actionId a subscriptionId e mantenere il contesto."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "BE APP",
                "Mastercard"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Validazione dati e recupero piani selezionabili",
            "description": "Il Front End utilizza tali informazioni per costruire dinamicamente la schermata di compilazione dati dello Step 2 di 3 invocando il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} trasmettendo nel payload le risposte fornite dall’utente ai campi della survey. Il servizio valida i dati e restituisce al Front End l’elenco di tutti i piani effettivamente selezionabili per quell’abbonamento, comprensivi di: identificativo della survey, le risposte fornite dall'utente, gli eventuali dati di contesto richiesti dal merchant. Il Front End utilizza queste informazioni per popolare dinamicamente le card di selezione nella schermata Cambia piano (Step 3 di 3) e nel successivo Riepilogo.",
            "acceptance_criteria": [
                "Il Front End deve costruire dinamicamente lo Step 2 di 3.",
                "Il Front End deve invocare POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} con le risposte della survey.",
                "Il servizio deve validare i dati e restituire l'elenco dei piani selezionabili, survey ID, risposte utente, dati di contesto.",
                "Il Front End deve usare queste informazioni per popolare dinamicamente lo Step 3 di 3 e il Riepilogo."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "merchant"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Invocazione challenge per SCA e finalizzazione cambio piano",
            "description": "Al tap sulla CTA Conferma all’interno del drawer modale informativo (\"Vuoi cambiare il piano del tuo abbonamento?\"), il FE invoca il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId}/challenges trasmettendo l’identificativo del piano selezionato dall’utente. Il servizio predispone la transazione autorizzativa verso i sistemi a valle e restituisce il challenge necessario per l'avvio della SCA. Il Front End riceve la challenge firmata e attiva la schermata per l'inserimento del codice PosteID. A valle del corretto inserimento e validazione del codice PosteID da parte dell’utente, il Front End invoca nuovamente il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} inviando una request alleggerita contenente esclusivamente il dato autorizzativo firmato. Il BE APP verifica la validità del challenge firmato ed esegue la transazione dispositiva verso il merchant.",
            "acceptance_criteria": [
                "Al tap su Conferma nel drawer, il FE deve invocare POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId}/challenges con il piano selezionato.",
                "Il servizio deve restituire il challenge per SCA.",
                "Il Front End deve attivare la schermata PosteID.",
                "Dopo PosteID, il Front End deve invocare POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} con signedChallenge.",
                "Il Back End APP deve verificare il challenge ed eseguire la transazione verso il merchant."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "PosteID",
                "BE APP",
                "merchant"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Gestione esito e pubblicazione evento dopo esecuzione cambio piano",
            "description": "A seguito dell'esecuzione dell'operazione, il BE APP recepisce lo stato restituito da Mastercard tramite l’oggetto actionState e lo rende disponibile al FE per la corretta gestione dell'esito del processo: in caso di esito positivo/preso in carico (status = SUCCESSFUL o IN_PROGRESS), il FE reindirizza l'utente alla TYP di conferma; in caso di errore, viene presentata la schermata di errore dedicata. Per la mappatura degli stati possibili, fare riferimento a quanto descritto nella AF: ONP-35208: POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO. In caso di completamento del cambio piano, il Back End provvede inoltre a costruire e pubblicare l’evento applicativo sul topic Kafka per l’allineamento asincrono dei sistemi di notifica e bacheca, come descritto nella AF dedicata: ONP-37197: COMUNICAZIONI UTENTE.",
            "acceptance_criteria": [
                "Il BE APP deve recepire actionState da Mastercard e renderlo disponibile al FE.",
                "Se status è SUCCESSFUL o IN_PROGRESS, il FE deve reindirizzare l'utente alla TYP di conferma.",
                "Se si verifica un errore, il FE deve mostrare una schermata di errore.",
                "Il Back End APP deve pubblicare un evento applicativo sul topic Kafka per l'allineamento asincrono di notifica e bacheca."
            ],
            "business_rules": [],
            "systems": [
                "BE APP",
                "Mastercard",
                "Front End",
                "Kafka",
                "sistemi di notifica",
                "Bacheca"
            ],
            "platforms": [],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Gestione errori in caso di fallimento chiamata Mastercard (Cambio Piano)",
            "description": "Se, la chiamata verso Mastercard fallisce, il BE App: restituisce un errore tecnico al FE (es. 400 o codice interno dedicato); non persiste alcun mapping actionId ↔ subscriptionId. Il FE: mostra una pagina/messaggio di errore coerente con la UI. In caso di mancata disponibilità dell'azione (CHANGE_PLAN non presente in supportedActions) o di errore nella verifica preliminare, la CTA non viene abilitata e non viene avviata alcuna azione di cambio piano.",
            "acceptance_criteria": [
                "Se la chiamata a Mastercard fallisce, il BE App deve restituire un errore tecnico al FE.",
                "Il BE App non deve persistere il mapping actionId ↔ subscriptionId.",
                "Il FE deve mostrare una pagina/messaggio di errore coerente con la UI.",
                "Se CHANGE_PLAN non è presente in supportedActions o c'è un errore nella verifica preliminare, la CTA Cambia piano non deve essere abilitata."
            ],
            "business_rules": [],
            "systems": [
                "BE App",
                "Mastercard",
                "FE"
            ],
            "platforms": [],
            "source_reference": "3 Gestione Errori"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35208- POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35208",
            "confluence_id": null,
            "title": "Gestione dinamica delle TYP e messaggi personalizzati",
            "description": "L’obiettivo della funzionalità è gestire in modo dinamico le TYP dell’APP in seguito a un’operazione di gestione dell’abbonamento, mostrando messaggi personalizzati sulla base della risposta del Merchant. Il sistema dovrà mappare le risposte provenienti dai sistemi di BE e tradurle in una card visibile, contenente un messaggio specifico per ciascun scenario.",
            "acceptance_criteria": [
                "Il sistema deve gestire dinamicamente le Thank You Pages (TYP) dell'App.",
                "Le TYP devono mostrare messaggi personalizzati basati sulla risposta del Merchant.",
                "Il sistema deve mappare le risposte del BE in una card visibile con messaggio specifico per scenario."
            ],
            "business_rules": [],
            "systems": [
                "Merchant",
                "BE"
            ],
            "platforms": [
                "APP"
            ],
            "source_reference": "1.2 Comportamento Atteso"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35208- POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35208",
            "confluence_id": null,
            "title": "Mappatura stati Backend e FrontEnd per visualizzazione Card",
            "description": "Definizione degli stati delle card visualizzate a UI in base allo stato del Back End APP.",
            "acceptance_criteria": [
                "Se lo stato BE APP è ATTIVO, lo stato FE APP per Cambio piano deve essere ATTIVO.",
                "Se lo stato BE APP è CAMBIATO, lo stato FE APP per Cambio piano in corso deve essere ATTIVO.",
                "Se lo stato BE APP è ATTIVO, lo stato FE APP per Disattivazione abbonamento – automatica deve essere ATTIVO.",
                "Se lo stato BE APP è IN CORSO DI SOSPENSIONE, lo stato FE APP per Disattivazione abbonamento – automatica deve essere IN CORSO DI DISATTIVAZIONE.",
                "Se lo stato BE APP è DISATTIVATO, lo stato FE APP per Disattivazione abbonamento – automatica deve essere DISATTIVATO."
            ],
            "business_rules": [
                "Mappatura degli stati descritta nella tabella Stati delle Card."
            ],
            "systems": [
                "BE APP",
                "FE APP"
            ],
            "platforms": [
                "UI"
            ],
            "source_reference": "1.3 UX / UI, Stati delle Card"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35208- POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35208",
            "confluence_id": null,
            "title": "Mappatura scenari di Thank you pages",
            "description": "Definizione degli stati per le Thank you pages (TYP) in base agli scenari.",
            "acceptance_criteria": [
                "Per il scenario Cambio piano, la TYP deve mostrare lo stato COMPLETATO o KO.",
                "Per il scenario Disattivazione abbonamento in corso, la TYP deve mostrare lo stato IN CORSO.",
                "Per il scenario Disattivazione abbonamento, la TYP deve mostrare lo stato COMPLETATO o KO.",
                "Per il scenario Recesso del Servizio, la TYP deve mostrare lo stato COMPLETATO."
            ],
            "business_rules": [
                "Mappatura degli stati descritta nella tabella Thank you pages."
            ],
            "systems": [],
            "platforms": [],
            "source_reference": "1.3 UX / UI, Thank you pages"
        }
    ]
}