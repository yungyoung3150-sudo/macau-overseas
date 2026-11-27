#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포터블 .xlsx 사본 — 폴라리스/구글시트/모든 엑셀에서 열림(매크로 없음).

핵심: 머리글의 '필터 ▼ 버튼'(엑셀/폴라리스 기본 기능)을 살려서,
     Arrival ▼ → "오름차순 정렬" 한 번으로 정렬. 매크로 불필요.

구조:
  1행 = 주황 머리글 + ▼버튼 (열 이름; 표 머리글)  → 고정, 정렬해도 안 움직임
  2행 = 빨강 예시행 (HONG GILDONG 샘플)            → 머리글 바로 아래, 가장 옛 날짜라 정렬해도 맨 위 유지
  3행~ = 실제 예약                                 → Arrival ▼ 정렬 시 이 부분이 정렬됨
원본 영문 머리글행(▼)과 주황 라벨행을 '주황+▼ 머리글 한 줄'로 합침(정보 손실 없음).
"Rate code" 오른쪽에 "Yestravel Reservation Code"(P열) 추가. 원본은 수정하지 않음.
"""
import zipfile, os, re

SRC = "~/Downloads/(3rd batch) Yes Travel KOL promotion reservation list.xlsx"
OUT = "~/Downloads/(3rd batch) Yes Travel KOL promotion reservation list - 사본.xlsx"
HEADER = "Yestravel Reservation Code"   # 새 idx 33

def edit_shared_strings(xml):
    xml = xml.replace("</sst>", f"<si><t>{HEADER}</t></si></sst>")
    return xml.replace('uniqueCount="33"', 'uniqueCount="34"')

def edit_sheet1(xml):
    row1 = re.search(r'<row r="1".*?</row>', xml, re.S).group(0)
    row2 = re.search(r'<row r="2".*?</row>', xml, re.S).group(0)
    row3 = re.search(r'<row r="3".*?</row>', xml, re.S).group(0)

    # 1행 = 주황 머리글(모든 셀 s="9") + P1, ▼버튼은 표(autoFilter)가 제공
    new1 = re.sub(r'<c r="([A-P]1)"(?: s="\d+")? t="s">', r'<c r="\1" s="9" t="s">', row1)
    new1 = new1.replace('</row>', '<c r="P1" s="9" t="s"><v>33</v></c></row>')

    # 3행(예시) → 2행으로 이동 + P2(빨강 빈칸)
    new2 = row3.replace('<row r="3"', '<row r="2"')
    new2 = re.sub(r'r="([A-P])3"', r'r="\g<1>2"', new2)
    new2 = new2.replace('</row>', '<c r="P2" s="68"/></row>')

    # 원본 1·2·3행 → 새 1·2행 (주황 라벨행=원본 2행 삭제, 색은 머리글로 흡수)
    xml = xml.replace(row1, "%%N1%%").replace(row2, "").replace(row3, new2).replace("%%N1%%", new1)

    # 머리글(1행)+예시(2행) 고정
    xml = xml.replace('ySplit="3" topLeftCell="A4"', 'ySplit="2" topLeftCell="A3"')
    return xml

def edit_table(xml):
    # 표 유지 → ▼버튼 유지. 범위 머리글(1행)+예시(2행)로, 새 열 추가.
    xml = xml.replace('ref="A1:O3"', 'ref="A1:P2"')          # 표 ref + autoFilter ref
    xml = re.sub(r'<sortState.*?</sortState>', '', xml, flags=re.S)
    xml = xml.replace('<tableColumns count="15">', '<tableColumns count="16">')
    anchor = 'name="Rate code "/>'
    xml = xml.replace(anchor, anchor + f'<tableColumn id="22" name="{HEADER}"/>')
    return xml

def main():
    with zipfile.ZipFile(SRC) as z:
        infos = z.infolist()
        parts = {i.filename: z.read(i.filename) for i in infos}

    parts["xl/sharedStrings.xml"] = edit_shared_strings(parts["xl/sharedStrings.xml"].decode()).encode()
    parts["xl/worksheets/sheet1.xml"] = edit_sheet1(parts["xl/worksheets/sheet1.xml"].decode()).encode()
    parts["xl/tables/table1.xml"] = edit_table(parts["xl/tables/table1.xml"].decode()).encode()

    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for i in infos:
            zout.writestr(i, parts[i.filename])
    print("WROTE:", OUT, os.path.getsize(OUT), "bytes")

if __name__ == "__main__":
    main()
