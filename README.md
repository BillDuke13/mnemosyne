# Mnemosyne Demo (Walrus + Sui + Mock Azure Face)

This demo shows the end-to-end flow for the Mnemosyne concept: a mock camera frame is “recognized” (no real Azure call), the recognized label is used to retrieve real on-chain memory metadata from Sui devnet and real memory content from Walrus testnet, then a prompt is rendered in the UI (and optionally spoken via macOS `say`).

## Deployed chain state (devnet)

- Package ID: `0x19df5b99556a1f786f9ed4bfe27ad649d7983c289747ed733e77dc84dfea4e47`
- MemoryBook ID (shared object): `0x8d11465046cb5e6f428051270d0cc636e06559066c16630ccd26a0609bf86f3b`
- Table ID (entries): `0xd94e3cf9b373f99d5f8eedec94489d022d0838c248e35d1e0ad74618fc5e589b`
- Entry map (ID → Walrus blob):
  - `0` (Family1-Dad) → `GohF9F8Um8zUdu3QyZdBw5BcjqI9nx5Oladod6GMIBk`
  - `1` (Family1-Mom) → `fegNUuP9T8Z1XVJGITjjAM3HD9-FM6OHPjH5R19wRRY`
  - `2` (Family1-Son) → `Gf0xoarmeZMB_fpyor2818hsz4GLEcghGQ8uBHuLgIM`

Walrus aggregator: `https://aggregator.walrus-testnet.walrus.space`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` to use the camera mock. Click **Start Camera**, then **Identify**. Selecting a face hint will map directly to the entry; leaving it blank cycles through the on-chain entries in order.

## What happens on Identify

1. Frontend captures a frame and posts to `/identify` (image is unused beyond validation; face recognition is mocked).
2. Backend reads Sui devnet dynamic fields from the MemoryBook table to resolve the chosen entry.
3. Backend downloads the Walrus blob for that entry, validates the SHA3-256 hash, and returns the structured memory.
4. Response renders as text; optional TTS via macOS `say` if `ENABLE_TTS=true`.

## Environment overrides

```
MNEMOSYNE_PACKAGE_ID=<pkg>
MNEMOSYNE_BOOK_ID=<object_id>
MNEMOSYNE_TABLE_ID=<table_id>
SUI_RPC=https://fullnode.devnet.sui.io
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
