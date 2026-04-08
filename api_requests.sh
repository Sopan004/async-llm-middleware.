#!/bin/bash
# Example API requests for AI Data Translation Layer
BASE_URL="http://localhost:8000/api/v1"

echo "=== Health Check ==="
curl -s $BASE_URL/health | python3 -m json.tool

echo ""
echo "=== Translate Invoice Text ==="
curl -s -X POST $BASE_URL/translate \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Invoice #4521. Date: Jan 5 2025. Client: Acme Corp, 123 Main St NY. Items: Web Dev $2500, SEO Audit $750, Hosting $300. Total: $3550. Due in 30 days. billing@acme.com",
    "chunk_for_rag": true,
    "chunk_size": 300
  }' | python3 -m json.tool

echo ""
echo "=== Translate with Custom Schema ==="
curl -s -X POST $BASE_URL/translate \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Patient: John Doe, DOB March 12 1985. Visit: 2nd Feb 2025. BP 120/80. Prescribed Metformin 500mg twice daily.",
    "output_schema": "{patient_name, date_of_birth, visit_date, vitals: {blood_pressure}, prescriptions: [{drug, dosage, frequency}]}",
    "chunk_for_rag": false
  }' | python3 -m json.tool

echo ""
echo "=== Upload File ==="
curl -s -X POST $BASE_URL/translate/file \
  -F "file=@examples/sample_invoice.txt" | python3 -m json.tool

echo ""
echo "=== Batch Translate ==="
curl -s -X POST $BASE_URL/translate/batch \
  -H "Content-Type: application/json" \
  -d '[
    "Order #001 - Customer: Jane Smith - Product: Laptop X1 - Qty: 2 - Price: $1200 each - Shipped: 10 Jan 2025",
    "Order #002 - Customer: Bob Jones - Product: Monitor 27in - Qty: 1 - Price: $450 - Pending shipment"
  ]' | python3 -m json.tool
