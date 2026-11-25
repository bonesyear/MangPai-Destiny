import json
import os
import random
import sys
import urllib.request

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'output'))

import _eval_common as ec


def test_shared_redline_words_and_exemptions():
    assert '赴美' in ec.QIANYI_FORBID
    assert '清秀' in ec.XM_FORBID
    assert ec.xm_forbidden_scan('五官清秀，眉目英俊')
    assert ec.xm_forbidden_scan('丑陋之相')
    assert not ec.xm_forbidden_scan('乙丑')


def test_no_signal_honesty_requires_exact_template_and_no_assertion():
    assert ec.qianyi_honest_nosignal('没有迁移信号，一生安居本地')
    assert not ec.qianyi_honest_nosignal('无论走哪步大运，都宜外出闯荡、迁居他乡')
    assert not ec.qianyi_honest_nosignal('无迁移信号，但宜赴美发展')
    assert ec.xiangmao_honest_nosignal('无显著相貌特征')
    assert not ec.xiangmao_honest_nosignal('气质无可挑剔')


def test_missing_judge_counts_as_missed_flip():
    review = {'case': {'result': {'scores': {'官命': {'s': 2}}}}}
    agree, tot, hit, flip_tot, _per_dim, _div = ec.agreement_stats(
        review, {}, ['case'], ['官命'], {'官命': 'guan'})
    assert (agree, tot, hit, flip_tot) == (0, 0, 0, 1)


def test_string_scores_are_rejected():
    review = {'case': {'result': {'scores': {'官命': {'s': '2'}}}}}
    with pytest.raises(ValueError, match='s'):
        ec.review_stats(review, ['case'], ['官命'], set())
    review['case']['result']['scores']['官命'] = {'s': 0, 'red': 'false'}
    with pytest.raises(ValueError, match='red'):
        ec.review_stats(review, ['case'], ['官命'], set(), new_dims=('官命',))


def test_stratified_rejects_more_forced_than_sample_size():
    with pytest.raises(ValueError, match='强制'):
        ec.stratified_fill({}, ['a', 'b'], 1, random.Random(0))


def _run_eval(tmp_path, monkeypatch, responses, **kwargs):
    from mangpai.subjective import llm_backend

    def fake_call(*args, **kw):
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(llm_backend, 'call_deepseek', fake_call)
    ec.run_llm_eval(
        'review', ['case'], {'case': {}}, str(tmp_path),
        review_system='S', judge_system='J',
        make_review_user=lambda rec: 'U', make_judge_user=lambda rec: 'U',
        review_dims=('官命',), judge_dims=('guan',),
        review_out='review.jsonl', judge_out='judge.jsonl', **kwargs)


