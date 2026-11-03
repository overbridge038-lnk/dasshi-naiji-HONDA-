"""出力ExcelをCSVと1セルずつ突き合わせる検証スクリプト。

使い方:  python tests/verify.py [出力xlsx] [内示csv]
省略時は output/ の最新xlsx と sample/ のCSV を使う。

見出し行（「背番」がある行）の文字から列を探すので、列の位置が変わっても動く。
- 日別：「11/1」のように / を含む見出し
- 合計：「合計」を含む見出し（当月・翌月・翌々月）
- 区分：あれば 数量の行の下に 箱数の行がある
- 入り数：あれば 箱数＝数量÷入り数（繰り上げ）、当月の箱数＝日ごとの箱数の合計 を確認
"""
import csv
import glob
import math
import os
import sys
import unicodedata

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(s):
    return unicodedata.normalize("NFKC", str(s or "")).replace(" ", "").upper()


def num(s):
    s = str(s or "").replace(",", "").strip()
    try:
        return float(s) if s else None
    except ValueError:  # 「abc」など数字でないもの
        return None


def main():
    xlsx = sys.argv[1] if len(sys.argv) > 1 else max(glob.glob(os.path.join(ROOT, "output", "*.xlsx")), key=os.path.getmtime)
    csv_path = sys.argv[2] if len(sys.argv) > 2 else glob.glob(os.path.join(ROOT, "sample", "*.csv"))[0]

    with open(csv_path, encoding="cp932") as f:
        rows = list(csv.reader(f))
    h = [x.strip() for x in rows[0]]
    key = h.index("整理番号")
    day_cols = {int(x): i for i, x in enumerate(h) if x.isdigit() and 1 <= int(x) <= 31}
    tot_cols = [i for i, x in enumerate(h) if x.startswith("内示数量(")][:3]
    data = {}
    for r in rows[1:]:
        if r and r[key].strip():
            data.setdefault(norm(r[key]), []).append(r)

    ws = openpyxl.load_workbook(xlsx).active
    hdr = next(c for row in ws.iter_rows() for c in row if norm(c.value) == norm("背番"))
    hr, c0 = hdr.row, hdr.column
    head = {c: str(ws.cell(hr, c).value or "") for c in range(1, ws.max_column + 1)}
    day_c = [c for c, v in head.items() if "/" in v]
    tot_c = [c for c, v in head.items() if "合計" in v]
    st_col = next(c for c, v in head.items() if v == "照合結果")
    kubun_c = next((c for c, v in head.items() if v == "区分"), None)
    irisu_c = next((c for c, v in head.items() if norm(v) in (norm("入り数"), norm("入数"))), None)
    assert len(tot_c) == 3, f"合計の列が3つありません: {tot_c}"

    ok = warn = ng = err = 0
    r = hr + 1
    while r <= ws.max_row:
        sb = ws.cell(r, c0).value
        if sb is None:
            r += 1
            continue
        box_r = r + 1 if kubun_c else None
        status = str(ws.cell(r, st_col).value or "")
        hits = data.get(norm(sb), [])
        got = [ws.cell(r, c).value for c in day_c + tot_c]
        got_f = [None if v is None else float(v) for v in got]

        if not hits:
            warn += 1
            if any(v is not None for v in got) or status != "CSVに該当なし":
                err += 1
                print(f"NG 行{r} {sb}: CSVに無いのに値または判定がおかしい")
        else:
            def total(i):
                vals = [num(x[i]) for x in hits]
                return None if all(v is None for v in vals) else sum(v or 0 for v in vals)

            exp_day = [total(day_cols[d]) if d in day_cols else None for d in range(1, len(day_c) + 1)]
            exp_tot = [total(i) for i in tot_cols]
            if exp_day + exp_tot != got_f:
                err += 1
                print(f"NG 行{r} {sb}: 数量\n  期待 {exp_day + exp_tot}\n  実際 {got_f}")

            # 箱数の確認
            if box_r:
                if ws.cell(r, kubun_c).value != "数量" or ws.cell(box_r, kubun_c).value != "箱数":
                    err += 1
                    print(f"NG 行{r} {sb}: 区分（数量／箱数）の並びがおかしい")
                irisu = num(ws.cell(r, irisu_c).value) if irisu_c else None
                got_box = [ws.cell(box_r, c).value for c in day_c + tot_c]
                got_box = [None if v is None else float(v) for v in got_box]
                if irisu and irisu > 0:
                    ceil = lambda v: None if v is None else float(math.ceil(v / irisu))
                    b_day = [ceil(v) for v in exp_day]
                    m0 = sum(v or 0 for v in b_day) if any(v is not None for v in exp_day) else ceil(exp_tot[0])
                    exp_box = b_day + [m0, ceil(exp_tot[1]), ceil(exp_tot[2])]
                    if exp_box != got_box:
                        err += 1
                        print(f"NG 行{box_r} {sb}: 箱数（入り数{irisu:g}）\n  期待 {exp_box}\n  実際 {got_box}")
                else:
                    if any(v is not None for v in got_box) or "入り数なし" not in status:
                        err += 1
                        print(f"NG 行{r} {sb}: 入り数が無いのに箱数がある、または「入り数なし」の表示が無い")

            if status == "一致":
                ok += 1
            elif status.startswith("日別"):
                ng += 1
            else:
                warn += 1
        r = (box_r or r) + 1

    print(f"一致 {ok} / 注意 {warn} / 異常 {ng} / 照合エラー {err}  ({os.path.basename(xlsx)})")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
