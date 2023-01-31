# Informacje ogólne

Aplikacja została zaprojektowana przy wykorzystaniu modułu django oraz pythona w wersji 3.9.

Dane w aplikacji są przechowywane za pomocą domyślnej bazy danych sqlite3 w 4 tabelach:

* Users - dla użytkowników
* Tournaments - dla turniejów
* Players - dla graczy
* Score - dla wprowadzonych wyników

System został podzielony na dwie aplikacje (w rozumieniu modułu
django) jedna per niezależny zasób. Pierwszą z nich jest 'user' zawierająca w sobie API oraz logikę dotyczącą
użytkowników a drugą 'tournament' zawierającą API oraz logikę dotyczącą turniejów oraz graczy wraz z wynikami (jako że
są to zasoby podległe turniejowi).

Serwer uruchamia się domyślnie pod adresem 'localhost:8000'.

Projekt można uruchomić wywołując komendę 'python manage.py runserver'.

# Cechy specyficzne dla implementacji

### Użytkownicy:

W systemie znajdują się trzy rodzaje użytkowników, definiowane poprzez parametr 'usergroup'. Możliwe opcje to:

* 'admin' - dla administratora
* 'user' - dla zwykłego uzytkownika

Użytkownik anonimowy, jako że zgodnie ze specyfikacją systemu nie może wprowadzać zmian w zasobach jest oznaczany jako
brak użytkownika (None). Informacja o zalogowanym użytkowniku jest przekazywana za pomocą mechanizmu session pod
zmienną 'auth_user'.

Domyślnie w systemie znajduje się jeden użytkownik będący administratorem, o loginie 'admin' i haśle 'admin'.

### Turnieje:

Turniej może posiadać jeden z 3 możliwych stanów definiowanych za pomocą parametru 'status':

* 'draft' - stan początkowy - oznacza zaplanowany turniej, autoryzowani uzytkownicy mogą edytować dane turnieju oraz
  przypisanych do nich graczy
* 'active' - turniej aktywny - turniej przechodzi w ten stan, jeżeli jego data startowa jest wcześniejsza od obecnej
  daty na serwerze, w
  tym stanie autoryzowani uzytkownicy mogą wprowadzać wyniki pojedynków
* 'historic' - turniej zakończony - turniej przechodzi w ten stan w momencie kiedy zostanie podany wynik finałowego
  starcia

Warunek umożliwiający przejście turnieju ze stanu 'draft' do 'active' jest sprawdzany reaktywnie w momencie pobrania
danego turnieju z serwera. Podobnie dzieje się w w przypadku przejścia z 'active' do 'historic', warunek jest sprawdzany
w momencie wprowadzania wyniku do turnieju.

### Wyniki:

Drabinka turniejowa jest generowana rekurencyjnie w momencie przejścia turnieju w stan 'active'. Każdy wynik (poza
finałem) posiada identyfikator następnego pojedynku 'next_id' oraz tego które miejsce zajmie zwycięzca w następnej
rundzie 'next_position' z opcjami 'A' lub 'B'.

W przypadku podania liczby graczy niebędącej potęgą 2, turniej jest automatycznie uzupełniany do wymaganej liczby
graczy. "Szczęśliwi gracze", którzy w pierwszej turze nie otrzymali przeciwnika są awansowani do następnej rundy w
momencie, kiedy wprowadzono już wyniki wszystkich pozostałych pojedynków w danej turze.

### Zgodność z architekturą REST:

Zdecydowano się zastosować złoty środek pomiędzy pełną zgodnością z achitekturą REST a łatwością implementacji
interfejsu graficznego.

Wobec tego ścieżki do zasobów uskuteczniają schematy:

* /zasób/
* /zasób/id/
* /zasób/id/zasób_podległy/
* /zasób/id/zasób_podległy/id2/

Zastosowane zostały również odpowiednie metody HTTP:

* GET dla pobierania zasob(u/ów)
* POST dla dodawania nowych zasobów oraz ich modyfikacji
* DELETE dla usuwania zasobów

Nie została wykorzystana metoda PUT ze względu na brak jej dostępności z poziomu dokumentu HTML, a metoda DELETE jest
udostępniona jednak dokumenty HTML uzyskują ją poprzez wysłanie GET na <adres_zasobu>/delete (również ze względu na brak
implementacji metody DELETE w standardzie HTML5).

Zastosowane zostały odpowiednie kody statusów dla odpowiedzi serwera. Niezgodnością z architekturą REST są natomiast
zwracane
odpowiedzi serwera, ponieważ zamiast zwracać zasoby w czystej formie (zdefinowanych przez content_type) zwracają
przekierowania lub elementy interfejsu
graficznego.