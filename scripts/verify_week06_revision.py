"""第六週修訂版靜態、離線、假API契約檢查；絕不連線或安裝套件。"""
import ast
import contextlib
import io
import json
import os
import re
import sys
import types
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def schema_check(schema):
    """核對本課使用的object/array契約，不宣稱是完整Schema validator。"""
    if schema.get('type') == 'object':
        assert schema.get('additionalProperties') is False
        assert set(schema['required']) == set(schema['properties'])
        assert len(schema['required']) == len(set(schema['required']))
        for field in schema['properties'].values():
            schema_check(field)
    if schema.get('type') == 'array':
        schema_check(schema['items'])
    for child in schema.get('$defs', {}).values():
        schema_check(child)


def load(edition):
    path = next((ROOT / 'week06').glob(f'*150分鐘修訂版_{edition}.ipynb'))
    notebook = json.loads(path.read_text(encoding='utf-8'))
    ids = [c['id'] for c in notebook['cells']]
    assert len(ids) == len(set(ids))
    env = {'__name__': '__main__'}
    sdk = types.ModuleType('openai')

    def forbidden_client(*args, **kwargs):
        raise AssertionError('離線順序檢查不應建立真實client')

    sdk.OpenAI = forbidden_client
    # 禁止讀取本機既有金鑰或Colab Secret，以假SDK隔離一切模型呼叫。
    colab = types.ModuleType('google.colab')
    colab.userdata = types.SimpleNamespace(get=lambda key: '')
    ordinary = 0
    with patch.dict(sys.modules, {'openai': sdk, 'google.colab': colab}), patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
        with contextlib.redirect_stdout(io.StringIO()):
            for cell in notebook['cells']:
                assert cell['cell_type'] in ['markdown', 'code']
                source = ''.join(cell['source'])
                assert not re.search(r'\?{4,}|\ufffd|sk-[A-Za-z0-9_-]{20,}', source)
                if cell['cell_type'] != 'code':
                    continue
                assert cell['outputs'] == [] and cell['execution_count'] is None
                if any(line.lstrip().startswith(('%', '!')) for line in source.splitlines()):
                    continue
                ast.parse(source)
                ordinary += 1
                exec(compile(source, cell['id'], 'exec'), env)
    assert env['client'] is None
    assert all(value is False for name, value in env.items() if name.startswith('RUN_'))
    return notebook, env, ordinary


def run_cell(notebook, env, key):
    source = ''.join(next(c for c in notebook['cells'] if c['id'] == f'w06r-{key}')['source'])
    # 測試時只開啟此格旗標；正式教材仍全部False。
    source = re.sub(r'(RUN_[A-Z_]+ = )False', r'\1True', source)
    with contextlib.redirect_stdout(io.StringIO()):
        exec(source, env)


