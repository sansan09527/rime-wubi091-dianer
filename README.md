# rime-wubi091-dianer

基于**点儿词库2026春**的 Rime 091五笔输入方案。

## 词库信息

| 项目 | 说明 |
|------|------|
| 编码方案 | 091五笔（始创者：行走的风景） |
| 词库来源 | 点儿词库2026春（作者：晓览） |
| 总词条数 | 222,207 |
| z词条数 | 3,757（特殊符号/emoji/快捷输入） |

## 文件说明

| 文件 | 说明 |
|------|------|
| `wubi091.schema.yaml` | 方案配置 |
| `wubi091.dict.yaml` | 主词库 |
| `wubi091.extended.dict.yaml` | 扩展词库（用户自定义词条） |

## z 词条说明

091五笔的 z 键区为特殊编码区，包含符号、emoji、快捷短语等：

- `za` → `&` `@`
- `zb` → `%`
- `zc` → `×` `÷`
- `zaf` → `α`（希腊字母）
- `zax` → `/爱心`（emoji 引用）
- `zzy` → 注音符号（ㄅㄆㄇ...）

本方案中 z 词条**全部保留**，通过以下配置实现与 z 键其他功能的兼容：

- 单按 `z` → 重复上屏（history，优先级 10000）
- `za`/`zb` 等组合 → 正常查词库
- encoder 排除 `'^z.*$'`，不自动造 z 开头的词
- 反引号 `` ` `` 触发拼音反查

## 安装

### 小狼毫（Windows）

将 3 个 `.yaml` 文件复制到 `%APPDATA%\Rime\`，右键托盘图标 → 重新部署。

### 同文输入法 Trime（Android）

将 3 个 `.yaml` 文件复制到 `/sdcard/rime/`，在设置中重新部署。

### 其他 Rime 发行版

将文件复制到对应的 Rime 用户目录，重新部署即可。

## 致谢

- [行走的风景](https://github.com/aLIEz-QI) — 091五笔编码方案始创者
- [晓览](https://github.com/aLIEz-QI/Rime-wubi091) — 点儿词库作者
- [osfans/trime](https://github.com/osfans/trime) — 同文输入法
- [aLIEz-QI/Rime-wubi091](https://github.com/aLIEz-QI/Rime-wubi091) — 参考方案

## License

词库版权归点儿词库作者晓览所有，本仓库仅提供 Rime 格式转换。
