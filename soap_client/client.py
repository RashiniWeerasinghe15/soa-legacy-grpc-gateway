from zeep import Client
from zeep.exceptions import Fault

WSDL_URL = "http://localhost:8000/?wsdl"
client = Client(WSDL_URL)

print("=== TEST 1: GetAccountStatus (Valid) ===")
acc = client.service.GetAccountStatus(account_number="ACC-1001")
print(f"Holder: {acc.account_holder} | Status: {acc.status} | Limit: ${acc.daily_limit}")

print("\n=== TEST 2: EvaluateTransactionRisk (Approved) ===")
risk = client.service.EvaluateTransactionRisk(account_number="ACC-1001", amount=250.0, destination_country="UK")
print(f"Approved: {risk.is_approved} | Score: {risk.risk_score} | Reason: {risk.reason}")

print("\n=== TEST 3: EvaluateTransactionRisk (Flagged High Risk) ===")
risk_bad = client.service.EvaluateTransactionRisk(account_number="ACC-1001", amount=50000.0, destination_country="SANCTIONED")
print(f"Approved: {risk_bad.is_approved} | Score: {risk_bad.risk_score} | Reason: {risk_bad.reason}")

print("\n=== TEST 4: FreezeAccount ===")
frozen = client.service.FreezeAccount(account_number="ACC-1001", reason="Suspected fraudulent transfer")
print(f"Account: {frozen.account_number} | Frozen: {frozen.is_frozen} | Timestamp: {frozen.timestamp}")

print("\n=== TEST 5: Fault Mapping (Empty Input -> InvalidArgument) ===")
try:
    client.service.GetAccountStatus(account_number="")
except Fault as f:
    print(f"SOAP Fault caught: [{f.code}] {f.message}")

print("\n=== TEST 6: Fault Mapping (Nonexistent Account -> NotFound) ===")
try:
    client.service.GetAccountStatus(account_number="ACC-9999")
except Fault as f:
    print(f"SOAP Fault caught: [{f.code}] {f.message}")