import base64
from datetime import datetime, timezone
import os
import struct

from fastapi import Depends, FastAPI, HTTPException
import mysql.connector


EPOCH = datetime(2022, 5, 2, 0, 0, 0, tzinfo=timezone.utc)

app = FastAPI()


def get_db():
    cnx = mysql.connector.connect(user=os.environ['MYSQL_USER'], password=os.environ['MYSQL_PASSWORD'],
                                  host=os.environ['MYSQL_HOST'], database=os.environ['MYSQL_DATABASE'])
    try:
        yield cnx
    finally:
        cnx.close()


@app.post("/generate/{brand}")
async def generate(brand: str, number: int = 10, db=Depends(get_db)):
    if len(brand) > 20:
        raise HTTPException(status_code=400, detail="Brand names longer than 20 characters are not supported.")

    if number > 128000:
        raise HTTPException(status_code=400, detail="Generating more than 128,000 codes at once is not supported.")

    # TODO: use a distributed lock to lock code generation for the current brand
    codes = gen_codes(number)
    with db.cursor() as cursor:
        query = 'INSERT INTO codes (brand, code) VALUES (%s, %s)'
        cursor.executemany(query, [(brand, code) for code in codes])
        db.commit()
    return {"result": codes}


@app.post("/fetch/{brand}")
async def fetch(brand: str, db=Depends(get_db)):
    with db.cursor() as cursor:
        query = 'SELECT code FROM codes WHERE brand = %s AND used = FALSE LIMIT 1 FOR UPDATE SKIP LOCKED'
        cursor.execute(query, (brand,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404)
        code = row[0]
        query = 'UPDATE codes SET used = TRUE WHERE brand = %s AND code = %s'
        cursor.execute(query, (brand, code))
        db.commit()
    return {"result": code}


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
    # TODO: sleep until all the milliseconds we used have elapsed
    return codes
