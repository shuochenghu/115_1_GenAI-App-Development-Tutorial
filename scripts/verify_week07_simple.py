"""簡化版靜態與AppTest驗證；所有模型呼叫都由假SDK攔截，不啟動伺服器。"""
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
import ast
import contextlib
import copy
import importlib.util
import io
import json
import logging
import os
import re
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('w07builder',ROOT/'scripts/build_week07_simple.py')
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

EVENT={'title':'AI專題討論','date':'下週三','time':'14:00','location':'A203','owner':None}


def reply(mode='ok', structured=False):
    content=[]
    if mode=='refusal':content=[SimpleNamespace(type='refusal',refusal='固定拒答')]
    text=json.dumps(EVENT,ensure_ascii=False) if structured else '假SDK固定回答'
    if mode=='empty':text=' '
    elif mode=='not-json':text='不是JSON'
    elif mode=='missing':text='{"title":"缺欄"}'
    return SimpleNamespace(output=[SimpleNamespace(type='message',content=content)],output_text=text,
                           status='incomplete' if mode=='incomplete' else 'completed')


class FakeStream:
    def __init__(self,events):
        self.events=events;self.closed=False

    def __enter__(self):return self
    def __iter__(self):return iter(self.events)
    def __exit__(self,*args):self.closed=True


class FakeResponses:
    def __init__(self):self.calls=[];self.mode='ok';self.streams=[]

    def create(self,**request):
        self.calls.append(copy.deepcopy(request))
        assert request['store'] is False
        assert request['input']
        if request.get('stream'):
            events=[]
            if self.mode!='empty':events.append(SimpleNamespace(type='response.output_text.delta',delta='假串流回答'))
            if self.mode=='refusal':events.append(SimpleNamespace(type='response.refusal.delta'))
            elif self.mode=='incomplete':events.append(SimpleNamespace(type='response.incomplete'))
            elif self.mode!='missing-completed':events.append(SimpleNamespace(type='response.completed',response=reply()))
            stream=FakeStream(events);self.streams.append(stream);return stream
        if 'text' in request:
            fmt=request['text']['format']
            assert fmt['type']=='json_schema' and fmt['strict'] is True
            assert set(fmt['schema']['required'])==set(EVENT)
            assert fmt['schema']['additionalProperties'] is False
        return reply(self.mode,'text' in request)


def assert_clean(app):
    assert not app.exception,[x.message for x in app.exception]


