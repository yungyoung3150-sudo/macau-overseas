#!/usr/bin/env python3
"""에어마카오(ICN-MFM, NX) 구글 직항가 수동 수집 보조 + 가드레일 — 검수용 코드.

배경: 네이버 수집기가 '항공_최저가'에 간헐적으로 '미운항'(가격 못 가져옴)을 채워 신뢰 불가.
그래서 에어부산처럼 에어마카오도 구글 항공(ICN→MFM, 에어마카오 NX 직항)으로 시장최저를 옮긴다.

  plan : 박수 규칙으로 (출발→귀국) 일정 산출 + 구글 검색 URL 생성.
  eval : 수집값(airmacau_manual.csv)을 읽어 시장최저(2인)=직항1인×2 → 기존 가드레일 판정.

박수 규칙(출처: 옵시디언 '마카오 패키지 핵심 정보'):
  2박3일: NX825 ICN 07:50→MFM 10:45 / NX826 MFM 18:00→ICN 22:45.  귀국 = 출발 + 2
  3박4일: NX821 ICN 14:15→MFM 17:15 / NX822 MFM 08:25→ICN 13:05.  귀국 = 출발 + 3
  ※ 에어마카오 NX는 매일 운항(판매일=공구 우리요금 입력된 날짜).
"""

from __future__ import annotations

import argparse
import base64
import csv
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO / "src"))

from macau_fare_monitor.alert import AlertLevel, classify  # noqa: E402

MANUAL = ROOT / "airmacau_manual.csv"
WD_KR = ["월", "화", "수", "목", "금", "토", "일"]

# 검증된 왕복 tfs 템플릿(PUS-MFM 7/24→7/27)에서 공항코드 PUS→ICN 치환 → 인천-마카오.
_TFS = ("CBwQAhoeEgoyMDI2LTA3LTI0agcIARIDUFVTcgcIARIDTUZNGh4SCjIwMjYt"
        "MDctMjdqBwgBEgNNRk1yBwgBEgNQVVNAAUgBcAGCAQsI____________AZgBAQ")
_RAW = base64.urlsafe_b64decode(_TFS + "=" * (-len(_TFS) % 4)).replace(b"PUS", b"ICN")


def google_url(dep: date, ret: date) -> str:
    """ICN-MFM 왕복 구글 항공 URL. 출발=07-24슬롯, 귀국=07-27슬롯 자리를 *플레이스홀더 경유*로
    치환해, dep/ret이 템플릿 날짜(07-24/07-27)와 겹쳐도 충돌하지 않게 한다."""
    b = _RAW.replace(b"2026-07-24", b"@@DEP@@").replace(b"2026-07-27", b"@@RET@@")
    b = b.replace(b"@@DEP@@", dep.isoformat().encode()).replace(b"@@RET@@", ret.isoformat().encode())
    return "https://www.google.com/travel/flights/search?tfs=" + base64.urlsafe_b64encode(b).decode().rstrip("=")


def ret_for(dep: date, stay: str) -> date:
    return dep + timedelta(days=2 if stay == "2박3일" else 3)


def cmd_plan(stay: str, dates):
    print(f"=== 에어마카오 {stay} 구글 검색(ICN→MFM, NX 직항) ===\n")
    for ds in dates:
        dep = datetime.strptime(ds, "%Y-%m-%d").date()
        ret = ret_for(dep, stay)
        print(f"{ds}({WD_KR[dep.weekday()]}) →{ret.isoformat()}({WD_KR[ret.weekday()]})")
        print(f"  {google_url(dep, ret)}")


def cmd_eval(path: Path):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if not (r.get("nx_direct_pp") or "").strip():
                continue
            dep = datetime.strptime(r["depart_date"], "%Y-%m-%d").date()
            our_2p = int(r["our_2p"]) if r.get("our_2p") else None
            nx_pp = int(r["nx_direct_pp"])
            market_2p = nx_pp * 2
            a = classify(our_2p, market_2p)
            rows.append((dep, r.get("stay", ""), our_2p, nx_pp, market_2p, a))
    order = {AlertLevel.ALARM: 0, AlertLevel.WATCH: 1, AlertLevel.SAFE: 2}
    rows.sort(key=lambda t: (order.get(t[5].level, 9), -(t[5].surcharge_pp or 0)))
    n = {lv: sum(1 for t in rows if t[5].level is lv) for lv in (AlertLevel.ALARM, AlertLevel.WATCH, AlertLevel.SAFE)}
    print(f"=== 에어마카오 가드레일: {len(rows)}건 · "
          f"🔴{n[AlertLevel.ALARM]} 🟠{n[AlertLevel.WATCH]} 🟢{n[AlertLevel.SAFE]} ===\n")
    for dep, stay, our, nx, mkt, a in rows:
        ov = f"{our:,}" if our else "-"
        print(f"{a.label:<22} {dep}({WD_KR[dep.weekday()]}) {stay}  "
              f"우리 {ov} vs 시장 {mkt:,}(직항 {nx:,}×2)  →시트입력값 {mkt}")


def main() -> int:
    p = argparse.ArgumentParser(description="에어마카오 구글 NX 수동수집 보조+가드레일")
    sub = p.add_subparsers(dest="cmd")
    pp = sub.add_parser("plan")
    pp.add_argument("stay", choices=["2박3일", "3박4일"])
    pp.add_argument("dates", nargs="+", help="출발일 YYYY-MM-DD ...")
    pe = sub.add_parser("eval")
    pe.add_argument("--csv", type=Path, default=MANUAL)
    args = p.parse_args()
    if args.cmd == "plan":
        cmd_plan(args.stay, args.dates)
    else:
        cmd_eval(getattr(args, "csv", MANUAL))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
