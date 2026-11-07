#!/usr/bin/env python3
"""Behavioral tests; no model/API calls. Requires latexmk for compile tests."""
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import zipfile
from unittest.mock import patch
import studio as s


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve() / 'paper'
        s.initialize(self.root, demo=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_unicode_selection_and_stale_save(self):
        original = (self.root / 'main.tex').read_bytes()
        text = '中文😀 LaTeX 注释'
        s.save_file(self.root, 'main.tex', text, s.sha(original))
        item = s.annotation(self.root, {'kind':'source','file':'main.tex','revision':s.sha(text.encode()),'start':2,'end':4,'quote':'😀','instruction':'替换这个符号'})
        self.assertEqual(item['quote'], '😀')
        with self.assertRaises(s.StudioError) as error:
            s.save_file(self.root, 'main.tex', 'overwrite', s.sha(original))
        self.assertEqual(error.exception.status,409)
        self.assertEqual((self.root/'main.tex').read_text(),text)
        self.assertEqual(s.submit(self.root)['submitted'],1)
        self.assertEqual(len(s.pending(self.root)),1)
        s.resolve(self.root,[item['id']],'needs-info','请补充语义')
        self.assertEqual(s.pending(self.root),[])

    def test_zip_slip_rejected_before_any_write(self):
        archive=Path(self.tmp.name)/'bad.zip'
        with zipfile.ZipFile(archive,'w') as z:
            z.writestr('good.tex','good')
            z.writestr('../escape.tex','bad')
        with self.assertRaises(s.StudioError):
            s.import_template(self.root,archive)
        self.assertFalse((self.root/'good.tex').exists())
        self.assertFalse((self.root.parent/'escape.tex').exists())

    def test_project_escape_and_symlink(self):
        for name in ['../private.tex','/tmp/private.tex','.paper-studio/config.json']:
            with self.assertRaises(s.StudioError):s.safe_path(self.root,name)
        (self.root/'link.tex').symlink_to(self.root.parent/'private.tex')
        with self.assertRaises(s.StudioError):s.safe_path(self.root,'link.tex')

    def test_merge_conflict_preserves_user_and_template(self):
        candidate=self.root.parent/'candidate';candidate.mkdir()
        before, before_digest=s.manifest(self.root),s.digest(self.root)
        s.copy_sources(self.root,candidate)
        (candidate/'main.tex').write_text('candidate')
        (self.root/'main.tex').write_text('user edit')
        with self.assertRaises(s.StudioError):s.merge_candidate(self.root,candidate,before,before_digest)
        self.assertEqual((self.root/'main.tex').read_text(),'user edit')
        (candidate/'venue.sty').write_text('change margins')
        with self.assertRaises(s.StudioError):s.merge_candidate(self.root,candidate,s.manifest(self.root),s.digest(self.root))
        self.assertFalse((self.root/'venue.sty').exists())

    @unittest.skipUnless(shutil.which('latexmk'),'latexmk required')
    def test_real_compile_stale_pdf_and_export_recompile(self):
        first=s.compile_project(self.root)
        self.assertTrue(first['ok'],first['log'])
        self.assertTrue(Path(first['pdf']).read_bytes().startswith(b'%PDF'))
        a={'kind':'pdf','page':1,'quote':'Research','buildId':first['id'],'instruction':'Clarify'}
        s.annotation(self.root,a)
        (self.root/'main.tex').write_text((self.root/'main.tex').read_text()+'\n% edit\n')
        with self.assertRaises(s.StudioError):s.annotation(self.root,a)
        good=(self.root/'main.tex').read_text()
        (self.root/'main.tex').write_text('\\documentclass{does-not-exist}\n')
        failed=s.compile_project(self.root)
        self.assertFalse(failed['ok'])
        self.assertEqual(s.state(self.root)['compile']['id'],first['id'])
        (self.root/'main.tex').write_text(good)
        exported=s.export_zip(self.root)
        clean=self.root.parent/'clean';clean.mkdir()
        with zipfile.ZipFile(io.BytesIO(exported)) as z:
            self.assertIn('sections/introduction.tex',z.namelist())
            self.assertIn('OVERLEAF-IMPORT.md',z.namelist())
            self.assertNotIn('paper-context.md',z.namelist())
            self.assertFalse(any(n.startswith('.paper-studio') for n in z.namelist()))
            z.extractall(clean)
        s.configure(clean,'main.tex','pdflatex')
        result=s.compile_project(clean)
        self.assertTrue(result['ok'],result['log'])

    @unittest.skipUnless(shutil.which('latexmk'),'latexmk required')
    def test_settings_change_during_snapshot_does_not_publish_wrong_pdf(self):
        (self.root/'other.tex').write_text((self.root/'main.tex').read_text())
        started, finished=threading.Event(),threading.Event()
        original_config=s.config
        triggered=False
        def change_settings():
            started.wait(5)
            s.configure(self.root,'other.tex','pdflatex')
            finished.set()
        def read_config(root):
            nonlocal triggered
            current=original_config(root)
            if not triggered:
                triggered=True
                started.set()
                # The setter must block until the snapshot lock is released.
                finished.wait(.2)
            return current
        setter=threading.Thread(target=change_settings)
        setter.start()
        try:
            with patch.object(s,'config',side_effect=read_config):
                result=s.compile_project(self.root)
            self.assertTrue(finished.wait(5))
            self.assertFalse(result['ok'], 'Old compiler settings were published under the new configuration digest')
            self.assertIn('来源已改变',result['log'])
        finally:
            started.set();setter.join(5)

    @unittest.skipUnless(shutil.which('latexmk'),'latexmk required')
    def test_official_template_with_wrapper_directory(self):
        archive=Path(self.tmp.name)/'official.zip'
        with zipfile.ZipFile(archive,'w') as z:
            z.writestr('official/main.tex',r'\documentclass{article}\usepackage{localstyle}\begin{document}\input{content}\end{document}')
            z.writestr('official/localstyle.sty',r'\ProvidesPackage{localstyle}\newcommand{\greeting}{Nested template works.}')
            z.writestr('official/content.tex',r'\greeting')
        nested=self.root.parent/'nested'
        s.initialize(nested,template=archive,main='official/main.tex')
        compiled=s.compile_project(nested)
        self.assertTrue(compiled['ok'],compiled['log'])
        clean=self.root.parent/'nested-export';clean.mkdir()
        with zipfile.ZipFile(io.BytesIO(s.export_zip(nested))) as z:z.extractall(clean)
        s.configure(clean,'official/main.tex','pdflatex')
        compiled=s.compile_project(clean)
        self.assertTrue(compiled['ok'],compiled['log'])

    @unittest.skipUnless(shutil.which('latexmk'),'latexmk required')
    def test_auto_bridge_with_local_fake_agent(self):
        # Exercise the real subprocess/snapshot/compile/merge protocol without an LLM call.
        bin_dir=self.root.parent/'bin';bin_dir.mkdir()
        exe=bin_dir/'codex'
        exe.write_text('#!'+os.sys.executable+'\nfrom pathlib import Path\nimport json,sys\nsys.stdin.read()\np=Path("sections/introduction.tex")\np.write_text(p.read_text().replace("This editor supports", "This workspace supports"))\nPath(".paper-studio/agent-result.json").write_text(json.dumps({"status":"done","summary":"Clarified wording; no new claims."}))\n')
        exe.chmod(0o755)
        text=(self.root/'sections/introduction.tex').read_text()
        start=text.index('This editor')
        item=s.annotation(self.root,{'kind':'source','file':'sections/introduction.tex','revision':s.sha(text.encode()),'start':start,'end':start+11,'quote':'This editor','instruction':'Clarify wording'})
        s.submit(self.root)
        with patch.dict(os.environ,{'PATH':str(bin_dir)+os.pathsep+os.environ['PATH']}):
            s.agent_job(self.root,s.pending(self.root))
        result=next(a for a in s.state(self.root)['annotations'] if a['id']==item['id'])
        self.assertEqual(result['status'],'done',result)
        self.assertIn('This workspace supports',(self.root/'sections/introduction.tex').read_text())

    def test_http_auth_and_no_overwrite(self):
        app=s.Application(self.root,'manual')
        server=s.ThreadingHTTPServer(('127.0.0.1',0),s.make_handler(app))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(base+'/api/state')
            self.assertEqual(error.exception.code,403)
            request=urllib.request.Request(base+'/api/state',headers={'X-Studio-Token':app.token})
            with urllib.request.urlopen(request) as response:self.assertEqual(json.load(response)['agent'],'manual')
            request=urllib.request.Request(base+'/api/submit',data=b'{}',headers={'X-Studio-Token':app.token,'Origin':'https://attacker.invalid'})
            with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(request)
            self.assertEqual(error.exception.code,403)
        finally:
            server.shutdown();server.server_close()


if __name__=='__main__':unittest.main(verbosity=2)