def check():
    logging.getLogger('streamlit').setLevel(logging.ERROR)
    logging.getLogger('streamlit.runtime.scriptrunner_utils.script_run_context').disabled=True
    # AppTest模組會建立暫存目錄；使用本配套可寫且忽略的測試目錄。
    test_temp=builder.APP/'.apptest-temp'
    test_temp.mkdir(exist_ok=True)
    previous_temp=tempfile.tempdir
    tempfile.tempdir=str(test_temp.resolve())
    from streamlit.testing.v1 import AppTest
    tempfile.tempdir=previous_temp
    reports=[]
    books=[]
    for teacher in (False,True):
        role='教師版' if teacher else '學生版'
        folder='teacher' if teacher else 'student'
        path=builder.WEEK/f'{builder.STEM}_{role}.ipynb'
        book=json.loads(path.read_text(encoding='utf-8'))
        assert book==builder.notebook(teacher)
        assert len({c['id'] for c in book['cells']})==len(book['cells'])
        assert len(book['cells'])==40
        blocks=[]
        for c in book['cells']:
            source=''.join(c['source'])
            assert '\ufffd' not in source and '???' not in source
            if c['cell_type']=='code':
                ast.parse(source)
                assert c['outputs']==[] and c['execution_count'] is None
                filename=c['metadata']['teaching']['file']
                assert source==(builder.APP/folder/filename).read_text(encoding='utf-8')
                blocks.append(source)
                # 不允許範例彼此匯入，也不依賴教師檢查模組。
                for node in ast.walk(ast.parse(source)):
                    if isinstance(node,ast.ImportFrom):
                        assert node.module in ['dotenv','openai']
            else:
                # 文字格的命令圍欄不視為標題。
                plain=re.sub(r'```.*?```','',source,flags=re.S)
                headings=list(re.finditer(r'^#{1,6} .+$',plain,re.M))
                assert len(headings)<=1
                if headings:assert headings[0].start()==0
        md=path.with_suffix('.md').read_text(encoding='utf-8')
        assert re.findall(r'```python\n(.*?)```',md,re.S)==blocks
        for link in re.findall(r'\]\(([^)]+)\)',md):
            if not link.startswith(('http','#')):assert (path.parent/link).exists(),link
        books.append(book)
        reports.append(f'{role}：40格／7個完整App，JSON／ID／標題分格／AST／輸出清空／來源與Markdown對齊通過。')
    assert [c['id'] for c in books[0]['cells']]==[c['id'] for c in books[1]['cells']]
    # 檔頭啟動路徑與教師提醒可不同；真正的練習答案只允許A／B／C三格不同。
    diff=[a['id'] for a,b in zip(books[0]['cells'],books[1]['cells'])
          if a['cell_type']=='code' and ast.dump(ast.parse(''.join(a['source'])))!=ast.dump(ast.parse(''.join(b['source'])))]
    assert diff==['w07s-01','w07s-02','w07s-03']
    responses=FakeResponses()
    fake=ModuleType('openai')

    def client(**options):
        assert options=={'api_key':'offline-placeholder','max_retries':0,'timeout':60.0}
        return SimpleNamespace(responses=responses)

    fake.OpenAI=client

    def app(name,folder='teacher'):
        result=AppTest.from_file(str(builder.APP/folder/name),default_timeout=10).run()
        assert_clean(result)
        return result

    # 所有測試都替換SDK與.env讀取；不會使用真實金鑰。
    with patch.dict(sys.modules,{'openai':fake}), patch('dotenv.load_dotenv',return_value=False), \
         patch.dict(os.environ,{'OPENAI_API_KEY':'offline-placeholder','OPENAI_MODEL':'offline-test'}), \
         contextlib.redirect_stdout(io.StringIO()):
        for folder in ['teacher','student']:
            for filename in builder.app_sources(folder=='teacher'):
                sample=app(filename,folder)
                assert all(c.value is False for c in sample.checkbox)
        assert not responses.calls,'初次開啟竟然請求API'
        a=app('01_inputs.py');a.text_input[0].set_value('小安').run();a.button[0].click().run()
        assert_clean(a);assert any('小安' in m.value for m in a.markdown)
        b=app('02_state.py');b.button[0].click().run();b.button[0].click().run()
        assert b.session_state.count==2
        b.button[1].click().run();assert b.session_state.count==0
        student=app('02_state.py','student');student.button[0].click().run();student.button[1].click().run()
        assert student.session_state.count==1,'學生歸零TODO不應已代填'

        c=app('03_form_ai.py');c.button[0].click().run();assert_clean(c)
        assert c.session_state.event_record['data']==EVENT and '離線' in c.session_state.event_record['mode']
        c.text_area[0].set_value('不同的活動原文').run()
        assert c.session_state.event_record['input']!='不同的活動原文','未送出就改寫結果'
        assert not responses.calls
        c.checkbox[0].check().run();assert not responses.calls,'只改模式不該請求'
        c.button[0].click().run();assert_clean(c)
        assert len(responses.calls)==1 and c.session_state.event_record['data']==EVENT
        assert responses.calls[-1]['input']=='不同的活動原文'
        for mode in ['incomplete','refusal','empty','not-json','missing']:
            responses.mode=mode;c.button[0].click().run();assert_clean(c)
            assert c.session_state.event_record is None and c.error
        responses.mode='ok';before=len(responses.calls)
        c.text_area[0].set_value(' ').run();c.button[0].click().run()
        assert len(responses.calls)==before and c.warning

        for filename in ['04_chat.py','05_streaming.py']:
            d=app(filename);before=len(responses.calls)
            d.chat_input[0].set_value('離線第一題').run();assert_clean(d)
            d.chat_input[0].set_value('離線第二題').run();assert_clean(d)
            assert len(d.session_state.messages)==4 and len(responses.calls)==before
            d.checkbox[0].check().run();assert d.session_state.messages==[]
            d.chat_input[0].set_value('真實路徑第一題').run();assert_clean(d)
            assert len(d.session_state.messages)==2 and len(responses.calls)==before+1
            d.chat_input[0].set_value('真實路徑第二題').run();assert_clean(d)
            assert len(responses.calls[-1]['input'])==3
            assert responses.calls[-1]['input'][0]['content']=='真實路徑第一題'
            assert len(d.session_state.messages)==4
            failures=['incomplete','refusal','empty']
            if filename=='05_streaming.py':failures.append('missing-completed')
            for mode in failures:
                responses.mode=mode;old=copy.deepcopy(d.session_state.messages)
                d.chat_input[0].set_value('這輪應失敗').run();assert_clean(d)
                assert d.session_state.messages==old and d.error,(filename,mode)
            responses.mode='ok'
            # 超過五輪時僅帶最近十則訊息；畫面仍保留已完成紀錄。
            d.session_state.messages=[{'role':r,'content':str(i)} for i in range(6) for r in ['user','assistant']]
            d.chat_input[0].set_value('測五輪視窗').run();assert_clean(d)
            assert len(responses.calls[-1]['input'])==11
            assert responses.calls[-1]['input'][0]['content']=='1'
            d.button[0].click().run();assert d.session_state.messages==[]
        assert responses.streams and all(s.closed for s in responses.streams)

        # AppTest無真人檔案選擇操作；用替代上傳物件驗證解碼與處理分支。
        holder={'bytes':'虛構活動文字。'.encode('utf-8')}

        def uploaded(*args,**kwargs):
            data=holder['bytes']
            return SimpleNamespace(name='test.txt',size=len(data),getvalue=lambda:data)

        with patch('streamlit.file_uploader',side_effect=uploaded):
            f=app('06_file.py');f.button[0].click().run();assert_clean(f)
            assert '離線' in f.session_state.file_record['mode']
            f.checkbox[0].check().run();f.button[0].click().run();assert_clean(f)
            assert f.session_state.file_record['answer']=='假SDK固定回答'
            responses.mode='incomplete';f.button[0].click().run();assert f.session_state.file_record is None and f.error
            responses.mode='ok'
            for bad in [b'\xff',b'',b'x'*65537,('字'*6001).encode('utf-8')]:
                before=len(responses.calls);holder['bytes']=bad;f.run();assert_clean(f)
                assert f.button[0].disabled and f.error
                assert len(responses.calls)==before and f.session_state.file_record is None
        g=app('07_layout.py');g.selectbox[0].set_value('精簡').run();assert_clean(g)
        assert len(g.tabs)==2 and not any('A203' in m.value for m in g.markdown)
        # 缺金鑰不能送出；不在輸出顯示SDK請求或敏感細節。
        with patch.dict(os.environ,{'OPENAI_API_KEY':''}):
            c=app('03_form_ai.py');c.checkbox[0].check().run();before=len(responses.calls)
            c.button[0].click().run();assert_clean(c)
            assert c.error and c.session_state.event_record is None and len(responses.calls)==before
    for item in reports:print('PASS',item)
    print('PASS 14份App預設離線0請求、輸入／歸零／表單保留、兩輪聊天／五輪視窗／清空、模式隔離、串流完成／失敗不保存與關閉連線。')
    print('PASS 假API格式／history／store=False／重試與timeout、拒答／未完成／空回應／解析與欄位失敗、缺金鑰與空輸入0請求。')
    print('PASS 替代上傳物件測試UTF-8／空檔／超大小／超字數、離線預覽與假摘要；非真人瀏覽器上傳驗證。')
    print('範圍：AppTest與假SDK，0次真實模型API；未啟動伺服器，未做瀏覽器、其他平台安裝、部署或試教。')


if __name__=='__main__':
    check()
