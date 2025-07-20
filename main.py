from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_invoice(file: UploadFile = File(...)):
    contents = await file.read()
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        total_sum = 0
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                # Find the header row (assuming it's always the first row matching 'Product')
                for row in table:
                    if row and 'Product' in row:
                        header = row
                        break
                # Find column indices
                product_idx = header.index("Product")
                total_idx = header.index("Total")
                # Iterate over data rows after header
                for row in table:
                    if not row or row == header:
                        continue
                    if row[product_idx] and row[product_idx].strip() == "Gadget":
                        val = row[total_idx]
                        if val and val.isdigit():
                            total_sum += int(val)
    return {"sum": total_sum}
