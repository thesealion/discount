import base64
from datetime import datetime, timezone
import struct

from fastapi import FastAPI, HTTPException

EPOCH = datetime(2022, 5, 2, 0, 0, 0, tzinfo=timezone.utc)

app = FastAPI()
storage = []


@app.post("/generate/{brand}")
async def generate(brand: str, number: int = 10):
    if number > 128000:
        raise HTTPException(status_code=400, detail="Generating more than 128,000 codes at once is not supported.")

    codes = gen_codes(number)
    storage.extend({"brand": brand, "code": code, "used": False} for code in codes)
    return {"result": codes}


@app.post("/fetch/{brand}")
async def fetch(brand: str):
    for row in storage:
        if row["brand"] == brand and not row["used"]:
            row["used"] = True
            return {"result": row["code"]}
    raise HTTPException(status_code=404)


def gen_codes(N):
    """Generate 10-character case-insensitive unique codes.

    Creates 48-bit values encoded with base32.
    Uses the current timestamp (the number of milliseconds since a custom epoch,
    41 bits) and a counter (7 bits). Thus, 128,000 unique codes can be generated
    every second for up to 69 years.
    Concurrent use requires locking.
    """

    codes = []
    delta = datetime.now(timezone.utc) - EPOCH
    ts = delta.seconds * 1000 + (delta.microseconds // 1000)
    while N > 0:
        for i in range(min(N, 128)):
            data = struct.pack('<q', (ts << 7) | i)[:6]
            codes.append(base64.b32encode(data).decode().strip('='))
            N -= 1
        ts += 1
    return codes
