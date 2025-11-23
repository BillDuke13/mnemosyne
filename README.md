# Mnemosyne Demo (Walrus + Sui + Mock Azure Face)

## Problem & Mission
Alzheimer’s patients lose not only facts but the *feeling of safety* with people they love. Mnemosyne is a cognitive prosthesis: it rebuilds “who is with me and why it matters” in real time, using verifiable on-chain memory and durable Walrus storage.

## What is Mnemosyne
Face → Memory Graph → Gentle Prompt. A captured portrait (mock Azure Face) maps to an on-chain MemoryBook entry, pulls a Walrus blob, verifies its hash, and surfaces a warm reminder the patient can trust. All state is live on Sui testnet and Walrus testnet.

## Why this demo wins (judge-fast bullets)
- Chain-verifiable memory graph (Sui shared objects, testnet, inspectable).
- Walrus real blobs, SHA3-256 integrity-checked; no central point of failure.
- Edge-first loop; swap mock camera for real device without changing APIs.
- Safety posture: public Azure sample portraits, no PII; integrity gating before display.
- Extensible cognition DAG: today a MemoryBook, tomorrow a relationship graph and time-aware recalls.
- Fully running: deployed package + shared object + blobs on public testnet.

## Architecture (text sketch)
Edge UI (portrait picker) → Mock Face ID → FastAPI → Sui MemoryBook (shared object) → Walrus blob fetch + hash verify → Prompt render (+ optional macOS TTS). No hidden services; everything can be opened in browser or Explorer.

## User experience flow
1) Pick a sample portrait (Dad/Mom/Son)  
2) Click **Identify**  
3) Backend reads Sui MemoryBook entry → pulls Walrus blob → verifies SHA3-256  
4) UI shows a gentle prompt: “This is your father. Last time you reviewed meds together.”  
5) Optional local TTS (macOS `say`) voices the prompt.

## Testnet deployment (live, inspectable)
- Package: `0x1c8db13f154371b87806ae5a54cf1d6e35c650a5b7ebae8c76f181e31dcc05be`
- MemoryBook (shared): `0x5acdf1b6fc224fc054f014c153780439b417b5e8609ca02e3ff1ea7bacaf0726`
- Table ID: `0x408592353531f028f9f6a4377bbacaba4ea3acca1121234fb55c3482da4c3ea3`
- Entries (ID → Walrus blob → hash):
  - 0 Family1-Dad → `GohF9F8Um8zUdu3QyZdBw5BcjqI9nx5Oladod6GMIBk` → `6660eb78937dad3a1f6774426da335821832f2c6719cd0491372b6a4e2399fc6`
  - 1 Family1-Mom → `fegNUuP9T8Z1XVJGITjjAM3HD9-FM6OHPjH5R19wRRY` → `4f05a52a39e2d0603ee8239980a9ad8a4c809d6fac5ae0d80f0430d77eefda28`
  - 2 Family1-Son → `Gf0xoarmeZMB_fpyor2818hsz4GLEcghGQ8uBHuLgIM` → `7a278bcc9044e43dc1803a7ab10ce41e0c249d7a8bcc7f1c18673ab04f4e0096`
- Walrus aggregator: `https://aggregator.walrus-testnet.walrus.space`  
- Sui RPC: `https://fullnode.testnet.sui.io`

Explorer links for judges:
- Package: https://explorer.sui.io/object/0x1c8db13f154371b87806ae5a54cf1d6e35c650a5b7ebae8c76f181e31dcc05be?network=testnet
- MemoryBook: https://explorer.sui.io/object/0x5acdf1b6fc224fc054f014c153780439b417b5e8609ca02e3ff1ea7bacaf0726?network=testnet
- Sample blob (Dad): https://aggregator.walrus-testnet.walrus.space/v1/blobs/GohF9F8Um8zUdu3QyZdBw5BcjqI9nx5Oladod6GMIBk

## Demo showcase (30-second script)
- Select “Dad” portrait → click Identify → see relation + last-summary prompt.  
- Switch to “Mom” and “Son” to prove multiple on-chain records.  
- Open a Walrus blob URL in a new tab to show real storage and matching hash.  
- (Optional) enable `ENABLE_TTS=true` to hear the prompt via macOS `say`.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000` → pick portrait → Identify.

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

## What happens on Identify
1) Frontend posts portrait data + hint to `/identify` (Face is mocked).  
2) Backend resolves MemoryBook entry from Sui testnet.  
3) Backend downloads Walrus blob, verifies SHA3-256 hash.  
4) Returns structured memory; UI renders prompt; optional local TTS.

## Safety & privacy posture
- No real faces or PII; Azure public sample portraits only.
- Integrity-gated rendering: hashes must match before display.
- Optional TTS is local-only; no cloud speech calls.

## Data sources
- Walrus blobs populated from `data/family1_*.json` (uploaded to testnet).
- Move module `memory.move` defines MemoryBook/MemoryEntry (u64 keys, shared object).

## Roadmap (beyond the demo)
- Relationship graph: caregivers/friends/doctors with richer edges and recency.
- Context cues: location/voice triggers for context-aware prompts.
- Remote updates: family uploads new memories → new Walrus blobs + on-chain refs.
- Hardware path: drop-in for glasses/phone camera feed using the same API surface.