def teacher_checks(notebook, env):
    run_cell(notebook, env, 'guided-check')
    # 檢查器必須擋下只複製外層、偷偷修改原Schema的實作。
    original_builder = env['build_practice_event_schema']
    from copy import deepcopy
    original_event = deepcopy(env['event_schema'])

    def mutating_builder():
        result = original_builder()
        env['event_schema']['properties']['title']['description'] = '不應修改原規格'
        return result

    env['build_practice_event_schema'] = mutating_builder
    try:
        run_cell(notebook, env, 'guided-check')
    except AssertionError:
        pass
    else:
        raise AssertionError('G檢查應擋下原Schema副作用')
    env['event_schema'] = original_event
    env['build_practice_event_schema'] = original_builder
    run_cell(notebook, env, 'guided-check')
    run_cell(notebook, env, 'support-schema-check')
    run_cell(notebook, env, 'support-local-check')
    run_cell(notebook, env, 'b-local')
    run_cell(notebook, env, 'c-check')
    for name in ['event_schema', 'assignment_schema', 'support_schema']:
        schema_check(env[name])
    schema_check(env['practice_event_schema'])
    for name in ['ReadingCard', 'ReviewInsight', 'OrderInfo', 'MeetingMinutes']:
        schema_check(env[name].model_json_schema())

    calls = []

    def create(**request):
        calls.append(request)
        assert request['store'] is False
        if 'text' not in request:
            return env['fake_response'](json.dumps({'title': 'AI專題', 'date': '下週三', 'time': '14:00', 'location': 'A203', 'owner': None}))
        format_spec = request['text']['format']
        assert format_spec['type'] == 'json_schema' and format_spec['strict'] is True
        schema_check(format_spec['schema'])
        if format_spec['name'] == 'support_ticket':
            case = next(case for case in env['SUPPORT_TESTS'] if case['input'] == request['input'])
            data = dict(case['expected'], summary='虛構測試摘要')
        elif format_spec['name'] == 'course_assignments':
            data = env['assignment_fixture']
        else:
            data = {'title': 'AI專題', 'date': '下週三', 'time': '14:00', 'location': 'A203', 'owner': None}
        return env['fake_response'](json.dumps(data, ensure_ascii=False))

    def parse(**request):
        calls.append(request)
        assert request['store'] is False
        model_cls = request['text_format']
        fixture = env['review_fixture'] if model_cls is env['ReviewInsight'] else env['order_fixture']
        response = env['fake_response']()
        response.output_parsed = model_cls.model_validate(fixture)
        return response

    fake_client = types.SimpleNamespace(responses=types.SimpleNamespace(create=create, parse=parse))
    env['client'] = fake_client
    expected_counts = {'live-comparison': 1, 'event-structured': 1, 'support-single': 1, 'support-batch': 3,
                       'b-live': 1, 'c-live': 1, 'assignment-offline': 1}
    for key, count in expected_counts.items():
        before = len(calls)
        run_cell(notebook, env, key)
        assert len(calls) - before == count, key
    assert all(row['extraction_ok'] and row['matches'] for row in env['support_rows'])
    assert env['review_ok'] and env['order_ok']
    assert env['ordinary_ok'] and env['event_usable']
    assert env['calculate_order'](env['order_result']) == (2230, 2290)

    # API失敗／拒答／中斷／非法資料不能宣告抽取成功。
    def with_response(response):
        return types.SimpleNamespace(responses=types.SimpleNamespace(create=lambda **kw: response, parse=lambda **kw: response))

    for response in env['failure_cases'].values():
        ok, result = env['extract_structured_safe']('測試', env['event_schema'], 'test', api_client=with_response(response))
        assert not ok and isinstance(result, str)
    for data in env['invalid_support_cases']:
        ok, result = env['extract_support_ticket']('測試', api_client=with_response(env['fake_response'](json.dumps(data))))
        assert not ok and '欄位檢查失敗' in result
    before = len(calls)
    assert not env['extract_structured_safe'](' ', env['event_schema'], 'empty', api_client=fake_client)[0]
    assert len(calls) == before
    ok, result = env['extract_structured']('文字', env['ReviewInsight'], api_client=with_response(env['fake_response']()))
    assert not ok and 'output_parsed' in result
    for response in env['failure_cases'].values():
        if response.status != 'completed' or env['get_refusal_reason'](response):
            response.output_parsed = env['ReviewInsight'].model_validate(env['review_fixture'])
            assert not env['extract_structured']('文字', env['ReviewInsight'], api_client=with_response(response))[0]

    def fail(**kw):
        raise RuntimeError('模擬網路失敗')

    failing = types.SimpleNamespace(responses=types.SimpleNamespace(create=fail, parse=fail))
    assert not env['extract_support_ticket']('文字', api_client=failing)[0]
    assert not env['extract_structured']('文字', env['ReviewInsight'], api_client=failing)[0]
    # 一般prompt失敗的格子仍可完成，下一格Structured可獨立執行。
    env['client'] = failing
    run_cell(notebook, env, 'live-comparison')
    assert env['ordinary_ok'] is False and '模擬網路失敗' in env['ordinary_result']
    env['client'] = fake_client
    run_cell(notebook, env, 'event-structured')
    assert env['event_usable'] is True
    # 合法JSON但缺欄位不能被列為可用事件。
    env['client'] = with_response(env['fake_response']('{"title":"部分事件"}'))
    run_cell(notebook, env, 'live-comparison')
    run_cell(notebook, env, 'event-structured')
    assert env['ordinary_ok'] is False and env['ordinary_errors']
    assert env['event_ok'] is True and env['event_usable'] is False and env['event_errors']
    env['client'] = fake_client
    copy = env['get_schema'](env['schema_registry'], 'course_event_v1')
    copy['properties']['title']['description'] = '測試修改'
    assert env['schema_registry']['course_event_v1']['properties']['title']['description'] != '測試修改'
    return expected_counts


def main():
    student, student_env, sc = load('學生版')
    teacher, teacher_env, tc = load('教師版')
    assert [(c['id'], c['cell_type']) for c in student['cells']] == [(c['id'], c['cell_type']) for c in teacher['cells']]
    changed = [a['id'] for a, b in zip(student['cells'], teacher['cells']) if a['source'] != b['source']]
    assert set(changed) == {'w06r-edition', 'w06r-guided-impl', 'w06r-support-schema', 'w06r-support-impl', 'w06r-b-model', 'w06r-c-models'}
    for function in ['build_practice_event_schema', 'build_support_schema', 'extract_support_ticket']:
        try:
            student_env[function](*(['文字'] if function == 'extract_support_ticket' else []))
        except NotImplementedError:
            pass
        else:
            raise AssertionError('學生骨架不應冒充完成')
    for name, fixture in [('ReviewInsight', 'review_fixture'), ('OrderInfo', 'order_fixture')]:
        try:
            student_env[name].model_validate(student_env[fixture])
        except student_env['ValidationError']:
            pass
        else:
            raise AssertionError('空白模型不應通過練習')
    for cell in teacher['cells']:
        if cell['cell_type'] == 'code':
            assert 'TODO' not in ''.join(cell['source'])
    counts = teacher_checks(teacher, teacher_env)
    print(json.dumps({'cells': len(student['cells']), 'markdown': sum(c['cell_type'] == 'markdown' for c in student['cells']),
                      'ordinary_python': [sc, tc], 'paired_differences': changed,
                      'fake_api_counts': counts, 'real_api_calls': 0, 'status': 'passed'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
