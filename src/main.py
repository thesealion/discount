import base64
from datetime import datetime, timezone
import struct

from fastapi import FastAPI

EPOCH = datetime(2022, 5, 2, 0, 0, 0, tzinfo=timezone.utc)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": gen_codes(1000)}


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
    while len(codes) < N:
        for i in range(min(N, 128)):
            data = struct.pack('<q', (ts << 7) | i)[:6]
            codes.append(base64.b32encode(data).decode().strip('='))
        ts += 1
    return codes
