import asyncio
import base64
import hashlib
import json
import os
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


PACKAGE_ID = os.getenv(
    "MNEMOSYNE_PACKAGE_ID",
    "0x19df5b99556a1f786f9ed4bfe27ad649d7983c289747ed733e77dc84dfea4e47",
)
MEMORY_BOOK_ID = os.getenv(
    "MNEMOSYNE_BOOK_ID",
    "0x8d11465046cb5e6f428051270d0cc636e06559066c16630ccd26a0609bf86f3b",
)
TABLE_ID = os.getenv(
    "MNEMOSYNE_TABLE_ID",
    "0xd94e3cf9b373f99d5f8eedec94489d022d0838c248e35d1e0ad74618fc5e589b",
)
SUI_RPC = os.getenv("SUI_RPC", "https://fullnode.devnet.sui.io")
WALRUS_AGGREGATOR = os.getenv(
    "WALRUS_AGGREGATOR", "https://aggregator.walrus-testnet.walrus.space"
)
ENTRY_HINTS = json.loads(
    os.getenv(
        "MNEMOSYNE_ENTRY_HINTS",
        json.dumps({"Family1-Dad": 0, "Family1-Mom": 1, "Family1-Son": 2}),
    )
)
ENABLE_TTS = os.getenv("ENABLE_TTS", "").lower() in {"1", "true", "yes"}

app = FastAPI(title="Mnemosyne Demo", version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")


class IdentifyRequest(BaseModel):
    image: Optional[str] = None
    face_hint: Optional[str] = None


class MemoryEntry(BaseModel):
    entry_id: int
    label: str
    relationship: str
    walrus_blob_id: str
    last_interaction_unix_ms: int
    notes_hash_hex: str
    summary: str


async def rpc_call(method: str, params: List[Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            SUI_RPC,
            headers={"Content-Type": "application/json"},
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise HTTPException(status_code=502, detail=data["error"])
        return data["result"]


async def fetch_entry_ids() -> List[int]:
    result = await rpc_call(
        "suix_getDynamicFields",
        [TABLE_ID, None, 50],
    )
    return [int(item["name"]["value"]) for item in result.get("data", [])]


async def fetch_entry(entry_id: int) -> MemoryEntry:
    result = await rpc_call(
        "suix_getDynamicFieldObject",
        [TABLE_ID, {"type": "u64", "value": str(entry_id)}],
    )
    value = (
        result["data"]["content"]["fields"]["value"]["fields"]
        if "data" in result
        else result["content"]["fields"]["value"]["fields"]
    )
    notes_hash_bytes: List[int] = value["notes_hash"]
    notes_hash_hex = "".join(f"{b:02x}" for b in notes_hash_bytes)
    summary = await fetch_walrus_summary(value["walrus_blob_id"])
    return MemoryEntry(
        entry_id=entry_id,
        label=value["label"],
        relationship=value["relationship"],
        walrus_blob_id=value["walrus_blob_id"],
        last_interaction_unix_ms=int(value["last_interaction_unix_ms"]),
        notes_hash_hex=notes_hash_hex,
        summary=summary,
    )


async def fetch_walrus_summary(blob_id: str) -> str:
    url = f"{WALRUS_AGGREGATOR}/v1/blobs/{blob_id}"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        content = resp.content
    try:
        data = json.loads(content.decode())
        return data.get("summary", "")
    except json.JSONDecodeError:
        return content.decode(errors="ignore")


def verify_hash(summary: str, expected_hex: str) -> bool:
    digest = hashlib.sha3_256(summary.encode()).hexdigest()
    return digest == expected_hex


async def resolve_label(face_hint: Optional[str]) -> MemoryEntry:
    entry_ids = await fetch_entry_ids()
    candidates: List[MemoryEntry] = []
    for entry_id in entry_ids:
        candidates.append(await fetch_entry(entry_id))
    if face_hint:
        for entry in candidates:
            if entry.label.lower() == face_hint.lower():
                return entry
    if ENTRY_HINTS:
        for label, eid in ENTRY_HINTS.items():
            for entry in candidates:
                if entry.entry_id == eid or entry.label == label:
                    return entry
    return candidates[0]


async def speak(text: str) -> None:
    if not ENABLE_TTS:
        return
    try:
        proc = await asyncio.create_subprocess_exec("say", text)
        await proc.wait()
    except FileNotFoundError:
        # TTS not available; silently skip.
        return


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.post("/identify", response_model=MemoryEntry)
async def identify(req: IdentifyRequest):
    # image is accepted but only used for logging; recognition is mocked by face_hint.
    if req.image:
        try:
            base64.b64decode(req.image.split(",")[-1])
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"Invalid image payload: {exc}") from exc
    entry = await resolve_label(req.face_hint)
    if not verify_hash(entry.summary, entry.notes_hash_hex):
        raise HTTPException(status_code=500, detail="Summary hash verification failed")
    await speak(
        f"This is your {entry.relationship} named {entry.label}. "
        f"Recent memory: {entry.summary}"
    )
    return entry


@app.get("/health")
async def health():
    entry_ids = await fetch_entry_ids()
    return {
        "package_id": PACKAGE_ID,
        "memory_book_id": MEMORY_BOOK_ID,
        "table_id": TABLE_ID,
        "entry_count": len(entry_ids),
        "walrus_aggregator": WALRUS_AGGREGATOR,
        "sui_rpc": SUI_RPC,
    }
