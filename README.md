# RippleAid (XRPL Testnet MVP)

RippleAid is a humanitarian aid MVP built on the **XRP Ledger (XRPL)**. It demonstrates an end-to-end flow where a beneficiary receives **tokenized aid vouchers**, spends them at a merchant, the merchant redeems vouchers back to the NGO, and the NGO settles the merchant in **XRP**.

No personal data is stored on-chain.

---

## MVP Flow

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

## XRPL Features Used

- **DIDSet**: beneficiary DID creation
- **TrustSet / Trustlines**: opt-in to hold voucher tokens
- **Issued Currency Tokens (IOUs)**: voucher token issuance and transfers
- **Payment transactions**: voucher issuance, spending, redemption, XRP settlement
- **AccountSet (Default Ripple on issuer)**: allows voucher transfers beneficiary → merchant

---

## How to run (Python)

Install:
```bash
pip install -r requirements.txt
