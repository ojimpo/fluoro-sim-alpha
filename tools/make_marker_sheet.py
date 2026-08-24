#!/usr/bin/env python3
"""L判シール紙にちょうど収まる ArUco マーカーシートを生成する。

透視シミュレーターの模型アライメント用。コンビニ（セブン-イレブンのシール紙
プリント等）で刷って切り、血管模型の隅に貼ることを想定している。

辞書は DICT_4X4_50。4x4 ビット＋外周1モジュールの黒枠＝6モジュール角なので、
同じ物理サイズなら 5x5/6x6 より 1 モジュールあたりの画素数を稼げる。ID は
4隅ぶん×模型数しか要らないので 50 個で十分すぎる。

余白（quiet zone）は検出に必須。黒枠の外側に最低1モジュールぶんの白が要る。
切り取り線は quiet zone の外に引いてあるので、線の上で切れば余白が残る。

  python3 tools/make_marker_sheet.py            # 貼る用の L判シール紙シート
  python3 tools/make_marker_sheet.py --mm 12    # 12mm 版
  python3 tools/make_marker_sheet.py --target   # 試す用の A4 テストターゲット
"""
import argparse

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DPI = 600
# L判 89x127mm。127mm はちょうど 5inch なので高さは端数が出ない
PAGE_W_MM, PAGE_H_MM = 89.0, 127.0
A4_W_MM, A4_H_MM = 210.0, 297.0
COLS, ROWS = 4, 4
QUIET_MM = 3.0      # 黒枠の外側の白。4x4 なら 1 モジュール = 約1.7mm なので余裕を見て 3mm
LABEL_MM = 4.0      # 切り取り線の外に出す ID 文字の帯
GUTTER_MM = 2.0


def mm(v: float) -> int:
    return round(v / 25.4 * DPI)


def build(marker_mm: float) -> tuple[Image.Image, float]:
    # モジュールが整数画素に乗らないと市松が不均一になって検出が鈍る。
    # 指定 mm に一番近い整数モジュールへ丸め、実寸は呼び出し元へ返す。
    module_px = max(1, round(mm(marker_mm) / 6))
    marker_px = module_px * 6
    actual_mm = marker_px / DPI * 25.4

    quiet_px, label_px, gutter_px = mm(QUIET_MM), mm(LABEL_MM), mm(GUTTER_MM)
    cell_px = marker_px + quiet_px * 2

    page = Image.new("L", (mm(PAGE_W_MM), mm(PAGE_H_MM)), 255)
    draw = ImageDraw.Draw(page)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", size=mm(2.2))
    except OSError:
        font = ImageFont.load_default()

    grid_w = COLS * cell_px + (COLS - 1) * gutter_px
    grid_h = ROWS * (cell_px + label_px) + (ROWS - 1) * gutter_px
    ox, oy = (page.width - grid_w) // 2, (page.height - grid_h) // 2

    aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    for row in range(ROWS):
        for col in range(COLS):
            marker_id = row * COLS + col
            x = ox + col * (cell_px + gutter_px)
            y = oy + row * (cell_px + label_px + gutter_px)

            img = cv2.aruco.generateImageMarker(aruco, marker_id, marker_px, borderBits=1)
            page.paste(Image.fromarray(np.asarray(img)), (x + quiet_px, y + quiet_px))

            # 切り取り線。quiet zone の外周なので線の上で切れば余白が残る
            draw.rectangle([x, y, x + cell_px, y + cell_px], outline=190, width=max(1, mm(0.15)))
            draw.text((x + cell_px // 2, y + cell_px + label_px // 2),
                      f"ID {marker_id}", fill=120, font=font, anchor="mm")

    margin_mm = ox / DPI * 25.4
    print(f"marker {actual_mm:.2f}mm ({module_px}px/module) / "
          f"cell {cell_px / DPI * 25.4:.2f}mm / 左右余白 {margin_mm:.1f}mm")
    return page, actual_mm


def build_target(marker_mm: float) -> Image.Image:
    """A4 で 1 枚刷るだけで検出を試せる的。

    貼る用のシートは ID 0-3 が最初の行に横一列に並ぶので、そのままカメラを
    向けても 4 点が一直線になって射影変換が退化する。こちらは ID 0-3 を
    模型と同じ時計回り（左上・右上・右下・左下）に置いてある。
    """
    module_px = max(1, round(mm(marker_mm) / 6))
    marker_px = module_px * 6
    quiet_px = mm(QUIET_MM)
    page = Image.new("L", (mm(A4_W_MM), mm(A4_H_MM)), 255)
    draw = ImageDraw.Draw(page)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", size=mm(4))
    except OSError:
        font = ImageFont.load_default()

    inset = mm(18)
    aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    spots = [(inset, inset), (page.width - inset - marker_px, inset),
             (page.width - inset - marker_px, page.height - inset - marker_px),
             (inset, page.height - inset - marker_px)]
    for marker_id, (x, y) in enumerate(spots):
        draw.rectangle([x - quiet_px, y - quiet_px,
                        x + marker_px + quiet_px, y + marker_px + quiet_px], fill=255)
        img = cv2.aruco.generateImageMarker(aruco, marker_id, marker_px, borderBits=1)
        page.paste(Image.fromarray(np.asarray(img)), (x, y))

    draw.text((page.width // 2, page.height // 2 - mm(6)),
              "fluoro-sim alignment target", fill=110, font=font, anchor="mm")
    draw.text((page.width // 2, page.height // 2 + mm(2)),
              "ids 0-3 clockwise from top-left", fill=150, font=font, anchor="mm")
    draw.text((page.width // 2, page.height // 2 + mm(10)),
              "print at any scale - detection does not care", fill=150, font=font, anchor="mm")
    print(f"target: marker {marker_px / DPI * 25.4:.2f}mm on A4")
    return page


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mm", type=float, default=10.0, help="マーカーの一辺 (既定 10mm)")
    ap.add_argument("--out", default=None, help="出力名 (拡張子なし)")
    ap.add_argument("--target", action="store_true",
                    help="貼らずに検出だけ試すための A4 ターゲットを出す")
    args = ap.parse_args()

    if args.target:
        out = args.out or "marker-target"
        page = build_target(args.mm * 2)     # 机の上で試す前提なので大きめ
        page.save(f"{out}.pdf", "PDF", resolution=DPI)
        page.save(f"{out}.png", dpi=(DPI, DPI))
        print(f"wrote {out}.pdf / {out}.png")
        return

    args.out = args.out or "marker-sheet"
    page, actual_mm = build(args.mm)
    # PDF は等倍印刷用、PNG はコンビニの写真/シール紙プリント用（縁なしで
    # 数%オーバースキャンされるが、quiet zone も一緒に拡大されるので検出には響かない）
    page.save(f"{args.out}.pdf", "PDF", resolution=DPI)
    page.save(f"{args.out}.png", dpi=(DPI, DPI))
    print(f"wrote {args.out}.pdf / {args.out}.png (marker {actual_mm:.2f}mm)")


if __name__ == "__main__":
    main()
