# 全模块独立复审计划（LLM 通路前置）

> 目的：实现 LLM 推演通道前，由 Kimi CLI（独立于历史 CC 审计）重新审查全部模块算法是否符合段氏著作/知识库内容。
> 审计原则（用户铁律）：列全所有问题不筛选取舍；每批独立验证；配额分批消耗。
> 每批输出：审计报告写归档 `kimi-audit-<批>-2026-08.md` + 300 字摘要；问题分 P0（算法偏离）/P1（缺书锚）/P2（注释/口径疑点）三级。

## 批次划分（10 批）

| 批 | 模块 | 对照源 |
|----|------|--------|
| 1 基础语法层 | constants/canggan/changsheng/nayin/zihe/he_types | 渊海子平/真诠/知识库§1 |
| 2 做功层 | zuogong_detect/zuogong_confirm/tiyong/binzhu/zeishen_bushen | 段氏理象学/知识库§4.1 |
| 3 功量象法层 | gongliang/muku/xiangfa/xiangfa_ops | 段氏中级/高级/知识库§4 |
| 4 命局正反层 | zhengfan/yunfan/yingqi/yingqi_subj | 段氏正反局/岁运/知识库§4 |
| 5 岁运层 | dayun/liunian/jiaoyun/laoyu | 段氏大运流年/知识库§4 |
| 6 判定层A | caiming/guanming/yongshen/juefa | 段氏财官/知识库§3/§5 |
| 7 判定层B | zhiye/hunyin/zaihuo/xueli/liuqin | 段氏职业婚姻灾祸/知识库§3 |
| 8 杂项层 | shensha/shenshu/shipaige/gongshen/gongfei/gongmen_wuzhi | 段氏神煞/郑民生碎片/知识库§4 |
| 9 辅助层 | bazi_calc/advanced/biqi/body_parts/chuangong/soil_type/virtual_solid/wood_type/anhe | 渊海子平/知识库§1 |
| 10 主观层 | narrative/schools/engine编排/payload | SOUL.md/知识库§0/§8 |

## 每批审计步骤（通用）
1. 读模块源码（mangpai/objective/ 或 subjective/）
2. 读对应著作原文（mangpai/docs/duan-books/*.txt 或 yuanhaiziping/ 等）+ 知识库相关章节
3. 逐函数对照：算法是否符合书例/书诀？有无偏离、遗漏、过度推断？
4. 跑模块测试（pytest 相关文件）确认现状
5. 输出问题清单（全列不筛选）：P0 算法偏离书义 / P1 缺书锚或口径疑点 / P2 注释或边缘
6. 写归档 + 300 字摘要

## ⚠️ 对照纪律（2026-08-15 强化，批5 起强制）
1. **原著优先**：对照源以段氏 txt 原文为第一依据（duan-books/*.txt 的原文+行号）；知识库仅作**定位索引**（§5 书锚清单→翻原著原文验证），不作判定依据
2. **挑战知识库**：发现知识库与原著不符 → 以原著为准 + 在报告中单列「知识库勘误」节（批3 已有先例：岳飞锚数字漂移）
3. **备案不豁免**：知识库中「已备案/已裁定/已收档」字样**不构成审查豁免**——备案本身可能错，须独立验证其依据
4. 每个 P0/P1 必须带**原著行号**（不是知识库章节号）；知识库引用仅作辅助定位

## 红线
- 只审计不改码（修复等全部批次完成后统一规划，或用户逐批批准）
- 不碰留出集；测试只跑不修