def test_run_eval_retries_errors_and_records_provenance(tmp_path, monkeypatch):
    from mangpai.subjective import llm_backend

    good = {
        'text': json.dumps({'scores': {'官命': {'s': 0, 'narr': '', 'eng': '', 'note': ''}}}),
        'usage': {'prompt_tokens': 1}, 'cost_cny': 0.01, 'price_tier': 'offpeak',
        'model': 'actual-model', 'requested_model': 'deepseek-v4-pro',
    }
    responses = [llm_backend.LLMBackendError('injected'), good]
    _run_eval(tmp_path, monkeypatch, responses)
    _run_eval(tmp_path, monkeypatch, responses)
    records = [json.loads(line) for line in (tmp_path / 'review.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(records) == 2
    assert 'api_error' in records[0] and 'result' not in records[0]
    result = records[1]
    assert result['model'] == 'actual-model'
    assert result['requested_model'] == 'deepseek-v4-pro'
    assert result['endpoint_host'] == 'api.deepseek.com'
    assert result['thinking'] is True
    assert len(result['system_sha256']) == 64
    assert result['timestamp']
    assert result['cost_cny'] == 0.01


def test_run_eval_schema_error_is_not_success(tmp_path, monkeypatch):
    response = {
        'text': json.dumps({'scores': {'官命': {'s': '2'}}}),
        'usage': {}, 'cost_cny': None, 'price_tier': 'offpeak', 'model': 'm',
    }
    _run_eval(tmp_path, monkeypatch, [response])
    record = json.loads((tmp_path / 'review.jsonl').read_text(encoding='utf-8'))
    assert 'schema_error' in record and 'result' not in record


def test_nondefault_evaluator_requires_explicit_opt_in(tmp_path, monkeypatch):
    monkeypatch.setenv('MANGPAI_LLM_BASE_URL', 'http://localhost:11434/v1/chat/completions')
    monkeypatch.delenv('MANGPAI_ALLOW_NONDEFAULT_EVALUATOR', raising=False)
    with pytest.raises(RuntimeError, match='非默认'):
        _run_eval(tmp_path, monkeypatch, [])


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, _limit=-1):
        return json.dumps(self.payload).encode('utf-8')


def _backend_response(monkeypatch, payload):
    from mangpai.subjective import llm_backend

    monkeypatch.setenv('MANGPAI_USE_LLM', '1')
    monkeypatch.setenv('MANGPAI_LLM_API_KEY', 'sk-local')
    monkeypatch.setenv('MANGPAI_LLM_RETRIES', '0')
    monkeypatch.setenv('MANGPAI_LLM_BASE_URL', 'http://example.invalid/v1/chat/completions')
    monkeypatch.setattr(urllib.request, 'urlopen', lambda req, timeout: _Response(payload))
    return llm_backend


def test_backend_uses_response_model_and_preserves_empty_content_usage(monkeypatch):
    payload = {
        'choices': [{'message': {'content': '{}'}}], 'model': 'actual-other',
        'usage': {'prompt_tokens': 10, 'completion_tokens': 5},
    }
    lb = _backend_response(monkeypatch, payload)
    result = lb.call_deepseek('S', 'U', model='deepseek-flash')
    assert result['model'] == 'actual-other'
    assert result['requested_model'] == 'deepseek-flash'
    assert result['cost_cny'] is None
    assert result['endpoint'].endswith('/chat/completions')
    assert result['thinking'] is True

    payload['model'] = 'deepseek-flash'
    payload['choices'][0]['message']['content'] = ''
    with pytest.raises(lb.LLMBackendError) as exc:
        lb.call_deepseek('S', 'U', model='deepseek-flash')
    assert exc.value.usage == payload['usage']
    assert exc.value.cost_cny is not None


def test_batch_merge_uses_timestamp_and_costs_all_attempts(tmp_path):
    records = [
        {'id': 'a', 'run_id': 'r1', 'timestamp': '2026-01-01T00:00:00+00:00',
         'cost_cny': 0.1, 'cost_usd': 0.01, 'parse_error': 'bad'},
        {'id': 'a', 'run_id': 'r1', 'timestamp': '2026-01-01T00:01:00+00:00',
         'cost_cny': 0.1, 'reading': {}},
        {'id': 'a', 'run_id': 'r2', 'timestamp': '2026-01-01T00:02:00+00:00',
         'cost_cny': 0.2, 'reading': {}},
    ]
    (tmp_path / 'batch_a.jsonl').write_text(
        '\n'.join(json.dumps(r) for r in records) + '\n', encoding='utf-8')
    attempts, latest = ec.load_batch(str(tmp_path))
    assert len(attempts) == 3
    assert len(latest) == 1 and latest[0]['run_id'] == 'r2'
    costs = ec.summarize_costs(attempts)
    assert costs['cost_cny'] == pytest.approx(0.4)
    assert costs['cost_usd'] == pytest.approx(0.01)


def _synthetic_case(cid='synthetic'):
    return {'id': cid, 'gender': '女', 'bazi': {
        'year': '甲子', 'month': '乙丑', 'day': '丙寅', 'hour': '丁卯'}}


def test_batch_run_case_records_reproduction_metadata(monkeypatch):
    import _llm_batch_trainset as batch

    def fake_call(system, user):
        return {'text': json.dumps({dim: {'conclusion': '数据不足', 'basis': [],
                                         'confidence': '低'}
                                    for dim in ('性格', '事业', '财运', '婚姻', '应期', '迁移', '相貌')}),
                'usage': {}, 'cost_cny': None, 'model': 'mock'}

    monkeypatch.setattr(batch, 'call_deepseek', fake_call)
    rec = batch.run_case(_synthetic_case())
    assert rec['run_id'] and rec['timestamp'] and rec['as_of_year']
    assert rec['engine_sha']['git_sha'] and rec['engine_sha']['tree_hash']
    assert len(rec['prompt_sha256']) == 64
    assert rec['features'] and rec['model'] == 'mock'


def test_batch_run_case_accepts_response_format_prefix(monkeypatch):
    import _llm_batch_trainset as batch

    reading = {dim: {'conclusion': '数据不足', 'basis': [], 'confidence': '低'}
               for dim in ('性格', '事业', '财运', '婚姻', '应期', '迁移', '相貌')}
    monkeypatch.setattr(batch, 'call_deepseek', lambda *args: {
        'text': '{"type":"json_object"}\n' + json.dumps(reading),
        'usage': {}, 'cost_cny': None, 'model': 'mock'})
    rec = batch.run_case(_synthetic_case())
    assert 'parse_error' not in rec
    assert rec['reading'] == reading


def test_batch_budget_stops_before_llm(monkeypatch):
    import _llm_batch_trainset as batch

    state = batch._budget_state()
    state['cap'] = state['spent'] = 0.01
    monkeypatch.setattr(batch, 'call_deepseek',
                        lambda *args: pytest.fail('预算耗尽后不应调用 LLM'))
    rec = batch.run_case(_synthetic_case(), state)
    assert rec['budget_exceeded'] is True
    assert 'features' not in rec


def test_batch_main_preserves_completed_records_on_error(tmp_path, monkeypatch):
    import _llm_batch_trainset as batch
    import time

    monkeypatch.setattr(batch, 'OUT_DIR', str(tmp_path))
    monkeypatch.setattr(batch.yaml, 'safe_load',
                        lambda f: [_synthetic_case('good'), _synthetic_case('bad')])
    monkeypatch.setattr(sys, 'argv', ['batch.py', '0', '2'])

    def fake_run(case, state):
        if case['id'] == 'bad':
            time.sleep(0.05)
            raise RuntimeError('injected interruption')
        return {'id': case['id'], 'cost_cny': 0}

    monkeypatch.setattr(batch, 'run_case', fake_run)
    with pytest.raises(RuntimeError, match='injected interruption'):
        batch.main()
    lines = (tmp_path / 'batch_0_2.jsonl').read_text(encoding='utf-8').splitlines()
    assert [json.loads(line)['id'] for line in lines] == ['good']


def test_valley_wait_is_portable_and_bounded():
    from datetime import datetime

    assert ec.seconds_to_valley(datetime(2026, 1, 1, 11, 0, 0)) == 3603
    assert ec.seconds_to_valley(datetime(2026, 1, 1, 15, 0, 0)) == 10803
    assert ec.seconds_to_valley(datetime(2026, 1, 1, 13, 0, 0)) == 0
    from datetime import timezone
    assert ec.seconds_to_valley(datetime(2026, 1, 1, 3, 0, 0, tzinfo=timezone.utc)) == 3603


def test_cross_dimension_redlines_are_structured():
    from mangpai.subjective.llm_channel import validate_reading

    data = {dim: {'conclusion': '数据不足', 'basis': [], 'confidence': '低'}
            for dim in ('性格', '事业', '财运', '婚姻', '应期', '迁移', '相貌')}
    data['事业']['conclusion'] = '海外业务可成'
    data['性格']['conclusion'] = '五官英俊'
    report = validate_reading(data, {}, {})
    red = {(v.get('kind'), v.get('dim')) for v in report['violations']}
    assert ('qianyi_redline', '事业') in red
    assert ('xiangmao_redline', '性格') in red


def test_n2_analyze_empty_batch_preserves_existing_ids(tmp_path, monkeypatch):
    import runpy

    batch = tmp_path / 'empty'
    batch.mkdir()
    out = tmp_path / 'out'
    out.mkdir()
    sentinel = out / 'l2_ids.json'
    sentinel.write_text('["keep"]', encoding='utf-8')
    monkeypatch.setenv('LLM_BATCH_DIR', str(batch))
    monkeypatch.setenv('T3_OUT_DIR', str(out))
    script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          'output', '_n2_analyze.py')
    with pytest.raises(SystemExit):
        runpy.run_path(script, run_name='__main__')
    assert sentinel.read_text(encoding='utf-8') == '["keep"]'


