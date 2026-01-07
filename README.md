# RippleAid (XRPL Testnet MVP)

RippleAid is a simple humanitarian aid MVP built on the **XRP Ledger (XRPL)**.
It demonstrates a complete flow where a verified beneficiary receives **tokenized aid vouchers**, spends them at a merchant, the merchant redeems vouchers back to the NGO, and the NGO settles the merchant in **XRP**.

> Hackathon demo only. No personal data is stored on-chain.

---

## MVP Flow (what this project does)

Actors:
- **NGO** (voucher issuer + settlement payer)
- **Beneficiary**
- **Merchant**

Flow:
1) Beneficiary creates an **XRPL DID**
2) Beneficiary + Merchant create **trustlines** to accept the voucher token
3) NGO issues voucher tokens to Beneficiary
4) Beneficiary pays Merchant with vouchers
5) Merchant redeems vouchers back to NGO
6) NGO pays Merchant in **XRP** (settlement)

---

## XRPL Features Used (required for judging)

- **DIDSet**: creates an on-ledger DID entry for the beneficiary (identity anchor)
- **TrustSet / Trustlines**: beneficiary & merchant opt-in to hold the voucher token
- **Issued Currency Tokens (IOUs)**: vouchers are issued and transferred on XRPL
- **Payment transactions**: voucher issuance, voucher spending, voucher redemption, XRP settlement
- **AccountSet (Default Ripple on issuer)**: enables voucher transfers from beneficiary → merchant

---

## How to run (Python)

1) Install dependencies:
```bash
pip install -r requirements.txt
