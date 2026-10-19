"""驗證簡化版的獨立執行、練習正負例與假API路徑；絕不連線。"""
from pathlib import Path
from types import SimpleNamespace, ModuleType
from unittest.mock import patch
import ast
import contextlib
import importlib.util
import io
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('simple_builder', ROOT/'scripts/build_week06_simple.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class SetFlags(ast.NodeTransformer):
    def __init__(self, flags):
        self.flags = flags

    def visit_Assign(self, node):
        if len(node.targets)==1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in self.flags:
                node.value = ast.Constant(self.flags[name])
        return self.generic_visit(node)


def run(cell, ns, **flags):
    source = ''.join(cell['source'])
    if '%pip' in source:
        return
    tree = ast.fix_missing_locations(SetFlags(flags).visit(ast.parse(source)))
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(tree, cell['id'], 'exec'), ns)


def response(data=None, status='completed', refusal=None, text=None, parsed=None):
    contents = [] if refusal is None else [SimpleNamespace(type='refusal', refusal=refusal)]
    return SimpleNamespace(status=status, output=[SimpleNamespace(type='message', content=contents)],
                           output_text=json.dumps(data, ensure_ascii=False) if text is None else text,
                           output_parsed=parsed)


EVENT = {'title': 'AI專題討論', 'date': '下週三', 'time': '14:00', 'location': 'A203', 'owner': None}
SUPPORT = {'category': '帳務問題', 'urgency': 'high', 'summary': '重複扣款請今天處理', 'needs_reply': True}
REVIEW = {'customer_name': '小明', 'rating': 5, 'sentiment': 'positive', 'summary': '好吃且服務親切'}
ORDER = {'order_id': 'A1023', 'customer_name': '範例小陳', 'shipping_fee': 60,
         'items': [{'item_name': '藍牙耳機', 'quantity': 2, 'unit_price': 990},
                   {'item_name': '保護殼', 'quantity': 1, 'unit_price': 250}]}


class FakeResponses:
    def __init__(self, override=None):
        self.calls = []
        self.override = override

    def create(self, **request):
        self.calls.append(request)
        assert request['store'] is False
        assert isinstance(request['input'], str) and request['input'].strip()
        if 'text' in request:
            fmt = request['text']['format']
            assert fmt['type']=='json_schema' and fmt['strict'] is True
            schema = fmt['schema']
            assert schema['type']=='object' and schema['additionalProperties'] is False
            assert set(schema['properties'])==set(schema['required'])
        if self.override is not None:
            return self.override
        if '扣款' in request['input']:
            assert request['instructions'].startswith('只依原文抽取')
            return response(SUPPORT)
        if '匯出' in request['input']:
            return response({'category': '操作疑問', 'urgency': 'low', 'summary': '詢問匯出報表方法', 'needs_reply': True})
        if '深色' in request['input']:
            return response({'category': '其他', 'urgency': 'low', 'summary': '建議增加深色模式', 'needs_reply': False})
        assert request['input'].startswith('下週三')
        return response(EVENT)

    def parse(self, **request):
        self.calls.append(request)
        assert request['store'] is False and isinstance(request['text_format'], type)
        if self.override is not None:
            return self.override
        model = request['text_format']
        data = REVIEW if model.__name__=='ReviewInsight' else ORDER
        return response(data, parsed=model.model_validate(data))


def cells_of(notebook):
    return {c['id'].removeprefix('w06s-'): c for c in notebook['cells'] if c['cell_type']=='code'}


def prepare(cells, key, ns=None):
    """只執行宣告的依賴；新namespace證明單元沒有偷讀前節變數。"""
    if ns is None:
        ns = {}
    done = set()

    def visit(k):
        if k in done:
            return
        for dep in cells[k]['metadata']['teaching']['needs']:
            visit(dep)
        run(cells[k], ns)
        done.add(k)

    visit(key)
    return ns