def test_n2_sample_rejects_mismatched_source(tmp_path, monkeypatch):
    import runpy

    for name, value in {
        'dump.json': {},
        'dump_source.json': {'batch': 'good', 'dump_sha256': 'x'},
        'l2_ids.json': {'batch': 'bad', 'n': 1, 'ids': []},
        'newdim_ids.json': {'batch': 'bad', 'n': 1, 'ids': []},
    }.items():
        (tmp_path / name).write_text(json.dumps(value), encoding='utf-8')
    monkeypatch.setenv('T3_OUT_DIR', str(tmp_path))
    script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          'output', '_n2_sample.py')
    with pytest.raises(ValueError, match='来源批次不一致'):
        runpy.run_path(script, run_name='__main__')


def test_v3_sample_freezes_dump_hash_and_strata(tmp_path, monkeypatch):
    import runpy

    dump = {f'c{i}': {'engine_key': {
        'caiming': {'tier_static': '富' if i % 2 else '贫'},
        'guanming': {'is_guanming': bool(i % 2)},
    }} for i in range(35)}
    (tmp_path / 'dump.json').write_text(json.dumps(dump), encoding='utf-8')
    (tmp_path / 'anchor_candidates.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'l2_ids.json').write_text('[]', encoding='utf-8')
    monkeypatch.setenv('T3_OUT_DIR', str(tmp_path))
    script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          'output', '_v3_sample.py')
    runpy.run_path(script, run_name='__main__')
    sample = json.loads((tmp_path / 'sample30.json').read_text(encoding='utf-8'))
    assert len(sample['sample']) == 30
    assert len(sample['dump_sha256']) == 64
    assert set(sample['strata']) == set(sample['sample'])


