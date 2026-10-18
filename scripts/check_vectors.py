#!/usr/bin/env python3
"""向量真源结构门禁：crypto/interop 两 JSON 的结构完整性校验（CI 与本地共用）。

specs 是五仓 SDK fixture 的唯一真源，坏数据合入即同时污染全部黄金向量测试；
本仓无运行时代码，完整性=JSON 可解析+顶层节齐全+黄金套件在位+向量节非空且逐项有 id。
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CRYPTO = ROOT / "crypto" / "crypto-vectors.json"
INTEROP = ROOT / "interop" / "v1" / "interop-cases.json"

CRYPTO_SECTIONS = [
    "_meta", "inputs", "keys", "digest", "messageEncrypt",
    "signature", "keyEncrypt", "dekPayload", "formatRules",
]
VECTOR_SECTIONS = [
    "digest", "messageEncrypt", "signature", "keyEncrypt",
    "dekPayload", "formatRules",
]
GOLDEN_SUITES = {"rsa2048", "sm2"}  # 五仓钉版拉取的最低黄金面
# 按 kind 分派的必需字段：build 型给实现侧输入/期望，verify 型给模拟网关响应/断言
CASE_FIELDS = {
    "build": ["id", "kind", "suite", "level", "input", "expected"],
    "verify-positive": ["id", "kind", "suite", "level", "response", "expect"],
    "verify-negative": ["id", "kind", "suite", "level", "response", "expect"],
}


def check_crypto(data: dict, errors: list[str]) -> None:
    for section in CRYPTO_SECTIONS:
        if section not in data:
            errors.append(f"crypto: 缺顶层节 {section}")
    if "keys" in data:
        missing = GOLDEN_SUITES - set(data["keys"])
        if missing:
            errors.append(f"crypto: 黄金套件缺失 {sorted(missing)}")
    for section in VECTOR_SECTIONS:
        items = data.get(section) or []
        if not items:
            errors.append(f"crypto: 向量节 {section} 为空")
            continue
        for i, item in enumerate(items):
            if "id" not in item:
                errors.append(f"crypto: {section}[{i}] 缺 id")


def check_interop(data: dict, errors: list[str]) -> None:
    for section in ("_meta", "cases"):
        if section not in data:
            errors.append(f"interop: 缺顶层节 {section}")
    cases = data.get("cases") or []
    if not cases:
        errors.append("interop: cases 为空")
    for i, case in enumerate(cases):
        fields = CASE_FIELDS.get(case.get("kind"))
        if fields is None:
            errors.append(f"interop: cases[{i}] 未知 kind {case.get('kind')!r}")
            continue
        for field in fields:
            if field not in case:
                errors.append(f"interop: cases[{i}] 缺 {field}")
    # caseCount 一致性：手工补 case 忘更计数的典型数据仓腐化
    declared = (data.get("_meta") or {}).get("caseCount")
    if isinstance(declared, int) and declared != len(cases):
        errors.append(f"interop: _meta.caseCount={declared} 与实际 {len(cases)} 不符")


def main() -> int:
    errors: list[str] = []
    for path, checker in ((CRYPTO, check_crypto), (INTEROP, check_interop)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        checker(data, errors)
    for error in errors:
        print(f"::error::{error}")
    print(f"结构门禁：{len(errors)} 处错误")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
