"""生成微软五笔 imscwubi .lex。

用法:
  python write_lex.py verify <现有.lex>            用现有文件解析出的记录重写一遍，检查是否逐字节一致
  python write_lex.py build <wubilex.txt> <输出.lex>  从「编码\\t词」打散格式（%20=空格）生成

文件结构（从 点儿词库26春.lex 推出来，verify 模式验证）：
  0x00 'imscwubi' | 0x08 u16 1, u16 1 | 0x0C u32 索引表偏移(0x40) | 0x10 u32 数据区偏移 | 0x14 u32 文件总长
  0x18 u32 0x78563412 | 其余 0 填到 0x40
  0x40 索引表：26 个 u32，第 i 个是首字母为 chr(97+i) 的第一条记录相对数据区的偏移（没有该字母就沿用下一个）
  数据区：每条 u16 记录长度 | u16 同码内序号(1 起) | u16 编码长度 | wchar 编码[4]（不足补 0）| 词(UTF-16LE) | u16 0
"""
import struct
import sys


def parse(b: bytes):
    data_start, total = struct.unpack_from("<II", b, 0x10)
    pos, recs = data_start, []
    while pos < total:
        rl, order, clen = struct.unpack_from("<HHH", b, pos)
        recs.append((b[pos + 6: pos + 14].decode("utf-16-le")[:clen],
                     b[pos + 14: pos + rl - 2].decode("utf-16-le", "surrogatepass")))
        pos += rl
    return b[:0x40], recs


def build(recs, header_template=None) -> bytes:
    body = bytearray()
    first = {}
    prev, order = None, 0
    for code, word in recs:
        order = order + 1 if code == prev else 1
        prev = code
        first.setdefault(code[0], len(body))
        w = word.encode("utf-16-le", "surrogatepass")
        c = code.encode("utf-16-le").ljust(8, b"\0")
        body += struct.pack("<HHH", 6 + 8 + len(w) + 2, order, len(code)) + c + w + b"\0\0"
    # 索引表：从 z 往前填，缺的字母沿用后一个字母的起点
    idx, nxt = [0] * 26, len(body)
    for i in range(25, -1, -1):
        nxt = first.get(chr(97 + i), nxt)
        idx[i] = nxt
    data_start = 0x40 + 4 * 26
    head = bytearray(header_template if header_template else
                     b"imscwubi" + struct.pack("<HHI", 1, 1, 0x40) + b"\0" * 0x30)
    struct.pack_into("<IIII", head, 0x10, data_start, data_start + len(body), 0x78563412, 0)
    return bytes(head[:0x40]) + struct.pack("<26I", *idx) + bytes(body)


mode = sys.argv[1]
if mode == "verify":
    b = open(sys.argv[2], "rb").read()
    head, recs = parse(b)
    out = build(recs)
    diff = next((i for i in range(min(len(b), len(out))) if b[i] != out[i]), None)
    print(f"records {len(recs)}, orig {len(b)} bytes, rebuilt {len(out)} bytes, identical={b == out}, first diff at {diff}")
else:
    rows = open(sys.argv[2], encoding="utf-16").read().splitlines()
    recs = []
    for r in rows:
        code, word = r.split("\t", 1)
        recs.append((code, word.replace("%20", " ")))
    open(sys.argv[3], "wb").write(build(recs))
    _, back = parse(open(sys.argv[3], "rb").read())
    print(f"built {len(recs)} records, read back {len(back)}, roundtrip ok={back == recs}")
