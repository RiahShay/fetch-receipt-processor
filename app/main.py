
import logging
import sys
import json
from receipt_processor import generate_id, calculate_points
from db import store_receipt, get_receipt_points
from fastapi import FastAPI, HTTPException, status, Body
from typing import Union, Any
import uvicorn

# Set up logging to record errors
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = FastAPI()


@app.get("/health")
def read_root():
    return {"status": "healthy"}


@app.post("/receipts/process")
def submit_receipt(
    payload: Any = Body(None)
):
    try:
        receipt_id = generate_id(json.dumps(payload))
        receipt_points = calculate_points(json.dumps(payload))
        db_status = store_receipt(str(receipt_id), receipt_points, payload)
        if (db_status is not None):
            return {"id": receipt_id}
        else:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error processing receipt.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        logging.exception(e) 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The receipt is invalid.")



@app.get("/receipts/{receipt_id}/points")
def get_points(receipt_id: str):
    receipt_pts = get_receipt_points(receipt_id)
    print(receipt_pts)
    if (receipt_pts is not None):
        return {"points": receipt_pts[0]}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No receipt found for that ID.")



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)