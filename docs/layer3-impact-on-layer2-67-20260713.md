# 第三层修复对第二层 67 例回测的影响评估

**日期**: 2026-07-13
**评估对象**: layer-3 三项修复（yongshen 方向判断 + 官命 over-fire 否决 + 阎锡山 L4）
**基准**: 第二层 67 例（docs/audit-phase2b-backtest.md），修复前 = residual-5-fix 后状态 ✅39/⚠️19/❌9
**工具**: /tmp/review/regression67.py（principled judge）+ compute_all 真实引擎核对

---

## 一、853 全量验证

| 检查 | 结果 |
|---|---|
| verify_mangpai | 361 passed, 0 failed |
| verify_dayun | 70 passed, 0 failed |
| objective verify | 422 passed, 0 failed |
| pytest | 101 passed, 5 xfailed |

**853 全绿。但 853 是引擎自洽性检查 + objective 检测层，不覆盖书例方向/veto 场景，绿 ≠ 书例准确率无回归**（见下）。

---

## 二、修复前后对比表

### 2a. principled judge（regression67.py，cat4 直调 `classify_guanming_combo` 原始路径，**对 veto 失明**）

| | ✅ | ⚠️ | ❌ |
|---|---|---|---|
| 修复前（pre-layer-3） | 39 | 19 | 9 |
| 修复后（principled） | 38 | 20 | 9 |
| Δ | -1 | +1 | 0 |

唯一可见变化：gl:阎锡山 ✅->⚠️（L3->L4，layer-3 P1 D 故意）。9 个 ❌ 一个没动。

### 2b. 真实引擎（compute_all，含 veto/方向 cap）— 书例准确率真相

| 类目 | 修复前 ✅/⚠️/❌ | 修复后 ✅/⚠️/❌ | Δ |
|---|---|---|---|
| cat1 zuogong (18) | 10/5/3 | 10/5/3 | 0 |
| cat2 gongliang (15) | 11/3/1 | 10/4/1 | 阎锡山 ✅->⚠️ |
| cat3 xiangfa (18) | 8/7/3 | 8/7/3 | 0（静态） |
| cat4 cai (4) | 1/2/1 | 1/2/1 | 0（cap 不改 primary） |
| cat4 guan (6) | 5/1/0 | 2/1/3 | **3 例 veto 误火** |
| cat5 (6) | 4/1/1 | 4/1/1 | 0 |
| **合计 (67)** | **39/19/9** | **35/20/12** | **✅-4 ⚠️+1 ❌+3** |

**真实引擎净回归 4 例（3 官命 + 阎锡山），0 例缓解。** principled judge 因 cat4 绕过 veto，只看到 1/4（阎锡山），对 3 官命误火完全失明。

---

## 三、9 个 ❌ 逐个变化

| # | 案例 | 修复前 | 修复后（真实引擎） | 方向判断是否触发 | 变化 |
|---|---|---|---|---|---|
| 1 | zg:制例二（丙辛戊壬/午丑寅戌）| ❌ primary=生用 lv5 | ❌ 同 | 是（R1 severe，glL1）| 无缓解；zuogong primary 错误未动 |
| 2 | zg:化例二（戊壬丙壬/申戌寅辰）| ❌ primary=生用 | ❌ 同 | 否 | 无变化（坐下印漏检）|
| 3 | zg:化例三中堂（甲丙己甲/子寅丑子）| ❌ primary=合用 | ❌ 同 | 否 | 无变化 |
| 4 | gl:克林顿（丙丙乙戊/戌申丑寅）| ❌ L2 | ❌ **L1** | **是（R1 severe 误火）**| **恶化**：L2->L1，且方向判 凶（破财），书为 L4 总统 |
| 5 | xf:化象:纺织 | ❌ 空 | ❌ 同 | 否 | 无变化（缺生克化象）|
| 6 | xf:化象:服装 | ❌ 空 | ❌ 同 | 否 | 无变化 |
| 7 | xf:借象:寅卯 | ❌ 缺同五行互借 | ❌ 同 | 否 | 无变化 |
| 8 | cai:过河拆桥 | ❌ guohe=False | ❌ 同 | 否 | 无变化（模板缺口）|
| 9 | xueli:博士（甲甲辛甲/寅戌亥午）| ❌ val=低 | ❌ 同 | 是（fanju+R1）| 无缓解；学历之神漏官杀未动 |

**结论：9 个 ❌ 全部仍为 ❌。8 例完全未动（结构/模板缺口），1 例（克林顿）被方向判断恶化（L2->L1 + 凶向误判）。0 例被自动缓解。**

---

## 四、标注：方向判断自动缓解 vs 仍需单独修

### 被方向判断自动缓解的：0 例

9 个 ❌ 的根因全部是**结构性缺口**（primary 类型错 / xiangfa 函数缺 / 模板窄 / 学历之神漏），与"吉凶方向"正交。方向判断处理的是"结构对但吉凶方向错"，对这 9 例无效。

