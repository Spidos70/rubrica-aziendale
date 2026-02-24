# Ferie Estive 2026 – Guida al deploy su VPS Aruba (Docker)

## Struttura

```
FerieEstive/
├── app.py                  # Applicazione Flask
├── requirements.txt
├── Dockerfile
├── docker-compose.yml      # Configurazione Docker Compose
├── nginx/
│   └── nginx.conf          # Reverse proxy
├── static/css/style.css
├── templates/              # HTML Jinja2
│   ├── base.html
│   ├── login.html
│   ├── selezione_dipendente.html
│   ├── dashboard.html
│   └── admin.html
└── data/                   # Database SQLite (creato al primo avvio)
    └── ferie.db
```

## Credenziali di accesso

| Tipo | Login | Password | Note |
|------|-------|----------|------|
| Dipendenti | `utenteGT` | `FFG_GT` | Condivisa tra tutti |
| Amministratore | `admin` | `AdminFerie2026!` | Pannello /admin |

Modifica le credenziali in `docker-compose.yml` prima del deploy.

## Deploy sul VPS Aruba

### 1. Copia i file sul VPS

```bash
# Da locale – copia l'intera cartella
scp -r ./FerieEstive/ utente@IP-VPS:/opt/ferie-estive/

# oppure con rsync
rsync -avz ./FerieEstive/ utente@IP-VPS:/opt/ferie-estive/
```

### 2. Sul VPS – build e avvio

```bash
cd /opt/ferie-estive

# Build immagine e avvio in background
docker compose up -d --build

# Verifica che i container siano in esecuzione
docker compose ps

# Controlla i log
docker compose logs -f
```

### 3. Prima configurazione (admin)

1. Apri `http://IP-VPS` nel browser
2. Accedi con `admin` / `AdminFerie2026!`
3. Vai alla tab **Dipendenti** → aggiungi i nomi dei dipendenti
4. Vai alla tab **Settimane** → abilita/disabilita le settimane selezionabili
   - Default: settimane 22–38 (fine maggio → metà settembre)
5. Vai alla tab **Impostazioni** → configura il massimo per settimana e la 4ª settimana

### 4. Accesso dipendenti

1. Apri `http://IP-VPS`
2. Login con `utenteGT` / `FFG_GT`
3. Seleziona il proprio nome dall'elenco
4. Scegli le settimane dal calendario e clicca **Salva**

---

## Funzionalità

### Dipendenti
- **Settimana aggiuntiva** (1ª scelta) – obbligatoria
- **Settimana di riserva** – opzionale
- **4ª settimana** – opzionale, abilitabile/disabilitabile dall'admin

### Amministratore
- Aggiunta/disattivazione dipendenti
- Configurazione settimane disponibili con toggle on/off
- Impostazione max dipendenti per settimana
- Visibilità completa di tutte le scelte
- Esportazione CSV

---

## Comandi utili

```bash
# Riavvio
docker compose restart

# Stop
docker compose down

# Rinnova solo l'app dopo modifiche al codice
docker compose up -d --build app

# Backup database
cp data/ferie.db data/ferie_backup_$(date +%Y%m%d).db

# Log in tempo reale
docker compose logs -f app
```

## Aggiornamento credenziali

Modifica le variabili in `docker-compose.yml`:
```yaml
environment:
  - APP_USERNAME=utenteGT      # username dipendenti
  - APP_PASSWORD=FFG_GT         # password dipendenti
  - ADMIN_PASSWORD=NuovaPassword!
  - SECRET_KEY=una-stringa-random-lunga
```

Poi riavvia: `docker compose up -d`

## HTTPS (opzionale, con Certbot)

Se hai un dominio puntato sul VPS:

```bash
# Installa certbot
apt install certbot python3-certbot-nginx

# Ottieni certificato (prima ferma nginx del compose)
docker compose stop nginx
certbot certonly --standalone -d tuodominio.it
docker compose start nginx
```

Poi modifica `nginx/nginx.conf` per aggiungere il blocco HTTPS su porta 443.
