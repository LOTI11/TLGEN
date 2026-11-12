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
            "title": "Accesso alla pagina di dettaglio Gestisci i tuoi abbonamenti dalla pagina foglia dell'abbonamento",
            "description": "Dopo il login, l'utente accede alla sezione Pagamenti ricorrenti e visualizza l'elenco degli abbonamenti attivi/presenti sul cruscotto. Selezionando un abbonamento, l'utente accede alla pagina foglia dell'abbonamento (che segue le logiche as-is) e visualizza la CTA Gestisci abbonamento. Selezionando la CTA, l'utente viene reindirizzato alla pagina di dettaglio Gestisci i tuoi abbonamenti.",
            "acceptance_criteria": [
                "L'utente, dopo il login, visualizza la sezione Pagamenti ricorrenti.",
                "L'utente visualizza l'elenco degli abbonamenti attivi/presenti sul cruscotto.",
                "Selezionando un abbonamento, l'utente accede alla pagina foglia dell'abbonamento.",
                "Nella pagina foglia dell'abbonamento, l'utente visualizza la CTA Gestisci abbonamento.",
                "Selezionando la CTA Gestisci abbonamento, l'utente viene reindirizzato alla pagina di dettaglio Gestisci i tuoi abbonamenti."
            ],
            "business_rules": [
                "La visualizzazione della CTA Gestisci Abbonamento è discriminata dal campo \"abilitatoDisattivazioneSubscriptions\".",
                "La CTA Gestisci Abbonamento è visualizzata nella pagina foglia se \"abilitatoDisattivazioneSubscriptions\" è TRUE."
            ],
            "systems": [
                "OneView",
                "Mastercard",
                "Back End APP",
                "Front End"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "1.2 Comportamento Atteso, 2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35186",
            "confluence_id": null,
            "title": "Recupero informazioni sugli abbonamenti e costruzione cruscotto Pagamenti ricorrenti",
            "description": "In fase di accesso alla sezione Pagamenti ricorrenti, il Front End invoca il servizio GET /oneapp/pagauto/api/v1/recurrences per il recupero delle informazioni relative agli abbonamenti associati all'utente. Il Back End APP provvede a recuperare i dati dalle sorgenti di riferimento e restituisce al Front End le informazioni necessarie alla costruzione del cruscotto e della pagina di dettaglio dell'abbonamento.",
            "acceptance_criteria": [
                "Il Front End invoca GET /oneapp/pagauto/api/v1/recurrences all'accesso alla sezione Pagamenti ricorrenti.",
                "Il Back End APP recupera i dati degli abbonamenti dalle sorgenti di riferimento.",
                "Il Back End APP restituisce al Front End le informazioni per la costruzione del cruscotto e della pagina di dettaglio dell'abbonamento."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "Back End APP",
                "OneView"
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
            "title": "Recupero delle azioni disponibili per la gestione di un abbonamento",
            "description": "A seguito della selezione della CTA Gestisci abbonamento, il Front End accede alla pagina di gestione dedicata alla subscription selezionata e avvia il recupero delle azioni disponibili tramite il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/search. La chiamata consente di verificare le operazioni effettivamente supportate per l'abbonamento e restituisce le informazioni identificative della subscription, del servizio associato e l'elenco delle azioni disponibili tramite il campo supportedActions.",
            "acceptance_criteria": [
                "Il Front End invoca POST /oneapp/pagauto/api/v1/recurrences/actions/search dopo la selezione della CTA Gestisci abbonamento.",
                "Il servizio restituisce le operazioni supportate per l'abbonamento.",
                "Il servizio restituisce le informazioni identificative della subscription.",
                "Il servizio restituisce le informazioni identificative del servizio associato.",
                "Il servizio restituisce l'elenco delle azioni disponibili nel campo supportedActions."
            ],
            "business_rules": [
                "Le informazioni restituite da POST /oneapp/pagauto/api/v1/recurrences/actions/search determinano la corretta esperienza utente.",
                "L'esperienza utente indirizza l'utente verso il relativo funnel operativo (Cambio Piano, Cancella Abbonamento) oppure verso l'eventuale schermata di Empty State qualora non siano disponibili azioni gestibili."
            ],
            "systems": [
                "Front End",
                "Back End APP",
                "Mastercard"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35186 ENTRY POINT DA PAGINA FOGLIA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35186",
            "confluence_id": null,
            "title": "Gestione errore in caso di indisponibilità del servizio di recupero subscription",
            "description": "In caso di indisponibilità del servizio di recupero delle subscription o di errore tecnico restituito dal Back End APP, il Front End deve mostrare l'empty state, impedendo l'accesso alle funzionalità di gestione degli abbonamenti.",
            "acceptance_criteria": [
                "Se il servizio di recupero subscription è indisponibile, il Front End mostra l'empty state.",
                "Se il Back End APP restituisce un errore tecnico durante il recupero subscription, il Front End mostra l'empty state.",
                "L'accesso alle funzionalità di gestione degli abbonamenti è impedito in caso di errore."
            ],
            "business_rules": [
                "L'empty state da mostrare è quello descritto nella AF specifica ONP-37528."
            ],
            "systems": [
                "Front End",
                "Back End APP"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "2.3 Gestione Errori"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Accesso e composizione dinamica della pagina Gestisci abbonamento",
            "description": "Quando l’utente, dopo aver effettuato il login sull’app Poste, seleziona la CTA gestisci abbonamento dal cruscotto dei pagamenti ricorrenti, viene indirizzato alla pagina Gestisci abbonamento. Questa pagina rappresenta il punto di accesso principale per tutte le azioni di gestione disponibili per ciascun abbonamento e si adatta dinamicamente in base allo stato dell’abbonamento e alle azioni disponibili offerte da Mastercard. La pagina è composta da un massimo di tre moduli: Cambia piano e Disattiva abbonamento.",
            "acceptance_criteria": [
                "L'utente viene indirizzato alla pagina Gestisci abbonamento dopo aver selezionato la CTA gestisci abbonamento dal cruscotto.",
                "La pagina Gestisci abbonamento si adatta dinamicamente in base allo stato dell'abbonamento.",
                "La pagina Gestisci abbonamento si adatta dinamicamente in base alle azioni disponibili offerte da Mastercard.",
                "La pagina può mostrare moduli per Cambia piano e Disattiva abbonamento."
            ],
            "business_rules": [
                "La presenza e la disposizione dei moduli dipendono sia dalle informazioni restituite da Mastercard, sia dalle azioni già effettuate dall'utente.",
                "Se una determinata azione è già stata eseguita (ad esempio, cambio piano), la pagina mostra una card informativa che segnala all'utente l'impossibilità di ripetere la stessa azione."
            ],
            "systems": [
                "Front End",
                "Mastercard"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "1.2 Comportamento Atteso"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Recupero informazioni per la costruzione dinamica della pagina Gestisci abbonamento",
            "description": "A seguito del tap sulla CTA Gestisci abbonamento, il Front End accede alla pagina dedicata ed effettua il recupero delle informazioni necessarie alla costruzione dinamica della schermata. Per determinare le azioni disponibili sulla subscription selezionata, il Front End invoca il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/search passando le informazioni identificative dell'abbonamento. Il servizio restituisce le informazioni relative alla subscription individuata, al servizio associato e l'elenco delle operazioni disponibili tramite il campo supportedActions.",
            "acceptance_criteria": [
                "Il Front End invoca POST /oneapp/pagauto/api/v1/recurrences/actions/search dopo il tap sulla CTA Gestisci abbonamento.",
                "Il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/search riceve le informazioni identificative dell'abbonamento.",
                "Il servizio restituisce informazioni relative alla subscription, al servizio associato e l'elenco delle operazioni disponibili tramite il campo supportedActions."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "Back End APP",
                "Mastercard"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Esposizione condizionale dei moduli Cambia piano e Disattiva abbonamento",
            "description": "La pagina Gestisci abbonamento non presenta una struttura statica ma viene generata dinamicamente sulla base delle informazioni restituite dal Back End APP. Il modulo Cambia piano viene visualizzato esclusivamente se tra le azioni disponibili risulta presente CHANGE_PLAN. Il modulo Disattiva abbonamento viene visualizzato esclusivamente se tra le azioni disponibili risulta presente CANCEL.",
            "acceptance_criteria": [
                "La pagina Gestisci abbonamento è generata dinamicamente dal Back End APP.",
                "Il modulo Cambia piano è visualizzato se CHANGE_PLAN è presente in supportedActions.",
                "Il modulo Disattiva abbonamento è visualizzato se CANCEL è presente in supportedActions."
            ],
            "business_rules": [
                "Le azioni supportate dal sistema includono CANCEL e CHANGE_PLAN.",
                "Qualora un'azione non sia disponibile o non sia più consentita per la specifica subscription, la relativa funzionalità non dovrà essere resa accessibile all'utente."
            ],
            "systems": [
                "Front End",
                "Back End APP"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "2. Specifiche Tecniche, 2.1 Normalizzazione e gestione delle azioni"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Visualizzazione e attivazione della card Cambia piano",
            "description": "Per la gestione della card Cambia piano, il Front End deve considerare sia la disponibilità dell'azione restituita dal backend sia lo stato corrente dell'abbonamento. La card è attiva e selezionabile se CHANGE_PLAN è presente tra le azioni disponibili e l'operazione non è ancora stata effettuata. Se l'operazione di cambio piano è già stata effettuata o non più disponibile, la card è informativa e non tappabile.",
            "acceptance_criteria": [
                "La card Cambia piano è attiva e selezionabile se CHANGE_PLAN è presente e l'operazione non è ancora stata effettuata.",
                "La card Cambia piano è informativa e non tappabile se l'operazione è già stata effettuata o non più disponibile."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "Back End APP"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "2.1 Normalizzazione e gestione delle azioni, Logica lato APP - Cambio Piano"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Visualizzazione Empty State per assenza di azioni disponibili",
            "description": "Nel caso in cui non siano presenti azioni disponibili per la subscription selezionata, il Front End deve indirizzare l'utente verso la schermata di Empty State.",
            "acceptance_criteria": [
                "Se supportedActions è vuoto o non contiene azioni, il Front End mostra l'Empty State."
            ],
            "business_rules": [
                "L'Empty State da mostrare è quello descritto nella AF dedicata ONP-37528."
            ],
            "systems": [
                "Front End"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35188 PAGINA DI SNODO -GESTISCI ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35188",
            "confluence_id": null,
            "title": "Normalizzazione dei dati da sistemi esterni per il Front End",
            "description": "Il Back End APP è responsabile della normalizzazione delle informazioni ricevute dai sistemi esterni e della loro esposizione verso il Front End tramite un modello applicativo coerente.",
            "acceptance_criteria": [
                "Il Back End APP normalizza le informazioni ricevute dai sistemi esterni.",
                "Il Back End APP espone le informazioni normalizzate al Front End tramite un modello applicativo coerente."
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
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Disattivazione automatica di un abbonamento tramite App Poste",
            "description": "L’obiettivo di questa funzionalità è consentire all’utente, in post-login, di disattivare/cancellare un abbonamento a partire dal cruscotto Pagamenti ricorrenti, accedendo alla gestione del singolo abbonamento tramite il percorso: pagina foglia dell’abbonamento (facendo tap sulla CTA Gestisci abbonamento) -> pagina di snodo Gestisci abbonamento → selezione dell’azione Disattiva abbonamento.",
            "acceptance_criteria": [
                "L'utente, autenticato, accede al cruscotto Pagamenti ricorrenti.",
                "L'utente seleziona un abbonamento e dalla pagina foglia accede alla sezione Gestisci abbonamento.",
                "L'utente sceglie Disattiva abbonamento dalla pagina di snodo."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "1.2 Comportamento Atteso, 1.3 UX / UI"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Gestione delle modalità di cancellazione abbonamento (automatica o guidata)",
            "description": "La cancellazione può avvenire in due modalità: Disattivazione automatica, dove l'intero processo avviene all'interno dell’APP (nessun reindirizzamento a terze parti), l'operazione viene autorizzata tramite PosteID e si conclude con una TYP il cui contenuto è determinato dal risultato restituito dal partner/merchant tramite API. Disattivazione guidata, dove l'utente viene reindirizzato al sito del merchant per completare la cancellazione (US dedicata: ONP-35193).",
            "acceptance_criteria": [
                "Il sistema supporta la disattivazione automatica.",
                "Il sistema supporta la disattivazione guidata con reindirizzamento.",
                "La disattivazione automatica non richiede reindirizzamenti.",
                "L'operazione di disattivazione automatica richiede autorizzazione tramite PosteID.",
                "La disattivazione automatica si conclude con una TYP il cui contenuto dipende dal risultato del partner/merchant."
            ],
            "business_rules": [
                "La scelta tra disattivazione automatica e guidata non dipende dall’utente.",
                "La scelta è determinata e proposta di default in base alla tipologia di operatività resa disponibile dal merchant e comunicata all’App tramite Mastercard.",
                "L’APP deve mostrare solo il flusso coerente con quanto indicato dai dati restituiti via API."
            ],
            "systems": [
                "Mastercard"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Visualizzazione pagina di disattivazione automatica per abbonamento",
            "description": "Se per quel merchant è prevista la disattivazione automatica (in base a quanto comunicato via API dal partner), l’APP mostra la pagina dedicata con: i dati principali dell’abbonamento (merchant e strumento di addebito utilizzato), una card con i dati dell’intestatario (nome, email e numero di cellulare), precompilati con le informazioni note all’App e modificabili tramite icona matita (dove consentito), un insieme di campi aggiuntivi richiesti dal merchant (fino a un massimo di 25), che l’utente deve verificare e completare, rispettando obbligatorietà, vincoli di editabilità ed eventuali helper. Può essere presente una card informativa che indica fino a quale data il servizio può restare fruibile anche dopo la richiesta di disattivazione, se tale informazione è disponibile.",
            "acceptance_criteria": [
                "La pagina di disattivazione automatica mostra i dati principali dell'abbonamento.",
                "La pagina di disattivazione automatica mostra una card con dati dell'intestatario precompilati.",
                "I dati dell'intestatario possono essere modificati tramite icona matita se consentito.",
                "La pagina può mostrare fino a 25 campi aggiuntivi richiesti dal merchant.",
                "I campi aggiuntivi rispettano obbligatorietà, vincoli di editabilità ed eventuali helper.",
                "La pagina può mostrare una card informativa sulla data di fruibilità del servizio dopo la richiesta di disattivazione."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [
                "App Poste"
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
            "title": "Processo di disattivazione automatica con autorizzazione PosteID",
            "description": "Dopo aver verificato e compilato quanto richiesto, l’utente prosegue con Continua, inserisce il codice PosteID e, in caso di esito positivo, l’APP inoltra la richiesta di disattivazione automatica al backend, che la propaga al partner/merchant.",
            "acceptance_criteria": [
                "L'utente prosegue con Continua dopo la compilazione dei dati.",
                "L'utente inserisce il codice PosteID.",
                "L'APP inoltra la richiesta di disattivazione automatica al backend in caso di esito positivo.",
                "Il backend propaga la richiesta al partner/merchant."
            ],
            "business_rules": [],
            "systems": [
                "App Poste",
                "PosteID",
                "Backend"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Gestione dello stato In corso di disattivazione e disabilitazione azioni in conflitto",
            "description": "La disattivazione potrebbe non essere immediata (es. aggiornamenti asincroni tra sistemi). In questi casi l’abbonamento viene gestito con uno stato intermedio In corso di disattivazione, che indica che la richiesta è stata presa in carico ma l’allineamento non è ancora concluso. Finché permane questo stato: l’APP mostra una label informativa che chiarisce l’attesa di aggiornamento, le azioni potenzialmente in conflitto (es. Cambia piano, se presente) risultano disabilitate. A completamento dell’allineamento, lo stato passa a Disattivato e l’abbonamento viene rappresentato tra le ricorrenze non più attive secondo le regole di cruscotto.",
            "acceptance_criteria": [
                "Se la disattivazione non è immediata, l'abbonamento assume lo stato In corso di disattivazione.",
                "L'APP mostra una label informativa quando l'abbonamento è nello stato In corso di disattivazione.",
                "Le azioni potenzialmente in conflitto (es. Cambia piano) sono disabilitate nello stato In corso di disattivazione.",
                "Lo stato cambia a Disattivato al completamento dell'allineamento.",
                "L'abbonamento viene rappresentato tra le ricorrenze non più attive una volta Disattivato."
            ],
            "business_rules": [
                "Gli aggiornamenti tra sistemi possono essere asincroni."
            ],
            "systems": [
                "OneView"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Verifica della disponibilità dell'azione di disattivazione tramite servizio tecnico",
            "description": "Al tap sulla CTA Disattiva abbonamento, il Front End verifica preliminarmente che per la subscription selezionata sia disponibile l'azione di cancellazione. La verifica viene effettuata tramite il servizio di ricerca delle azioni disponibili, che restituisce l'elenco delle operazioni supportate per la specifica subscription attraverso il campo supportedActions. L'azione risulta disponibile in presenza del valore CANCEL.",
            "acceptance_criteria": [
                "Il Front End verifica la disponibilità dell'azione di cancellazione dopo il tap sulla CTA Disattiva abbonamento.",
                "La verifica avviene tramite il servizio di ricerca delle azioni disponibili.",
                "L'azione è considerata disponibile se CANCEL è presente in supportedActions."
            ],
            "business_rules": [],
            "systems": [
                "Front End"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Avvio del processo di disattivazione tramite API",
            "description": "A seguito della selezione della funzionalità Disattiva abbonamento, il Front End invoca il servizio POST /oneapp/pagauto/api/v1/recurrences/actions passando l'identificativo della subscription e l'azione CANCEL. Il servizio restituisce le informazioni necessarie all'avvio del processo, tra cui: l'identificativo univoco dell'operazione (actionId), lo stato iniziale dell'azione e l'eventuale survey contenente i campi richiesti dal merchant (actionSurvey). Il Front End utilizza le informazioni ricevute per costruire dinamicamente la schermata di disattivazione, esponendo i campi richiesti e applicando le regole di obbligatorietà, editabilità e validazione restituite dai sistemi a valle.",
            "acceptance_criteria": [
                "Il Front End invoca POST /oneapp/pagauto/api/v1/recurrences/actions con subscriptionId e CANCEL.",
                "Il servizio restituisce actionId, stato iniziale dell'azione e actionSurvey.",
                "Il Front End costruisce la schermata di disattivazione dinamicamente basandosi su actionSurvey.",
                "La schermata applica regole di obbligatorietà, editabilità e validazione."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "Back End APP"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "2. Specifiche Tecniche"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35192- DISATTIVAZIONE AUTOMATICA DELL'ABBONAMENTO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35192",
            "confluence_id": null,
            "title": "Invio dati survey e finalizzazione richiesta di disattivazione",
            "description": "Una volta completata la compilazione dei dati richiesti, il Front End invia le informazioni raccolte tramite il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} trasmettendo: l'identificativo della survey, le risposte fornite dall'utente e gli eventuali dati di contesto richiesti dal merchant. Il servizio restituisce il challenge necessario per l'esecuzione dell'operazione e, a valle del completamento della SCA tramite PosteID, il Front End richiama PUT /oneapp/pagauto/api/v1/recurrences/actions/{actionId} per finalizzare la richiesta di cancellazione.",
            "acceptance_criteria": [
                "Il Front End invia i dati raccolti tramite POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId}.",
                "Il payload include l'identificativo della survey, le risposte dell'utente e dati di contesto.",
                "Il servizio restituisce il challenge.",
                "Dopo SCA con PosteID, il Front End richiama PUT /oneapp/pagauto/api/v1/recurrences/actions/{actionId}.",
                "PUT /oneapp/pagauto/api/v1/recurrences/actions/{actionId} finalizza la richiesta di cancellazione."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "Back End APP",
                "PosteID"
            ],
            "platforms": [
                "App Poste"
            ],
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
            "description": "A seguito dell'aggiornamento dello stato dell'operazione, il Back End APP pubblica l'evento applicativo destinato ai sistemi di notifica e Bacheca.",
            "acceptance_criteria": [
                "Il Back End APP pubblica un evento applicativo dopo l'aggiornamento dello stato dell'operazione.",
                "L'evento è destinato ai sistemi di notifica e Bacheca."
            ],
            "business_rules": [
                "L'evento è come descritto nella AF specifica ONP-37197."
            ],
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
            "title": "Flusso di cambio piano per abbonamento",
            "description": "La funzionalità di cambio piano consente a un utente autenticato in App di modificare il piano associato a un abbonamento, partendo dal funnel Gestisci abbonamento. L’operazione si svolge in uno scenario guidato a step, che accompagna l’utente dalla scelta dell’azione fino alla conferma.",
            "acceptance_criteria": [
                "L'utente autenticato può modificare il piano di un abbonamento.",
                "Il flusso inizia dal funnel Gestisci abbonamento.",
                "L'operazione segue uno scenario guidato a step."
            ],
            "business_rules": [
                "La disponibilità del cambio piano, la lista dei piani selezionabili e la raccolta di dati aggiuntivi sono determinati dinamicamente dai sistemi esterni.",
                "Il flusso mantiene coerenza con le regole del singolo merchant."
            ],
            "systems": [],
            "platforms": [
                "App Poste"
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
            "title": "Interfaccia utente della pagina iniziale del flusso Cambio piano (Step 1/3)",
            "description": "La pagina iniziale del flusso Cambio piano (Step 1/3) è composta da un Titolo, dati dell’abbonamento, e una Card Intestatario con dati utente precompilati e non modificabili (nome, cognome, beneficiario, strumento di pagamento, dati del piano attualmente associato all’abbonamento, se disponibili nel contesto della subscription). Include una CTA Continua per avviare l’operazione di cambio piano e recuperare le eventuali informazioni necessarie alla costruzione dello step successivo.",
            "acceptance_criteria": [
                "La pagina iniziale mostra un Titolo.",
                "La pagina mostra i dati dell'abbonamento.",
                "È presente una Card Intestatario.",
                "La Card Intestatario mostra nome e cognome precompilati e non modificabili.",
                "La Card Intestatario mostra beneficiario precompilato e non modificabile.",
                "La Card Intestatario mostra strumento di pagamento precompilato e non modificabile.",
                "La Card Intestatario mostra dati del piano attualmente associato se disponibili.",
                "È presente una CTA Continua.",
                "Al tap sulla CTA Continua, l'operazione di cambio piano viene avviata.",
                "Al tap sulla CTA Continua, vengono recuperate le informazioni per lo step successivo."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "1.3 UX / UI, Pagina iniziale step 1/3"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Interfaccia utente della pagina Dati del flusso Cambio piano (Step 2/3)",
            "description": "La pagina Dati (Step 2/3) espone i campi richiesti dal merchant sulla base delle regole ricevute: i campi possono essere precompilati, obbligatori, opzionali, modificabili o in sola lettura. Sono presenti Nome e Cognome dell’intestatario (non modificabili), dati dell’intestatario modificabili (email, cellulare) ove previsti dalla survey, ed eventuali altri campi dinamici richiesti dal merchant (fino a un massimo di 25), gestiti secondo le regole di visibilità, obbligatorietà e modificabilità ricevute. Include una CTA Continua.",
            "acceptance_criteria": [
                "La pagina Dati mostra campi richiesti dal merchant.",
                "I campi rispettano le regole di precompilazione, obbligatorietà, opzionalità, modificabilità o sola lettura.",
                "Nome e Cognome dell'intestatario sono visualizzati e non modificabili.",
                "Email e numero di cellulare sono modificabili se previsti dalla survey.",
                "Fino a 25 altri campi dinamici sono visualizzati con regole specifiche.",
                "È presente una CTA Continua.",
                "Al tap sulla CTA Continua, i dati confermati vengono inviati per validazione.",
                "Se la validazione ha esito positivo, il flusso prosegue con la pagina Cambia piano."
            ],
            "business_rules": [
                "I campi sono esposti in base alle regole ricevute dal merchant.",
                "La validazione positiva dei dati permette di proseguire al prossimo step."
            ],
            "systems": [
                "FE APP",
                "BE APP"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "1.3 UX / UI, 2/3 Dati"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Interfaccia utente della pagina Cambia piano per selezione (Step 3/3)",
            "description": "La pagina Cambia piano (Step 3/3) consente all’utente di selezionare il nuovo piano tra quelli disponibili per l’abbonamento selezionato. La pagina è composta da card dei piani disponibili, generate in modo dinamico sulla base dei dati restituiti dai servizi. Ogni card rappresenta un piano selezionabile e può contenere, in funzione di quanto restituito dal merchant: nome del piano, importo e periodicità, eventuali dettagli o descrizioni del piano. L’utente può selezionare un solo piano. Include una CTA Continua, abilitata solo dopo aver selezionato uno dei piani disponibili.",
            "acceptance_criteria": [
                "La pagina Cambia piano mostra card dei piani disponibili.",
                "Le card sono generate dinamicamente dai servizi.",
                "Ogni card mostra nome, importo, periodicità e dettagli del piano.",
                "L'utente può selezionare un solo piano.",
                "È presente una CTA Continua.",
                "La CTA Continua è abilitata solo dopo la selezione di un piano."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "1.3 UX / UI, Pagina Cambia piano step 3/3"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Interfaccia utente della pagina Riepilogo e conferma per il cambio piano",
            "description": "La pagina Riepilogo mostra l'Operazione (es. Cambio piano abbonamento), i dati dell’Intestatario, l'Esercente, il Piano selezionato e l'Importo del nuovo piano. Include una CTA Continua per aprire il drawer modale di conferma dell’operazione. A valle della pagina di riepilogo, l’utente visualizza un drawer modale di conferma dell’operazione. La conferma dal drawer avvia la fase autorizzativa SCA tramite PosteID. Dopo l’autorizzazione, l’App mostra la TYP di esito: conferma/presa in carico in caso di esito positivo, oppure schermata KO in caso di errore.",
            "acceptance_criteria": [
                "La pagina Riepilogo mostra l'Operazione.",
                "La pagina Riepilogo mostra i dati dell'Intestatario raccolti e confermati.",
                "La pagina Riepilogo mostra l'Esercente.",
                "La pagina Riepilogo mostra il Piano selezionato.",
                "La pagina Riepilogo mostra l'Importo del nuovo piano.",
                "È presente una CTA Continua.",
                "Al tap sulla CTA Continua, si apre un drawer modale di conferma.",
                "La conferma dal drawer avvia la fase autorizzativa SCA tramite PosteID.",
                "L'App mostra una TYP di esito (OK o KO)."
            ],
            "business_rules": [],
            "systems": [
                "PosteID"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Aggiornamento asincrono dei dati Data di attivazione e Importo nella pagina foglia dopo il cambio piano",
            "description": "Dopo la TYP di cambio piano, in caso di esito OK, nella pagina foglia dell’abbonamento i campi Data di attivazione e Importo si aggiornano in funzione del verificarsi o meno del pagamento del nuovo piano contestualmente al cambio. Se il pagamento è avvenuto contestualmente al cambio piano, Data di attivazione e Importo si aggiornano in modo asincrono. Fino all’aggiornamento effettivo, ci sarà uno stato intermedio nei sistemi di OneView e, lato FE APP, nella pagina Gestisci abbonamento la card di azione è inibita ed informa l’utente che: il piano è stato cambiato e i dati si aggiorneranno a breve. La card torna attiva quando i dati risultano aggiornati nella pagina foglia e lo stato cambia nei sistemi di OneView. Se il pagamento non è avvenuto contestualmente al cambio piano, Data di attivazione e Importo si aggiornano al primo pagamento/addebito periodico del nuovo piano. Fino all’aggiornamento, è presente la stessa card informativa in Gestisci abbonamento e la card non deve più essere visibile una volta allineati i dati in pagina foglia.",
            "acceptance_criteria": [
                "I campi Data di attivazione e Importo si aggiornano dopo la TYP di cambio piano OK.",
                "L'aggiornamento è asincrono se il pagamento è contestuale.",
                "L'aggiornamento avviene al primo pagamento se non contestuale.",
                "Una card informativa appare nella pagina Gestisci abbonamento fino all'aggiornamento.",
                "La card informativa inibisce l'azione.",
                "La card informativa scompare o l'azione diventa attiva dopo l'aggiornamento dei dati."
            ],
            "business_rules": [
                "Lo stato intermedio nei sistemi di OneView inibisce la card di azione.",
                "Il BE APP e One View non espongono i dati in maniera sincrona, per la natura stessa del data office, basata sul BATCH."
            ],
            "systems": [
                "OneView",
                "BE APP",
                "Data Office"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "1.3 UX / UI, Approfondimento sui sistemi BE APP"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Verifica della disponibilità dell'azione di cambio piano tramite servizio tecnico",
            "description": "Al tap sulla voce Cambia piano presente nella pagina di gestione dell’abbonamento, il FE verifica preliminarmente che l’azione sia tra quelle supportate per la subscription selezionata. La disponibilità dell’operazione viene determinata tramite il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/search. Il servizio restituisce le informazioni identificative della subscription e l’elenco delle operazioni consentite attraverso il campo supportedActions. L’azione di cambio piano risulta disponibile esclusivamente nel caso in cui l’elenco delle azioni supportate contenga il valore CHANGE_PLAN.",
            "acceptance_criteria": [
                "Il Front End invoca POST /oneapp/pagauto/api/v1/recurrences/actions/search dopo il tap su Cambia piano.",
                "Il servizio verifica le operazioni consentite per la subscription.",
                "L'azione di cambio piano è disponibile se CHANGE_PLAN è presente in supportedActions."
            ],
            "business_rules": [],
            "systems": [
                "Front End"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Avvio del processo di cambio piano tramite API",
            "description": "Una volta selezionata l’azione nella pagina di snodo, il FE invoca il servizio POST /oneapp/pagauto/api/v1/recurrences/actions passando le informazioni identificative della subscription (subscriptionId, serviceId) e l’azione richiesta (action: CHANGE_PLAN). Il servizio restituisce le informazioni necessarie all’avvio del processo, tra cui: l’identificativo univoco dell’operazione (actionId) e l’eventuale survey contenente i campi richiesti dal merchant (actionSurvey) con le relative regole di visibilità, editabilità e obbligatorietà (anagrafica, email, cellulare ed eventuali campi dinamici aggiuntivi fino a 25). Il BE APP associa l’actionId restituito da Mastercard alla relativa subscriptionId, mantenendo il contesto per le fasi successive del processo. Il Front End utilizza tali informazioni per costruire dinamicamente la schermata di compilazione dati dello Step 2 di 3.",
            "acceptance_criteria": [
                "Il Front End invoca POST /oneapp/pagauto/api/v1/recurrences/actions con i parametri specificati.",
                "Il servizio restituisce actionId e actionSurvey.",
                "actionSurvey contiene regole per i campi (anagrafica, email, cellulare, campi dinamici).",
                "Il Back End APP associa actionId alla subscriptionId.",
                "Il Front End costruisce la schermata di compilazione dati dinamicamente."
            ],
            "business_rules": [],
            "systems": [
                "FE APP",
                "BE APP",
                "Mastercard"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Invio dati survey e recupero piani selezionabili per cambio piano",
            "description": "Il Front End invoca il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} trasmettendo nel payload le risposte fornite dall’utente ai campi della survey. Il servizio valida i dati e restituisce al Front End l’elenco di tutti i piani effettivamente selezionabili per quell’abbonamento, comprensivi di: identificativo della survey, le risposte fornite dall'utente, gli eventuali dati di contesto richiesti dal merchant. Il Front End utilizza queste informazioni per popolare dinamicamente le card di selezione nella schermata Cambia piano (Step 3 di 3) e nel successivo Riepilogo.",
            "acceptance_criteria": [
                "Il Front End invoca POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} con le risposte utente.",
                "Il servizio valida i dati.",
                "Il servizio restituisce l'elenco dei piani selezionabili.",
                "L'elenco include identificativo survey, risposte e dati di contesto.",
                "Il Front End popola le card di selezione e il Riepilogo dinamicamente."
            ],
            "business_rules": [],
            "systems": [
                "Front End",
                "Back End APP"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Richiesta challenge e autorizzazione SCA tramite PosteID per cambio piano",
            "description": "A valle della pagina di riepilogo, al tap sulla CTA Conferma all’interno del drawer modale informativo (\"Vuoi cambiare il piano del tuo abbonamento?\"), il FE invoca il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId}/challenges trasmettendo l’identificativo del piano selezionato dall’utente. Il servizio predispone la transazione autorizzativa verso i sistemi a valle e restituisce il challenge necessario per l'avvio della SCA. Il Front End riceve la challenge firmata e attiva la schermata per l'inserimento del codice PosteID.",
            "acceptance_criteria": [
                "Il Front End invoca POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId}/challenges dopo la conferma nel drawer.",
                "Il payload include l'identificativo del piano selezionato.",
                "Il servizio predispone la transazione autorizzativa.",
                "Il servizio restituisce il challenge.",
                "Il Front End riceve il challenge firmato.",
                "Il Front End attiva la schermata per l'inserimento del codice PosteID."
            ],
            "business_rules": [],
            "systems": [
                "FE APP",
                "BE APP",
                "PosteID"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Finalizzazione della transazione di cambio piano dopo autorizzazione",
            "description": "A valle del corretto inserimento e validazione del codice PosteID da parte dell’utente, il Front End invoca nuovamente il servizio POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} inviando una request alleggerita contenente esclusivamente il dato autorizzativo firmato. Il BE APP verifica la validità del challenge firmato ed esegue la transazione dispositiva verso il merchant.",
            "acceptance_criteria": [
                "Il Front End invoca POST /oneapp/pagauto/api/v1/recurrences/actions/{actionId} dopo validazione PosteID.",
                "La request alleggerita contiene signedChallenge.",
                "Il Back End APP verifica la validità del challenge firmato.",
                "Il Back End APP esegue la transazione dispositiva verso il merchant."
            ],
            "business_rules": [],
            "systems": [
                "FE APP",
                "BE APP",
                "Mastercard"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Gestione dell'esito del cambio piano e pubblicazione eventi applicativi",
            "description": "A seguito dell'esecuzione dell'operazione, il BE APP recepisce lo stato restituito da Mastercard tramite l’oggetto actionState e lo rende disponibile al FE per la corretta gestione dell'esito del processo: in caso di esito positivo/preso in carico (status = SUCCESSFUL o IN_PROGRESS), il FE reindirizza l'utente alla TYP di conferma; in caso di errore, viene presentata la schermata di errore dedicata. In caso di completamento del cambio piano, il Back End provvede inoltre a costruire e pubblicare l’evento applicativo sul topic Kafka per l’allineamento asincrono dei sistemi di notifica e bacheca.",
            "acceptance_criteria": [
                "Il Back End APP recepisce actionState da Mastercard.",
                "Il Back End APP rende actionState disponibile al Front End.",
                "Se status è SUCCESSFUL o IN_PROGRESS, il Front End reindirizza alla TYP di conferma.",
                "Se si verifica un errore, viene mostrata la schermata di errore dedicata.",
                "Il Back End APP pubblica l'evento applicativo sul topic Kafka.",
                "L'evento è destinato all'allineamento asincrono di notifica e bacheca."
            ],
            "business_rules": [
                "Per la mappatura degli stati possibili, fare riferimento a quanto descritto nella AF ONP-35208.",
                "Per la funzionalità di change plan, la documentazione Mastercard indica una gestione sincrona dell’esito.",
                "Il frontend, se status = COMPLETATO, mostra la TYP di conferma operazione con esito OK."
            ],
            "systems": [
                "FE APP",
                "BE APP",
                "Mastercard",
                "Kafka",
                "sistemi di notifica",
                "Bacheca"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Gestione errore tecnico in caso di fallimento chiamata Mastercard per cambio piano",
            "description": "Se, la chiamata verso Mastercard fallisce, il BE App restituisce un errore tecnico al FE (es. 400 o codice interno dedicato) e non persiste alcun mapping actionId ↔ subscriptionId. Il FE mostra una pagina/messaggio di errore coerente con la UI.",
            "acceptance_criteria": [
                "Se la chiamata a Mastercard fallisce, il Back End App restituisce un errore tecnico al Front End.",
                "Il Back End App non persiste il mapping actionId ↔ subscriptionId.",
                "Il Front End mostra una pagina/messaggio di errore coerente con la UI."
            ],
            "business_rules": [],
            "systems": [
                "FE APP",
                "BE APP",
                "Mastercard"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "3 Gestione Errori"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35194- CAMBIO PIANO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35194",
            "confluence_id": null,
            "title": "Gestione della CTA Cambia piano in caso di indisponibilità dell'azione",
            "description": "In caso di mancata disponibilità dell'azione (CHANGE_PLAN non presente in supportedActions) o di errore nella verifica preliminare, la CTA non viene abilitata e non viene avviata alcuna azione di cambio piano.",
            "acceptance_criteria": [
                "La CTA Cambia piano non è abilitata se CHANGE_PLAN non è presente in supportedActions.",
                "La CTA Cambia piano non è abilitata in caso di errore nella verifica preliminare.",
                "Nessuna azione di cambio piano viene avviata in questi casi."
            ],
            "business_rules": [],
            "systems": [
                "Front End"
            ],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "3 Gestione Errori"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35208- POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35208",
            "confluence_id": null,
            "title": "Gestione dinamica delle Thank You Page (TYP) con messaggi personalizzati",
            "description": "L’obiettivo della funzionalità è gestire in modo dinamico le TYP dell’APP in seguito a un’operazione di gestione dell’abbonamento, mostrando messaggi personalizzati sulla base della risposta del Merchant. Il sistema dovrà mappare le risposte provenienti dai sistemi di BE e tradurle in una card visibile, contenente un messaggio specifico per ciascun scenario.",
            "acceptance_criteria": [
                "Le TYP sono gestite dinamicamente.",
                "I messaggi nelle TYP sono personalizzati in base alla risposta del Merchant.",
                "Il sistema mappa le risposte dai sistemi di Back End.",
                "Le risposte sono tradotte in una card visibile con messaggio specifico per scenario."
            ],
            "business_rules": [],
            "systems": [
                "BE APP"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Mappatura stato Back End APP e UI per card Cambio piano",
            "description": "Quando il Back End APP ha lo stato ATTIVO per un cambio piano, l'UI e lo stato Front End APP sono ATTIVO. Quando il Back End APP ha lo stato CAMBIATO per un cambio piano, l'UI e lo stato Front End APP sono ATTIVO.",
            "acceptance_criteria": [
                "Se stato BE APP = ATTIVO per cambio piano, stato FE APP = ATTIVO.",
                "Se stato BE APP = CAMBIATO per cambio piano, stato FE APP = ATTIVO."
            ],
            "business_rules": [],
            "systems": [
                "BE APP",
                "FE APP"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Mappatura stato Back End APP e UI per card Disattivazione automatica abbonamento",
            "description": "Quando il Back End APP ha lo stato ATTIVO per disattivazione abbonamento automatica, l'UI e lo stato Front End APP sono ATTIVO. Quando il Back End APP ha lo stato IN CORSO DI SOSPENSIONE per disattivazione abbonamento automatica, l'UI e lo stato Front End APP sono IN CORSO DI DISATTIVAZIONE. Quando il Back End APP ha lo stato DISATTIVATO per disattivazione abbonamento automatica, l'UI e lo stato Front End APP sono DISATTIVATO.",
            "acceptance_criteria": [
                "Se stato BE APP = ATTIVO per disattivazione automatica, stato FE APP = ATTIVO.",
                "Se stato BE APP = IN CORSO DI SOSPENSIONE per disattivazione automatica, stato FE APP = IN CORSO DI DISATTIVAZIONE.",
                "Se stato BE APP = DISATTIVATO per disattivazione automatica, stato FE APP = DISATTIVATO."
            ],
            "business_rules": [],
            "systems": [
                "BE APP",
                "FE APP"
            ],
            "platforms": [
                "App Poste"
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
            "title": "Mappatura stati per Thank You Page (TYP) di cambio piano",
            "description": "La Thank You Page per il cambio piano può mostrare uno stato COMPLETATO o KO.",
            "acceptance_criteria": [
                "La TYP di cambio piano mostra lo stato COMPLETATO per esito positivo.",
                "La TYP di cambio piano mostra lo stato KO per esito negativo."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "1.3 UX / UI, Thank you pages"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35208- POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35208",
            "confluence_id": null,
            "title": "Mappatura stati per Thank You Page (TYP) di disattivazione abbonamento",
            "description": "La Thank You Page per la disattivazione abbonamento può mostrare uno stato IN CORSO o COMPLETATO o KO.",
            "acceptance_criteria": [
                "La TYP di disattivazione abbonamento mostra lo stato IN CORSO.",
                "La TYP di disattivazione abbonamento mostra lo stato COMPLETATO per esito positivo.",
                "La TYP di disattivazione abbonamento mostra lo stato KO per esito negativo."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "1.3 UX / UI, Thank you pages"
        },
        {
            "source": "CONFLUENCE",
            "source_id": "ONP-35208- POSSIBILI ESITI DELLE OPERAZIONI e CARD DI CAMBIO STATO.md",
            "iniziativa_id": null,
            "epic_id": null,
            "jira_id": "ONP-35208",
            "confluence_id": null,
            "title": "Mappatura stati per Thank You Page (TYP) di Recesso del Servizio",
            "description": "La Thank You Page per il Recesso del Servizio può mostrare uno stato COMPLETATO.",
            "acceptance_criteria": [
                "La TYP di Recesso del Servizio mostra lo stato COMPLETATO."
            ],
            "business_rules": [],
            "systems": [],
            "platforms": [
                "App Poste"
            ],
            "source_reference": "1.3 UX / UI, Thank you pages"
        }
    ]
}