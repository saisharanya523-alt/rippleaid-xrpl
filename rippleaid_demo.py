import json
from datetime import datetime, timezone
from typing import Any

import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet

try:
    from xrpl.transaction import submit_and_wait
except Exception:
    from xrpl.transaction.reliable_submission import submit_and_wait  # type: ignore

try:
    from xrpl.models.requests import AccountObjects
except Exception:
    from xrpl.models import AccountObjects  # type: ignore


TESTNET_URL = "https://s.altnet.rippletest.net:51234"
EXPLORER_TX = "https://testnet.xrpl.org/transactions/{}"
VOUCHER_CURRENCY = "RAID"


def now_iso_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def str_to_hex(s: str) -> str:
    return s.encode("utf-8").hex().upper()


def addr(wallet: Any) -> str:
    return getattr(wallet, "classic_address", None) or getattr(wallet, "address")


def tx_link(tx_hash: str) -> str:
    return EXPLORER_TX.format(tx_hash)


def submit(tx, client, wallet, label: str):
    resp = submit_and_wait(tx, client, wallet)
    result = resp.result
    tx_hash = result.get("hash") or (result.get("tx_json") or {}).get("hash")
    engine = result.get("engine_result")

    print(f"\n{label}")
    print(f"engine_result: {engine}")
    if tx_hash:
        print(f"tx_hash: {tx_hash}")
        print(f"explorer: {tx_link(tx_hash)}")
    else:
        print(json.dumps(result, indent=2))

    return result


def main():
    client = JsonRpcClient(TESTNET_URL)

    ngo = generate_faucet_wallet(client, debug=True)
    beneficiary = generate_faucet_wallet(client, debug=True)
    merchant = generate_faucet_wallet(client, debug=True)

    print("NGO:", addr(ngo))
    print("Beneficiary:", addr(beneficiary))
    print("Merchant:", addr(merchant))

    acctset = xrpl.models.transactions.AccountSet(
        account=addr(ngo),
        set_flag=xrpl.models.transactions.AccountSetAsfFlag.ASF_DEFAULT_RIPPLE,
    )
    submit(acctset, client, ngo, "1) NGO enables Default Ripple")

    did_doc = {"id": f"did:rippleaid:{addr(beneficiary)}", "controller": addr(beneficiary)}
    did_data = {"verified_by": "MockNGO", "timestamp": now_iso_z()}

    did_tx = xrpl.models.transactions.DIDSet(
        account=addr(beneficiary),
        uri=str_to_hex(f"did:rippleaid:{addr(beneficiary)}"),
        did_document=str_to_hex(json.dumps(did_doc, separators=(",", ":"))),
        data=str_to_hex(json.dumps(did_data, separators=(",", ":"))),
    )
    submit(did_tx, client, beneficiary, "2) Beneficiary creates DID")

    for w, who in [(beneficiary, "Beneficiary"), (merchant, "Merchant")]:
        trust_tx = xrpl.models.transactions.TrustSet(
            account=addr(w),
            limit_amount=xrpl.models.amounts.IssuedCurrencyAmount(
                currency=VOUCHER_CURRENCY,
                issuer=addr(ngo),
                value="1000000",
            ),
        )
        submit(trust_tx, client, w, f"3) {who} sets trustline for {VOUCHER_CURRENCY}")

    issue_tx = xrpl.models.transactions.Payment(
        account=addr(ngo),
        destination=addr(beneficiary),
        amount=xrpl.models.amounts.IssuedCurrencyAmount(
            currency=VOUCHER_CURRENCY,
            issuer=addr(ngo),
            value="50",
        ),
    )
    submit(issue_tx, client, ngo, f"4) NGO issues 50 {VOUCHER_CURRENCY} to Beneficiary")

    pay_merchant_tx = xrpl.models.transactions.Payment(
        account=addr(beneficiary),
        destination=addr(merchant),
        amount=xrpl.models.amounts.IssuedCurrencyAmount(
            currency=VOUCHER_CURRENCY,
            issuer=addr(ngo),
            value="10",
        ),
    )
    submit(pay_merchant_tx, client, beneficiary, f"5) Beneficiary pays 10 {VOUCHER_CURRENCY} to Merchant")

    redeem_tx = xrpl.models.transactions.Payment(
        account=addr(merchant),
        destination=addr(ngo),
        amount=xrpl.models.amounts.IssuedCurrencyAmount(
            currency=VOUCHER_CURRENCY,
            issuer=addr(ngo),
            value="10",
        ),
    )
    submit(redeem_tx, client, merchant, f"6) Merchant redeems 10 {VOUCHER_CURRENCY} to NGO")

    settle_tx = xrpl.models.transactions.Payment(
        account=addr(ngo),
        destination=addr(merchant),
        amount=xrpl.utils.xrp_to_drops(1),
    )
    submit(settle_tx, client, ngo, "7) NGO settles Merchant with 1 XRP")

    objs = client.request(AccountObjects(account=addr(beneficiary))).result.get("account_objects", [])
    did_objs = [o for o in objs if o.get("LedgerEntryType") == "DID"]
    print("DID exists:", bool(did_objs))


if __name__ == "__main__":
    main()
