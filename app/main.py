
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
        payload_json = json.dumps(payload)
        receipt_id = generate_id(payload_json)
        receipt_points = calculate_points(payload_json)
        check = store_receipt(str(receipt_id), receipt_points, payload)
        if (check):
            return {"id": receipt_id}
        else:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    except HTTPException as http_error:
        logging.error(f"HTTP error occurred: {http_error.detail}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error processing receipt.")
    except (json.JSONDecodeError, ValueError) as e:
        # Handle specific errors related to payload
        logging.error(f"JSON or ValueError occurred: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The receipt is invalid.")
    except Exception as e:
        # Catch any unexpected errors
        print(e)
        logging.error(f"An unexpected error occurred: {e}")
        logging.exception(e)  # Logs stack trace as well
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


@app.get("/receipts/{receipt_id}/points")
def get_points(receipt_id: str):
    receipt_pts = get_receipt_points(receipt_id)
    if (receipt_pts is not None):
        return {"points": receipt_pts[0]}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No receipt found for that ID.")



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)