# 脱脂内示データ抽出

内示CSVと脱脂ひな形（Excel）をドラッグ＆ドロップすると、背番ごとに日別数量と3か月分の合計を抜き出し、Excelでダウンロードできるツールです。

## ツールを開く
**https://overbridge038-lnk.github.io/dasshi-naiji-HONDA-/**

（GitHub Pages。ダウンロードした `脱脂内示データ抽出.html` をダブルクリックしても同じように動きます）

## 使い方
1. 上のURLを開く（Chrome / Edge）
2. 内示CSV（協豊○○.csv）とひな形（.xlsx）を画面にドロップ
3. 赤・黄の行を確認して「Excelダウンロード」

インターネット接続は不要です。

## フォルダ構成
| 場所 | 中身 |
|---|---|
| `脱脂内示データ抽出.html` | ツール本体 |
| `icon/` | アイコン（ショートカットには `dasshi_icon.ico`） |
| `index.html` | 短いURLで開いたときにツール本体へ移動するページ |
| `sample/` | テスト用のCSV・ひな形・期待結果（CSVの単価・金額は空欄にしてあります） |
| `tests/` | 自動テスト |
| `output/` | テストで作られたExcelの置き場 |
| `CLAUDE.md` | Claude Code向けの仕様・開発ルール |

## Claude Codeで続きを開発するとき
このフォルダで `claude` を起動すると、`CLAUDE.md` の仕様を読んだ状態で始められます。
