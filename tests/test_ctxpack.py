import unittest
import os
import tempfile
import shutil
import json
from math import ceil


class TestWalkFiles(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.tmpdir)

    def _write(self, rel_path, content="hello"):
        full = os.path.join(self.tmpdir, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w') as f:
            f.write(content)

    def test_alphabetical_sorting(self):
        self._write('b.py')
        self._write('a.py')
        self._write('c.py')
        from ctxpack import walk_files
        results = walk_files(self.tmpdir)
        paths = [r['path'] for r in results]
        self.assertEqual(paths, sorted(paths))

    def test_directory_blocklisting(self):
        self._write('.git/config', 'repo')
        self._write('node_modules/pkg/index.js', 'code')
        self._write('__pycache__/main.cpython.py', 'code')
        self._write('real/file.py', 'ok')
        from ctxpack import walk_files
        results = walk_files(self.tmpdir)
        paths = [r['path'] for r in results]
        self.assertIn('real/file.py', paths)
        
        noise_dirs = [r for r in results if r['status'] == 'noise_dir']
        self.assertEqual(len(noise_dirs), 3)
        self.assertEqual({n['path'] for n in noise_dirs}, {
            '.git/config', 'node_modules/pkg/index.js', '__pycache__/main.cpython.py'
        })

    def test_utf8_text_classification(self):
        self._write('hello.txt', 'hello world')
        from ctxpack import walk_files
        results = walk_files(self.tmpdir)
        text_files = [r for r in results if r['status'] == 'text']
        self.assertEqual(len(text_files), 1)
        self.assertEqual(text_files[0]['content'], 'hello world')

    def test_binary_classification(self):
        full = os.path.join(self.tmpdir, 'data.bin')
        with open(full, 'wb') as f:
            f.write(b'\xff\xfe\x00\x01')
        from ctxpack import walk_files
        results = walk_files(self.tmpdir)
        binaries = [r for r in results if r['status'] == 'binary']
        self.assertEqual(len(binaries), 1)
        self.assertEqual(binaries[0]['path'], 'data.bin')

    def test_noise_extension_skipped(self):
        self._write('lib.min.js', 'minified')
        self._write('lib.min.css', 'styles')
        self._write('data.map', 'mapping')
        self._write('main.pyc')
        self._write('lib.so')
        from ctxpack import walk_files
        results = walk_files(self.tmpdir)
        noise = [r for r in results if r['status'] == 'noise_ext']
        self.assertEqual(len(noise), 5)

    def test_too_large_file(self):
        content = 'x' * (1_048_576 + 1)
        self._write('big.txt', content)
        from ctxpack import walk_files
        results = walk_files(self.tmpdir)
        large = [r for r in results if r['status'] == 'too_large']
        self.assertEqual(len(large), 1)

    def test_token_count_formula(self):
        content = 'hello world ' * 10
        expected = ceil(len(content) / 4)
        self._write('test.txt', content)
        from ctxpack import walk_files
        results = walk_files(self.tmpdir)
        self.assertEqual(results[0]['tokens'], expected)

    def test_gitignore_rules(self):
        self._write('.gitignore', "*.log\n/temp/\nignored_file.txt")
        self._write('app.log', 'logging')
        self._write('temp/app.py', 'code')
        self._write('ignored_file.txt', 'secret')
        self._write('valid.py', 'print(1)')
        
        from ctxpack import walk_files
        results = walk_files(self.tmpdir)
        
        ignored = [r for r in results if r['status'] == 'ignored']
        self.assertEqual(len(ignored), 3)
        ignored_paths = {r['path'] for r in ignored}
        self.assertEqual(ignored_paths, {'app.log', 'temp/app.py', 'ignored_file.txt'})
        
        valid = [r for r in results if r['status'] == 'text' and r['path'] != '.gitignore']
        self.assertEqual(len(valid), 1)
        self.assertEqual(valid[0]['path'], 'valid.py')


class TestRankFiles(unittest.TestCase):
    def test_non_text_gets_score_zero(self):
        from ctxpack import rank_files
        files = [
            {'path': 'a.txt', 'content': 'foo', 'tokens': 1, 'status': 'noise_ext', 'reason': 'x'},
        ]
        result = rank_files(files, 'foo')
        self.assertEqual(result[0]['score'], 0)

    def test_path_match_weighted_three_times(self):
        from ctxpack import rank_files
        files = [
            {'path': 'config.py', 'content': '', 'tokens': 1, 'status': 'text', 'reason': ''},
        ]
        result = rank_files(files, 'config')
        self.assertEqual(result[0]['score'], 3.0)

    def test_content_match_capped_at_ten(self):
        from ctxpack import rank_files
        many = 'hello ' * 100
        files = [
            {'path': 'f.txt', 'content': many, 'tokens': 1, 'status': 'text', 'reason': ''},
        ]
        result = rank_files(files, 'hello')
        self.assertEqual(result[0]['score'], 10.0)

    def test_depth_penalty(self):
        from ctxpack import rank_files
        files = [
            {'path': 'deep/dir/config.py', 'content': 'config', 'tokens': 1, 'status': 'text', 'reason': ''},
            {'path': 'config.py', 'content': 'config', 'tokens': 1, 'status': 'text', 'reason': ''},
        ]
        result = rank_files(files, 'config')
        self.assertGreater(result[0]['score'], result[1]['score'])

    def test_tie_broken_alphabetically(self):
        from ctxpack import rank_files
        files = [
            {'path': 'b.py', 'content': 'token', 'tokens': 1, 'status': 'text', 'reason': ''},
            {'path': 'a.py', 'content': 'token', 'tokens': 1, 'status': 'text', 'reason': ''},
        ]
        result = rank_files(files, 'token')
        self.assertEqual(result[0]['path'], 'a.py')
        self.assertEqual(result[1]['path'], 'b.py')

    def test_token_short_words_skipped(self):
        from ctxpack import rank_files
        files = [
            {'path': 'a.py', 'content': 'a an', 'tokens': 1, 'status': 'text', 'reason': ''},
        ]
        result = rank_files(files, 'a an')
        self.assertEqual(result[0]['score'], 0)


class TestTruncation(unittest.TestCase):
    def test_empty_content_on_zero_budget(self):
        from ctxpack import truncate_file_content
        self.assertEqual(truncate_file_content('hello\nworld', 0), "")

    def test_small_budget_truncates(self):
        from ctxpack import truncate_file_content
        content = '\n'.join(f'line{i}' for i in range(200))
        result = truncate_file_content(content, 80)
        self.assertIn('[TRUNCATED]', result)

    def test_large_budget_keeps_all(self):
        from ctxpack import truncate_file_content
        content = '\n'.join(f'line{i}' for i in range(5))
        result = truncate_file_content(content, 1000)
        self.assertNotIn('[TRUNCATED]', result)
        lines = result.split('\n')
        self.assertEqual(len(lines), 5)

    def test_margin_respected(self):
        from ctxpack import truncate_file_content
        content = '\n'.join(f'line{i}' for i in range(100))
        result = truncate_file_content(content, 49)
        self.assertEqual(result, "")


class TestDirectoryTree(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.tmpdir)

    def _write(self, rel_path, content=""):
        full = os.path.join(self.tmpdir, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w') as f:
            f.write(content)

    def test_tree_includes_files_and_dirs(self):
        self._write('a.py')
        self._write('sub/b.py')
        from ctxpack import generate_tree
        tree = generate_tree(self.tmpdir)
        self.assertIn('a.py', tree)
        self.assertIn('sub', tree)
        self.assertIn('b.py', tree)

    def test_tree_excludes_noise_dirs(self):
        self._write('.git/HEAD')
        self._write('node_modules/pkg/index.js')
        self._write('real/file.py')
        from ctxpack import generate_tree
        tree = generate_tree(self.tmpdir)
        self.assertNotIn('.git', tree)
        self.assertNotIn('node_modules', tree)
        self.assertIn('real', tree)
        self.assertIn('file.py', tree)


class TestAssembleBundle(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.tmpdir)

    def test_budget_enforced(self):
        os.chdir(self.tmpdir)
        from ctxpack import assemble_bundle
        files = [
            {'path': 'big.txt', 'content': 'x' * 10000, 'tokens': 2500, 'status': 'text', 'reason': '', 'score': 10},
        ]
        bundle, included, excluded = assemble_bundle(files, 100, self.tmpdir)
        total_tokens = ceil(len(bundle) / 4)
        self.assertLessEqual(total_tokens, 100)

    def test_non_text_files_excluded(self):
        os.chdir(self.tmpdir)
        from ctxpack import assemble_bundle
        files = [
            {'path': 'a.txt', 'content': None, 'tokens': 0, 'status': 'noise_ext', 'reason': 'x', 'score': 0},
        ]
        bundle, included, excluded = assemble_bundle(files, 1000, self.tmpdir)
        self.assertEqual(len(included), 0)
        self.assertEqual(len(excluded), 1)


class TestManifest(unittest.TestCase):
    def test_structure(self):
        from ctxpack import build_manifest
        manifest = build_manifest(
            budget=1000,
            bundle="hello world",
            included=[{'path': 'a.py', 'tokens': 5, 'score': 3.0}],
            excluded=[{'path': 'b.py', 'status': 'noise_ext', 'reason': 'x'}]
        )
        self.assertEqual(manifest['budget'], 1000)
        self.assertEqual(manifest['used'], ceil(len("hello world") / 4))
        self.assertEqual(len(manifest['included']), 1)
        self.assertEqual(len(manifest['excluded']), 1)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.tmpdir)

    def _write(self, rel_path, content="content"):
        full = os.path.join(self.tmpdir, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w') as f:
            f.write(content)

    def test_deterministic_output(self):
        self._write('a.py', 'def a(): pass')
        self._write('src/b.py', 'def b(): pass')
        self._write('readme.md', '# project')
        from ctxpack import walk_files, rank_files, assemble_bundle, build_manifest
        files = walk_files(self.tmpdir)
        ranked = rank_files(files, 'python')
        bundle1, inc1, exc1 = assemble_bundle(ranked, 500, self.tmpdir)
        m1 = build_manifest(500, bundle1, inc1, exc1)
        m1_json = json.dumps(m1, sort_keys=True)

        for _ in range(3):
            files2 = walk_files(self.tmpdir)
            ranked2 = rank_files(files2, 'python')
            bundle2, inc2, exc2 = assemble_bundle(ranked2, 500, self.tmpdir)
            m2 = build_manifest(500, bundle2, inc2, exc2)
            m2_json = json.dumps(m2, sort_keys=True)
            self.assertEqual(m1_json, m2_json)
            self.assertEqual(bundle1, bundle2)

    def test_full_pipeline_exit_code_zero(self):
        self._write('hello.py', 'print(1)')
        import subprocess
        ctxpack_path = os.path.join(os.path.dirname(__file__), '..', 'ctxpack.py')
        result = subprocess.run(
            ['python', ctxpack_path, '--path', self.tmpdir, '--task', 'test', '--budget', '500'],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)


if __name__ == '__main__':
    unittest.main()
