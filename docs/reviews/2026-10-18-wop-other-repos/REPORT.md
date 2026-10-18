# wop 其余仓库审查报告（2026-10-18）

范围：wop-java-sdk、wop-skills、wop-mcp、wop-web-tools（java-showcase、static-openapi 未深审：示例/工具类，低风险）。

## 1. wop-java-sdk —— 一项阻断，已修复（PR #43）

**阻断：RSA2048 实现无黄金向量背书**
- AlgorithmSuite 已注册 WOP-RSA2048-SHA256，但 wop-sdk-core/pom.xml 钉版 wopSpecsRef=4a50824 的 crypto-vectors.json 不含 rsa2048（实测 keys 仅 rsa3072/rsa4096/sm2；sha256 与钉值一致=钉版未漂移但内容陈旧）；specs main a1f7feb（PR #25）已含。
- 向量测试为硬编码套件方法（rsa3072SignMatchesGoldenVector 等），钉版升级不自动覆盖。
- 六仓中唯一缺 2048 向量验证。

**口径：默认套件未随五 SDK 统一**——双模板与 README 双语示例默认 WOP-RSA3072-SHA256。

**修复（fix/rsa2048-vector-pin，CI 全绿）：**
1. wopSpecsRef→a1f7feb + wopSpecsCryptoVectorsSha256→c7dd6574…（interop-cases 未变，其 sha256 与 InteropConformanceTest 哨兵免改）
2. 补 rsa2048SignMatchesGoldenVector / oaep2048UnwrapMatchesGoldenVector 两面字节级测试（对齐五仓覆盖基线：signature + oaep-unwrap）
3. 双模板与 README 示例默认改 WOP-RSA2048-SHA256；覆盖描述补 RSA2048

验证：core 全量 429 测试绿（新钉版构建期拉取 + sha256 校验通过）。

**架构优点**：构建期按 ref+sha256 从 specs 拉取、fail-closed（无副本漂移面）优于五 SDK 的 fixture 副本模式——五 SDK 后续可向此迁移。

## 2. wop-skills PR #23（factory 上游同步）—— 审查通过，可合

- 同步源真实：锚 7cf96c055 存在于 awesome-rules 本地 feedback/wop-skills-neutral-hostnames 分支（upstream-lock 指本地路径；GitHub 侧 im47cn/awesome-rules 对 bot 不可见，上游 PR #260 状态需 im47cn 本人确认）
- PR 分支 543 测试全绿（15 skipped）；upstream-sync-check --check 干净（full 面与上游字节一致）
- 与 main 无分叉（纯超集，MERGEABLE）
- 描述失真一节：「test_space_id_maps_path_namespace 在 main 实测红」已过期——main 该测试现已绿（后续 PR 自愈），不影响本 PR 增量价值

## 3. wop-mcp —— 无阻断

- keypair.py 密码学纪律好：CSPRNG（cryptography RSA2048 + secrets.randbelow SM2 d∈[1,n)）、私钥 0600 O_EXCL 落盘不回显、SDK 加载器契约自检（含 I5 曲线校验）、gmssl _kg 脆弱耦合有声明与回归
- 4 个工具均为文档查询+密钥生成，无签名/交易执行面

## 4. wop-web-tools —— 无阻断

- gm/gmcore.js = sm-crypto-v2 审计内置（非自实现国密），带 smGoldenSelfTest 黄金向量自测
- S1/S2 禁词门禁（scan_banned.mjs，pre-commit+CI）：无跨源资源/无网络 API 禁词/无存储 API——浏览器端隐私纪律成熟
- wf9 联调 fetch 目标仅网关占位域（gateway.example.com），无第三方外发

## 遗留

- awesome-rules 中性化分支的 GitHub 上游 PR #260 状态待 im47cn 确认（bot 不可见）
- java-showcase / static-openapi 未深审（后续如需）