### 仍需单独修：9 例（全部）+ layer-3 新引入的 4 例回归

**9 个原 ❌（按 docs/layer2-9gap-analysis-20260713.md 五分组）**：
- 分组一 串行链（制例二/化例二/化例三）：主功用串行链非强度权重，需范式重构
- 分组三/四 xiangfa（化象纺织/服装、借象寅卯）：补生克化象 + 同五行互借
- 分组五 模板（过河拆桥、博士学历）：过河拆桥补六合/暗合方向；学历之神补官杀

**layer-3 新引入的 4 例回归（不在原 9 ❌ 内）**：
- 财制印/带帽/公门武职：官命被 veto 误否决（✅->❌）
- 阎锡山：principled 判 ✅->⚠️（郝金阳标准下为 ✅，gongliang-第六章标准 book=3 下为 ⚠️，**标准冲突**）

---

## 五、关键发现：layer-3 方向判断在 67 例上系统性误火

### 5a. 误火面：19/64 例被标 direction=凶

对 67 例去重 64 八字跑 compute_all，**19 例 direction=凶**，而 2 个真凶例（抢劫/受贿，laoyu 高）**反而未触发**（laoyu 已被 layer-3 从 veto 触发器剔除）。误火与漏检同时存在。

| 触发源 | 误火例数 | 机制 |
|---|---|---|
| 反局 fanju（zhengfan 模块） | 13 | "日柱做功 vs 全局做功方向相背"判据过松，官命/贵命常误判反局 |
| 比劫夺财 R1（yongshen） | 7 | **bug：day_gan 自身被归为比劫**，"日主克财"（正常我克者财）误计为夺财 |
| 两者皆有 | 1（博士）| - |

### 5b. R1 比劫夺财 bug 根因（yongshen.py:149-153）

```python
fc = _wx_cat(dw, _pos_main_wx(fp, gans, zhis))   # fp='day_gan' 时 = day_wx
tc = _wx_cat(dw, _pos_main_wx(tp, gans, zhis))
if fc == '比劫' and tc == '财':   # day_gan 克财 -> fc='比劫'(自党) 误中
```

`_wx_cat(day_wx, day_wx)` 返回 '比劫'，故日主克财被当作比劫夺财。段氏"比劫夺财"特指**同辈（非日主）**夺财，日主克财=正常财关系。

- 财制印（癸日）：2 个 R1 hits **全是** `day_gan(比劫)->..._gan(财)`，排除 day_gan 后 hits=0，整个误否决消失
- 克林顿（乙日）：1 真 hit（寅克丑）+ 1 day_gan bug hit（乙克戊）；排除后 severe->normal，cap L1->L2

### 5c. 反局 veto 误火（带帽/公门武职）

zhengfan 模块对官命判反局：带帽"日柱做功指向土,木 vs 全局木"、公门"日柱指向木,金 vs 全局木"。该判据在印戴官帽/七杀入墓等官命上系统性偏松，被 veto 无条件信任。

### 5d. principled judge 方法论失明

regression67.py cat4 调 `classify_guanming_combo`（原始无否决路径），而 veto 在 `assess_guanming_level`（engine 路径）内，由新模块 `assess_direction_signals` 驱动。故 principled judge 对 layer-3 否决**完全失明**，显示 cat4 guan ✅5/⚠️1/❌0，真实引擎实为 ✅2/⚠️1/❌3。

---

## 六、结论与建议

1. **layer-3 三项修复对第二层 9 个 ❌ 零缓解**：9 例根因皆为结构/模板缺口，与方向正交。
2. **layer-3 在 67 例上净回归 4 例**（真实引擎 ✅39->35）：3 官命 veto 误火（隐于 principled judge）+ 阎锡山 ✅->⚠️（标准冲突）。
3. **方向判断系统性误火**：19/64 被标凶，2 真凶例漏检；R1 有 day_gan-as-比劫 bug，反局判据过松。
4. **principled judge 失明**：cat4 绕过 veto，需改调 `analyze_guanming`（engine 路径）或加 compute_all 判定。
5. **建议**：
   - 修 R1 bug：`detect_bijiao_duocai` 排除 day_gan（及日支本气=日主五行？）作比劫 actor → 直接解 财制印 + 缓和 克林顿
   - 反局 veto 加门槛：仅当反局为**主功方向**且无正向官命结构时否决，或降为降档不否决
   - principled judge cat4 改走 engine 路径，否则后续方向/veto 类修复无法被回测捕获
   - 阎锡山：明确两套标准（郝金阳 L4 vs gongliang-第六章 L3），回测 book level 取其一并对齐

**853 绿但书例准确率回退**：印证 853 自洽检查与书例方向/veto 场景正交，需补方向/veto 的书例断言进 pytest。
