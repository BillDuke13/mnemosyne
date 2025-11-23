# Mnemosyne Demo (Walrus + Sui + Mock Azure Face)

This demo shows the end-to-end flow for the Mnemosyne concept: a mock camera frame is “recognized” (no real Azure call), the recognized label is used to retrieve real on-chain memory metadata from Sui devnet and real memory content from Walrus testnet, then a prompt is rendered in the UI (and optionally spoken via macOS `say`).

## Deployed chain state (testnet)

- Package ID: `0x1c8db13f154371b87806ae5a54cf1d6e35c650a5b7ebae8c76f181e31dcc05be`
- MemoryBook ID (shared object): `0x5acdf1b6fc224fc054f014c153780439b417b5e8609ca02e3ff1ea7bacaf0726`
- Table ID (entries): `0x408592353531f028f9f6a4377bbacaba4ea3acca1121234fb55c3482da4c3ea3`
- Entry map (ID → Walrus blob):
  - `0` (Family1-Dad) → `GohF9F8Um8zUdu3QyZdBw5BcjqI9nx5Oladod6GMIBk` (hash `6660eb78937dad3a1f6774426da335821832f2c6719cd0491372b6a4e2399fc6`)
  - `1` (Family1-Mom) → `fegNUuP9T8Z1XVJGITjjAM3HD9-FM6OHPjH5R19wRRY` (hash `4f05a52a39e2d0603ee8239980a9ad8a4c809d6fac5ae0d80f0430d77eefda28`)
  - `2` (Family1-Son) → `Gf0xoarmeZMB_fpyor2818hsz4GLEcghGQ8uBHuLgIM` (hash `7a278bcc9044e43dc1803a7ab10ce41e0c249d7a8bcc7f1c18673ab04f4e0096`)

Walrus aggregator: `https://aggregator.walrus-testnet.walrus.space`  
Sui RPC (testnet): `https://fullnode.testnet.sui.io`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` to use the sample portrait mock (no real camera). Choose a portrait (Dad/Mom/Son) and click **Identify**; the backend reads testnet MemoryBook and Walrus blobs, then renders the memory prompt.

## What happens on Identify

1. Frontend captures a frame and posts to `/identify` (image is unused beyond validation; face recognition is mocked).
2. Backend reads Sui devnet dynamic fields from the MemoryBook table to resolve the chosen entry.
3. Backend downloads the Walrus blob for that entry, validates the SHA3-256 hash, and returns the structured memory.
4. Response renders as text; optional TTS via macOS `say` if `ENABLE_TTS=true`.

## Environment overrides

```
MNEMOSYNE_PACKAGE_ID=0x1c8db13f154371b87806ae5a54cf1d6e35c650a5b7ebae8c76f181e31dcc05be
MNEMOSYNE_BOOK_ID=0x5acdf1b6fc224fc054f014c153780439b417b5e8609ca02e3ff1ea7bacaf0726
MNEMOSYNE_TABLE_ID=0x408592353531f028f9f6a4377bbacaba4ea3acca1121234fb55c3482da4c3ea3
SUI_RPC=https://fullnode.testnet.sui.io
WALRUS_AGGREGATOR=https://aggregator.walrus-testnet.walrus.space
MNEMOSYNE_ENTRY_HINTS='{"Family1-Dad":0,"Family1-Mom":1,"Family1-Son":2}'
ENABLE_TTS=true   # enables macOS `say`
```

## Data sources

- Walrus blobs store real summaries in `data/family1_*.json` (uploaded to testnet).
- Move module `memory.move` manages on-chain MemoryBook and entries (u64 keys, shared object).

## Demo recording tips

- Keep the browser UI visible with the camera preview and the Result panel.
- Trigger one recognized match and one with a different hint to show the mapping.
- Include a terminal tailing the server logs if you want to show hash verification.