def test_clopper_pearson_zero_flip_upper_bound():
    import _t3_calibrate

    assert _t3_calibrate.clopper_pearson_upper(0, 30) == pytest.approx(0.095, abs=0.001)
    assert _t3_calibrate.clopper_pearson_upper(30, 30) == 1.0


def test_v3_judge_uses_its_own_output_dir(tmp_path, monkeypatch):
    import _v3_judge_sample as sample

    (tmp_path / 'dump.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'sample30.json').write_text('{"sample": []}', encoding='utf-8')
    monkeypatch.setattr(sample, 'OUT', str(tmp_path))
    seen = {}
    monkeypatch.setattr(sample._t3_eval, 'run',
                        lambda mode, ids, dump, **kw: seen.update(kw))
    sample.main()
    assert seen['out_dir'] == str(tmp_path)


def test_batch_analyze_reports_first_parse_and_separate_currencies(tmp_path, monkeypatch, capsys):
    import runpy

    records = [
        {'id': 'a', 'timestamp': '2026-01-01T00:00:00+00:00',
         'parse_error': 'bad', 'cost_usd': 0.01},
        {'id': 'a', 'timestamp': '2026-01-01T00:01:00+00:00',
         'violations': [], 'cost_cny': 0.1},
        {'id': 'b', 'timestamp': '2026-01-01T00:00:00+00:00',
         'violations': [], 'cost_cny': 0.2},
    ]
    (tmp_path / 'batch_test.jsonl').write_text(
        '\n'.join(json.dumps(r) for r in records) + '\n', encoding='utf-8')
    script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          'output', '_llm_batch_analyze.py')
    monkeypatch.setattr(sys, 'argv', [script, str(tmp_path)])
    runpy.run_path(script, run_name='__main__')
    output = capsys.readouterr().out
    assert '首轮解析失败=1/2' in output
    assert '当前解析失败=0/2' in output
    assert '¥0.30' in output and '$0.0100' in output


def test_rescore_record_features_and_year_are_reused():
    case = _synthetic_case()
    record = {'features': {'sentinel': True}, 'as_of_year': 2025}
    res, features = ec.engine_for_record(case, record)
    assert features == {'sentinel': True}
    assert res['input']['as_of'].startswith('2025-')


def test_fewshot_contamination_registry_matches_all_four_pillars():
    import yaml
    from mangpai.subjective.prompts.hao_style_fewshot import FEWSHOT_EXAMPLES

    cases = []
    for group in ('trainset', 'heldout'):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            group, 'cases.yaml')
        with open(path, encoding='utf-8') as f:
            cases.extend(yaml.safe_load(f))
    overlaps = set()
    for example in FEWSHOT_EXAMPLES:
        pillars = [part[:2] for part in example['bazi'].split()[:4]]
        for case in cases:
            if [case['bazi'][p] for p in ('year', 'month', 'day', 'hour')] == pillars:
                overlaps.add(case['id'])
    assert overlaps == ec.FEWSHOT_CONTAMINATED_IDS


def test_fewshot_outdated_conclusions_are_removed():
    from mangpai.subjective.prompts.hao_style_fewshot import FEWSHOT_EXAMPLES

    first = next(e for e in FEWSHOT_EXAMPLES if e['id'] == '第1期·生孩子')
    actress = next(e for e in FEWSHOT_EXAMPLES if e['id'] == '第14期·演员')
    assert '多婚之象' not in first['engine']
    assert '财命：富' in actress['engine']
    assert '财命：小康' not in actress['engine']
    assert '独身之象' not in actress['engine']
