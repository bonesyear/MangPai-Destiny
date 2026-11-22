# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_case_files_have_no_raw_quotes_and_neutral_names():
    for rel in ('mangpai/tests/heldout/cases.yaml', 'mangpai/tests/trainset/cases.yaml'):
        cases = yaml.safe_load((ROOT / rel).read_text(encoding='utf-8'))
        assert all('raw_quote' not in case for case in cases)
        assert all(case['name'] == case['id'] for case in cases)


def test_calibration_labels_are_deidentified():
    paths = [
        'mangpai/calib_zhenbao.py', 'mangpai/verify_layer3_checkpoint.py',
        'mangpai/tests/calib_assertions.yaml', 'mangpai/tests/test_zhiye.py',
    ]
    private_names = ('李凡' + '丁', '刘' + 'XX', '阎' + '锡' + '山')
    for rel in paths:
        text = (ROOT / rel).read_text(encoding='utf-8')
        assert not any(name in text for name in private_names), rel


def test_review_file_is_not_tracked():
    assert not (ROOT / 'mangpai/tests/heldout/review.txt').exists()


def test_book_index_has_no_prose_or_watermark():
    for path in (ROOT / 'mangpai/docs/book-index').glob('*.md'):
        for line in path.read_text(encoding='utf-8').splitlines()[2:]:
            assert not any(token in line for token in ('。', '；', '眉批', 'yibooks')), (
                path.name, line)


def test_env_and_review_ignore_rules():
    for rel in ('.env.production', 'deploy/test.env', 'mangpai/tests/heldout/review.txt'):
        proc = subprocess.run(['git', 'check-ignore', '--no-index', '-q', '--', rel], cwd=ROOT)
        assert proc.returncode == 0, rel


def test_privacy_discloses_actual_llm_payload():
    text = (ROOT / 'docs/privacy-policy.md').read_text(encoding='utf-8')
    assert '流年公历年份' in text and '用户提问原文' in text
    assert '八字干支、性别、出生地经度、系统提示词' not in text
