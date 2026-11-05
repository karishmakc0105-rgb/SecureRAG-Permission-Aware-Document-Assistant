import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
docs=json.loads((ROOT/"data"/"documents.json").read_text(encoding="utf-8"))
users=json.loads((ROOT/"data"/"users.json").read_text(encoding="utf-8"))
by_name={u["username"]:u for u in users}

def allowed(doc,user):
    return (doc["tenant_id"]==user["tenant_id"] and
            (bool(set(doc["allowed_roles"]) & set(user["roles"]) or
                  user["user_id"] in doc["allowed_users"])))

def test_every_document_has_tenant_and_acl():
    for doc in docs:
        assert doc.get("tenant_id")
        assert isinstance(doc.get("allowed_roles"),list)
        assert isinstance(doc.get("allowed_users"),list)

def test_employee_cannot_read_acme_salary_register():
    assert not allowed(next(d for d in docs if d["doc_id"]=="acme_conf_salary"),
                       by_name["acme_employee"])

def test_hr_can_read_acme_salary_register():
    assert allowed(next(d for d in docs if d["doc_id"]=="acme_conf_salary"),
                   by_name["acme_hr"])

def test_tenant_isolation():
    assert not allowed(next(d for d in docs if d["doc_id"]=="acme_public_leave"),
                       by_name["blue_employee"])

def test_user_specific_offer_is_private():
    offer=next(d for d in docs if d["doc_id"]=="acme_user_offer")
    assert allowed(offer,by_name["acme_employee"])
    assert allowed(offer,by_name["acme_hr"])  # HR role is allowed
    assert not allowed(offer,by_name["blue_employee"])
