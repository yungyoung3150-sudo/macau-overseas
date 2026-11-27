import json, glob, sys, shutil, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else HERE
OUT = os.path.expanduser("~/Downloads/macau-cs-handoff.html")
SCRATCH = os.environ.get("ORCA_CHAT_SCRATCH_DIR")
CATS = ["진행 중 공구", "결항", "항공", "예약·확정", "여권·서류", "요금·결제", "취소·환불",
        "호텔", "투어·특전", "이동·교통", "응대 원칙", "어디서 확인", "담당·연락"]
TRIES = ["결항", "여권", "유아 요금", "버스투어", "취소", "항공권번호", "홍영기", "엑스트라베드"]

entries = []
for f in sorted(glob.glob(os.path.join(SRC, "*.json"))):
    if os.path.basename(f).startswith("_"):
        continue
    for e in json.load(open(f)):
        assert e.get("title") and e.get("a") and e.get("cat"), (f, e)
        if e["cat"] not in CATS:
            print("unknown cat", e["cat"], "→ 어디서 확인", e["title"])
            e["cat"] = "어디서 확인"
        entries.append(e)

seen = {}
for e in entries:
    key = e["title"].replace(" ", "")
    if key in seen:
        print("dup title:", e["title"], "|", seen[key].get("src"), "|", e.get("src"))
    seen[key] = e

entries.sort(key=lambda e: CATS.index(e["cat"]))
for i, e in enumerate(entries):
    e["id"] = f"e{i}"

built = datetime.date.today().strftime("%Y-%m-%d")
data = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")
html = (open(os.path.join(HERE, "template.html")).read()
        .replace("__DATA__", data)
        .replace("__TRIES__", json.dumps(TRIES, ensure_ascii=False))
        .replace("__BUILT__", built)
        .replace("__DOC__", "https://claude.ai/artifact/X5wkUURNQ8h14wiBeByjxq"))
open(OUT, "w").write(html)
if SCRATCH:
    shutil.copy(OUT, os.path.join(SCRATCH, f"macau-cs-handoff-{built}.html"))
print(len(entries), "entries", len(html.encode()) // 1024, "KB →", OUT)
