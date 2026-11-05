import json, requests, csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
API="http://127.0.0.1:8000"
users=json.loads((ROOT/"data"/"users.json").read_text(encoding="utf-8"))
cases=json.loads((ROOT/"data"/"evaluation.json").read_text(encoding="utf-8"))
tokens={}
with open("evaluation_credentials.json", "r", encoding="utf-8") as file:
    demo_passwords = json.load(file)

tokens = {}

for u in users:
    username = u["username"]

    if username not in demo_passwords:
        continue

    r = requests.post(
        API + "/login",
        json={
            "username": username,
            "password": demo_passwords[username]
        }
    )

    r.raise_for_status()
    tokens[username] = r.json()["access_token"]
user_by_name={u["username"]:u for u in users}
rows=[]
for case in cases:
    user=case["user"]
    token=tokens[user]
    response=requests.post(API+"/ask",headers={"Authorization":f"Bearer {token}"},
                           json={"question":case["question"],"top_k":5})
    response.raise_for_status()
    data=response.json()
    retrieved={s["doc_id"] for s in data["sources"]}
    expected=set(case["expected_doc_ids"])
    # A security pass means no returned doc is outside this user's allowed corpus.
    docs=json.loads((ROOT/"data"/"documents.json").read_text(encoding="utf-8"))
    u=user_by_name[user]
    allowed={d["doc_id"] for d in docs if d["tenant_id"]==u["tenant_id"] and
             (set(d["allowed_roles"]) & set(u["roles"]) or u["user_id"] in d["allowed_users"])}
    unauthorized=retrieved-allowed
    forbidden=set(case.get("forbidden_doc_ids", []))
    forbidden_returned=retrieved & forbidden
    hit=1 if expected & retrieved else (1 if not expected and not forbidden_returned else 0)
    rows.append({"user":user,"question":case["question"],"expected_docs":";".join(expected),
                 "retrieved_docs":";".join(retrieved),"retrieval_hit_or_correct_denial":hit,
                 "unauthorized_docs":";".join(unauthorized),
                 "forbidden_target_docs_returned":";".join(forbidden_returned),
                 "security_pass":int(not unauthorized and not forbidden_returned)})
with (ROOT/"evaluation_results.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f"Cases: {len(rows)}")
print(f"Retrieval hit/correct-denial rate: {sum(r['retrieval_hit_or_correct_denial'] for r in rows)/len(rows):.1%}")
print(f"Unauthorized retrievals: {sum(bool(r['unauthorized_docs']) for r in rows)}")
print("Saved evaluation_results.csv")
