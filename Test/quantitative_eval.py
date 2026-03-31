import json, requests, time

URL = "https://ayyyhaga-prof2-ayhaga.hf.space/text-to-text"
INP = "eval_questions.jsonl"
OUT = "eval_outputs.jsonl"

def main():
    with open(INP, "r", encoding="utf-8") as f:
        qs = [json.loads(line) for line in f]

    out = []
    for q in qs:
        t0 = time.time()
        r = requests.post(URL, json={"question": q["question"]}, timeout=180)
        r.raise_for_status()
        data = r.json()
        latency = time.time() - t0

        out.append({
            "id": q["id"],
            "question": q["question"],
            "is_answerable": q["is_answerable"],
            "answer": data.get("answer",""),
            "retrieved_ids": data.get("retrieved_ids",[]),
            "latency_sec": round(latency, 3),
        })
        print(q["id"], "ok")

    with open(OUT, "w", encoding="utf-8") as f:
        for row in out:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("Saved:", OUT)

if __name__ == "__main__":
    main()
