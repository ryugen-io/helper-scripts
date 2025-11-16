# Claude CI/CD Skip System

Dieses Repository verwendet ein sicheres Skip-System für Claude CI/CD Workflows.

## Funktionsweise

Das System verhindert versehentliches oder unauthorisiertes Überspringen der Claude CI/CD Workflows durch Hash-Validierung.

### Zwei Sicherheitsstufen:

#### 1. Standard-Modus (Content-basiert)
Die `.skip` Datei muss exakt den folgenden Text enthalten:
```
SKIP_CLAUDE_CI_APPROVED
```

**SHA256 Hash:** `80960e69edf8e0868c81b3fa9eb415a5421d1e6ac6dc8e3abd640f3dd85c2f3c`

#### 2. Enhanced-Modus (Secret-basiert)
Setze ein GitHub Secret namens `SKIP_FILE_HASH` mit einem beliebigen SHA256 Hash. Nur `.skip` Dateien mit diesem exakten Hash werden akzeptiert.

## Verwendung

### Claude CI/CD deaktivieren:

**Standard-Modus:**
```bash
# Kopiere die Beispieldatei
cp .skip.example .skip

# Oder erstelle die Datei manuell
echo -n "SKIP_CLAUDE_CI_APPROVED" > .skip

# Committe und pushe
git add .skip
git commit -m "Deaktiviere Claude CI/CD temporär"
git push
```

**Enhanced-Modus (empfohlen für Production):**
```bash
# 1. Erstelle eine .skip Datei mit eigenem Inhalt
echo -n "MeinGeheimesSkipToken2024!" > .skip

# 2. Berechne den Hash
sha256sum .skip | awk '{print $1}'
# Beispiel Output: abc123def456...

# 3. Füge das Secret in GitHub hinzu:
#    Settings > Secrets and variables > Actions > New repository secret
#    Name: SKIP_FILE_HASH
#    Value: abc123def456...

# 4. Committe und pushe
git add .skip
git commit -m "Deaktiviere Claude CI/CD mit eigenem Token"
git push
```

### Claude CI/CD wieder aktivieren:

```bash
rm .skip
git add .skip
git commit -m "Aktiviere Claude CI/CD wieder"
git push
```

## Sicherheitsmerkmale

1. **Hash-Validierung**: Nicht jede `.skip` Datei wird akzeptiert
2. **Fallback-Logik**: Bei ungültiger `.skip` Datei läuft CI/CD normal weiter
3. **Audit-Trail**: Alle Skip-Versuche werden in den Workflow-Logs dokumentiert
4. **Flexibilität**: Unterstützt sowohl einfachen als auch Secret-basierten Modus

## Betroffene Workflows

- `.github/workflows/claude.yml` (Issue/PR Kommentare mit @claude)
- `.github/workflows/claude-code-review.yml` (Automatische PR Reviews)

## Workflow-Ausgaben

- ✅ No .skip file found - proceeding with Claude CI/CD
- ⏭️ Valid .skip file found (content verified) - Claude CI/CD will be skipped
- ⏭️ Valid .skip file found (hash verified) - Claude CI/CD will be skipped
- ⚠️ .skip file found but invalid content - proceeding with Claude CI/CD for security
- ⚠️ .skip file found but hash mismatch - proceeding with Claude CI/CD for security

## Eigenen Hash erstellen

```bash
# Erstelle beliebigen Text und berechne Hash
echo -n "DeinEigenerText" | sha256sum | awk '{print $1}'

# Oder verwende einen zufälligen Token
openssl rand -base64 32 | tee .skip | sha256sum | awk '{print $1}'
```
