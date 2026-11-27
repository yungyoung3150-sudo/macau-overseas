import json, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
CATS = ["진행 중 공구", "결항", "항공", "예약·확정", "여권·서류", "요금·결제", "취소·환불",
        "호텔", "투어·특전", "이동·교통", "응대 원칙", "어디서 확인", "담당·연락"]
E = [e for f in sorted(glob.glob(os.path.join(HERE, "*.json"))) for e in json.load(open(f))]
def md(e):
    out = [f"### {e['title']}", e["a"].replace("\n", "  \n")]
    if e.get("changed"): out.append(f"**바뀐 점.** {e['changed']}")
    if e.get("warn"): out.append(f"**주의.** {e['warn']}")
    if e.get("say"): out.append("**고객 답변 예시.**\n\n> " + e["say"].replace("\n", "\n> "))
    out.append(f"검색어 {', '.join(e.get('q') or [])} · 근거 {e.get('src','')}")
    return "\n\n".join(out)
for i, c in enumerate(CATS):
    rows = [e for e in E if e["cat"] == c]
    rows.sort(key=lambda e: not e.get("pin"))
    chunks, cur = [], ""
    for e in rows:
        m = md(e) + "\n\n"
        if cur and len((cur + m).encode()) > 14000:
            chunks.append(cur); cur = ""
        cur += m
    chunks.append(cur)
    for j, ch in enumerate(chunks):
        open(os.path.join(HERE, "doc-md", f"{i:02d}-{j}.md"), "w").write(ch.strip() + "\n")
    print(i, c, len(rows), "entries", len(chunks), "chunks", sum(len(x.encode()) for x in chunks)//1024, "KB")
