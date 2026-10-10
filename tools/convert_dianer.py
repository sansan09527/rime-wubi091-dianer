"""点儿词库（极点格式）→ Rime wubi091.dict.yaml + 微软五笔（WubiLex）导入码表。

做的事和「词库处理工具：QQ格式→打散格式（清爽版）」一样：一码多词拆成一码一词、去 ~、还原连接符。

用法: python convert_dianer.py <极点格式五笔词库.txt> <春季版 wubi091.dict.yaml> <输出目录> <版本名, 如 2026.summer> <中文版本名, 如 2026夏>

规则与 2026 春版一致（春版就是从极点格式转的，含 76 条 5 码的 zr 日文假名，冰凌格式限 4 码会丢掉它们）：
- 极点格式 [Text] 段每行「编码 词1 词2 ...」，词前 ~ 是生僻字/emoji 标记，去掉 ~ 保留词
- 词里的空格：点儿词库作者用连接符 $20（春夏都是），还原成空格；%20 是 WubiLex 的写法，顺手也兼容
- 候选顺序 = 文件顺序（方案 extended 词典是 sort: original），权重写行号只是占位
- 同一编码下重复的词只留第一次出现
- 生僻字库是单独的文件，不并入（春版也没并）
- 微软五笔导出：只留 ≤4 码；空格写成 WubiLex 认的 %20
"""
import sys
from collections import OrderedDict
from pathlib import Path

src, spring_dict, out_dir, ver, ver_cn = sys.argv[1:6]
out = Path(out_dir)
out.mkdir(parents=True, exist_ok=True)

lines = Path(src).read_text(encoding="utf-16").splitlines()
start = lines.index("[Text]") + 1
entries = OrderedDict()          # (code, word) -> None，保序去重；word 里已是真空格
bad = 0
for ln in lines[start:]:
    parts = ln.split(" ")
    code = parts[0]
    if len(parts) < 2 or not code.isascii() or not code.islower():
        bad += 1
        continue
    for w in parts[1:]:
        if w:
            entries.setdefault((code, w.lstrip("~").replace("$20", " ").replace("%20", " ")), None)

# --- Rime：春版文件头逐字保留（只换版本号），免得 encoder 规则之类被改动 ---
old_text = Path(spring_dict).read_text(encoding="utf-8")
old_head, old_body = old_text.split("\n...\n", 1)
head = old_head.replace("2026春", ver_cn).replace('"2026.spring"', f'"{ver}"') + "\n...\n"
rows = [f"{word}\t{code}\t{i}" for i, (code, word) in enumerate(entries, 1)]
(out / "wubi091.dict.yaml").write_text(head + "\n".join(rows) + "\n", encoding="utf-8", newline="\n")

# --- 微软五笔 / WubiLex：打散格式，码前词后，一码一行，UTF-16LE 带 BOM ---
ms_rows = [f"{code}\t{word.replace(' ', '%20')}" for code, word in entries if len(code) <= 4]
(out / "wubilex.txt").write_text("\r\n".join(ms_rows) + "\r\n", encoding="utf-16", newline="")

# --- 和春版对比 ---
old = set()
for l in old_body.splitlines():
    p = l.split("\t")
    if len(p) >= 2 and not l.startswith("#"):
        old.add((p[1], p[0]))
new = {(c, w) for c, w in entries if not w.startswith("#")}   # 以 # 开头的行在 Rime 里是注释，两版都一样
added, removed = new - old, old - new
rep = [f"极点源行数(去表头) {len(lines) - start}, 跳过 {bad}, 去重后 {len(entries)}",
       f"春版 {len(old)} 条 → 夏版 {len(new)} 条（不计 # 开头的 {len(entries) - len(new)} 条）；新增 {len(added)}，删除 {len(removed)}",
       f"含空格词条 {sum(' ' in w for _, w in entries)}；残留连接符 $20={sum('$20' in w for _, w in entries)} %20={sum('%20' in w for _, w in entries)}；残留 ~ 开头 {sum(w.startswith('~') for _, w in entries)}",
       f"5 码以上 {sum(len(c) > 4 for c, _ in entries)} 条（Rime 保留，微软五笔导出时去掉）；微软五笔导出 {len(ms_rows)} 行",
       "新增示例: " + "、".join(f"{w}({c})" for c, w in sorted(added)[:25]),
       "删除示例: " + "、".join(f"{w}({c})" for c, w in sorted(removed)[:25])]
(out / "report.txt").write_text("\n".join(rep) + "\n", encoding="utf-8")
print("ok")