def check():
    fake_module = ModuleType('openai')
    fake_module.__version__ = 'offline-test'
    constructors = []

    def fake_openai(**kwargs):
        constructors.append(kwargs)
        assert kwargs == {'max_retries': 0, 'timeout': 60.0}
        return SimpleNamespace(responses=FakeResponses())

    fake_module.OpenAI = fake_openai
    reports = []
    with patch.dict(sys.modules, {'openai': fake_module, 'google.colab': None}), patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
        pairs = []
        for teacher in (False, True):
            role = '教師版' if teacher else '學生版'
            path = ROOT/'week06'/f'{builder.STEM}_{role}.ipynb'
            nb = json.loads(path.read_text(encoding='utf-8'))
            assert nb==builder.build(teacher), '檔案與重建來源不同'
            assert len({c['id'] for c in nb['cells']})==len(nb['cells'])
            assert len(nb['cells'])==90
            for cell in nb['cells']:
                if cell['cell_type']=='markdown':
                    source = ''.join(cell['source'])
                    headings = list(re.finditer(r'^#{1,6} .+$', source, re.MULTILINE))
                    assert len(headings)<=1, (cell['id'], '同格有多個標題')
                    if headings:
                        assert headings[0].start()==0, (cell['id'], '標題前仍混有上一節文字')
            codes = cells_of(nb)
            assert len(codes)==26
            # N1應留在JSON Schema事件單元，Pydantic區不再切回作業Schema。
            ids = [c['id'] for c in nb['cells']]
            assert ids.index('w06s-event-schema') < ids.index('w06s-array') < ids.index('w06s-api-guide')
            assert ids.index('w06s-array') < ids.index('w06s-pydantic-guide')
            assert 'assignment_schema' not in json.dumps(nb, ensure_ascii=False)
            n1 = prepare(codes, 'array')
            event_items = n1['event_list_schema']['properties']['events']['items']
            assert event_items['required']==['title', 'owner']
            assert event_items['properties']['owner']['type']==['string','null']
            assert len(n1['event_list_data']['events'])==2
            assert n1['event_list_data']['events'][0]['owner'] is None
            assert ids.index('w06s-pydantic-bad') < ids.index('w06s-event-list-model') < ids.index('w06s-b-guide')
            n2 = prepare(codes, 'event-list-model')
            assert codes['event-list-model']['metadata']['teaching']=={'needs': [], 'api_requests': 0}
            assert n2['event_list_data']==n1['event_list_data']
            assert n2['event_list'].model_dump()==n1['event_list_data']
            assert isinstance(n2['event_list'],n2['EventList'])
            assert all(isinstance(item,n2['EventItem']) for item in n2['event_list'].events)
            assert n2['event_list'].events[0].owner is None
            assert n2['EventList'].model_validate({'events': []}).events==[]
            for bad in [{'events': [{'title': '活動'}]},
                        {'events': [{'title': '活動', 'owner': 123}]},
                        {'events': [{'title': '活動', 'owner': None, 'extra': '多欄'}]}]:
                try:
                    n2['EventList'].model_validate(bad)
                except ValueError:
                    pass
                else:
                    raise AssertionError('N2未擋下非法活動資料')
            ns = {}
            for cell in codes.values():
                assert cell['outputs']==[] and cell['execution_count'] is None
                source = ''.join(cell['source'])
                assert '\ufffd' not in source and '???' not in source
                if '%pip' not in source:
                    tree = ast.parse(source)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target,ast.Name) and target.id.startswith('RUN_'):
                                    assert isinstance(node.value,ast.Constant) and node.value.value is False
                    run(cell,ns)
                prepare(codes, cell['id'].removeprefix('w06s-'))
            markdown = path.with_suffix('.md').read_text(encoding='utf-8')
            blocks = __import__('re').findall(r'```python\n(.*?)```', markdown, __import__('re').S)
            assert blocks==[''.join(c['source']) for c in codes.values()]
            assert markdown.count('```')==52
            pairs.append(nb)
            reports.append(f'{role}：90格／64文字格／26程式格；標題分格、25格AST、清空輸出、預設關閉、無金鑰順序與25格依宣告獨立執行、Markdown對齊通過；N2與N1相同資料的物件／dump／正負例通過（安裝格未執行）。')
        assert not constructors, '無金鑰不應建立client'
        assert [c['id'] for c in pairs[0]['cells']]==[c['id'] for c in pairs[1]['cells']]
        changed=[a['id'] for a,b in zip(pairs[0]['cells'],pairs[1]['cells']) if a['cell_type']=='code' and a['source']!=b['source']]
        assert changed==['w06s-g','w06s-a-schema','w06s-a-validator','w06s-b-model','w06s-c-model']

        tc, sc = cells_of(pairs[1]), cells_of(pairs[0])
        local = [('g','RUN_G'), ('a-local','RUN_A_LOCAL'), ('b-model','RUN_B_LOCAL'), ('c-model','RUN_C_LOCAL')]
        for key,flag in local:
            ns = prepare(tc,key)
            run(tc[key],ns,**{flag:True})
        reports.append('教師G六欄、A合法／缺欄／過長／型別／多欄／合法錯分類、B評分負例、C金額與數量負例通過。')

        # 實測邊界：不是只檢查實作文字，合法與非法資料都經過正式validator。
        ns = prepare(tc,'a-validator'); validator=ns['validate_support_data']
        for value in [None, [], {}, dict(SUPPORT, category='付款'),dict(SUPPORT, urgency='urgent'),
                      dict(SUPPORT, summary=''),dict(SUPPORT, summary=' '),dict(SUPPORT, summary=123),
                      dict(SUPPORT, needs_reply=1),dict(SUPPORT, summary='字'*31)]:
            assert validator(value)
        assert validator(dict(SUPPORT,summary='字'*30))==[]
        assert validator(dict(SUPPORT,category='其他'))==[]

        activities = [('event-plain','RUN_EVENT_PLAIN','plain_result',1),
                      ('event-strict','RUN_EVENT_STRICT','strict_result',1),
                      ('a-single','RUN_A_SINGLE','support_result',1),
                      ('a-batch','RUN_A_BATCH','support_rows',3),
                      ('b-live','RUN_B_REVIEW','review_result',1),
                      ('c-live','RUN_C_ORDER','order_result',1)]
        for key,flag,result,number in activities:
            ns=prepare(tc,key); fake=FakeResponses(); ns['client']=SimpleNamespace(responses=fake)
            run(tc[key],ns,**{flag:True})
            assert len(fake.calls)==number and ns[result] is not None,(key,ns.get(result))
            if key=='event-plain': assert 'text' not in fake.calls[0]
            elif key=='event-strict': assert fake.calls[0]['text']['format']['schema']==ns['event_schema']
            elif key.startswith('a-'):
                assert fake.calls[0]['instructions']==ns['support_rules']
                assert fake.calls[0]['text']['format']['schema']==ns['support_schema']
                if key=='a-batch': assert all(row['matches'] for row in ns['support_rows'])
            # 上次成功後再失敗，不能繼續顯示上次採用的資料。
            failures = [response(status='incomplete'),response(status='failed'),response(refusal='固定拒答'),
                        response(text=' ')]
            if key in ['event-plain','event-strict','a-single','a-batch']:
                failures += [response(text='不是JSON'),response(text='[]'),response({})]
            else:
                failures += [response(parsed=None),response(parsed=object())]
            for failure in failures:
                failed_fake=FakeResponses(failure); ns['client']=SimpleNamespace(responses=failed_fake)
                run(tc[key],ns,**{flag:True})
                if result=='support_rows':
                    assert len(ns[result])==3
                    assert all(row['result'] is None and row['error'] for row in ns[result])
                else:
                    assert ns[result] is None,(key,'失敗仍有結果')
        # 欄位不合法的JSON也要由正式A入口擋下。
        for bad in [dict(SUPPORT,summary='字'*31),dict(SUPPORT,needs_reply='true')]:
            ns=prepare(tc,'a-single'); ns['client']=SimpleNamespace(responses=FakeResponses(response(bad)))
            run(tc['a-single'],ns,RUN_A_SINGLE=True)
            assert ns['support_result'] is None and ns['support_error']
        reports.append('假API：P1/P2/A單筆/A三題/B/C共6種活動的1/1/1/3/1/1次請求、實際參數及成功→失敗不沿用舊資料通過。拒答／未完成／failed／空回應／解析／欄位／空物件等負例通過。')

        # 學生未完成練習時，付費入口必須在本機先停止。
        for key,flag,result,_ in activities[2:]:
            ns=prepare(sc,key); fake=FakeResponses(); ns['client']=SimpleNamespace(responses=fake)
            try:
                run(sc[key],ns,**{flag:True})
            except (RuntimeError,NotImplementedError):
                assert key=='a-batch'
            assert not fake.calls,(key,'未完成仍送出API')
        reports.append('學生TODO未完成時A/B/C付費入口皆0次假請求；不以None冒充完成。')
        with patch.dict(os.environ,{'OPENAI_API_KEY':'offline-placeholder'}):
            run(tc['setup'],{})
        assert len(constructors)==1
    for line in reports:
        print('PASS',line)
    print('範圍：僅靜態、本機Pydantic、假SDK與假回應；0次真實API，未測Colab或150分鐘試教。')


if __name__=='__main__':
    check()
