import tempfile
import unittest
from pathlib import Path

import repoexplain as rx


class RepoExplainTest(unittest.TestCase):
    def test_scan_and_pack(self):
        with tempfile.TemporaryDirectory() as d:
            files = {
                "README.md": "# Demo\n",
                "package.json": '{"main": "./src/start.js", "scripts": {"dev": "node src/start.js"}}',
                "src/start.js": "require('./store')\n",
                "src/store.py": "class User(models.Model):\n    name = 1\n",
                "node_modules/x/index.js": "junk",
                "logo.png": "\0\0",
                "big.js": "x" * (rx.MAX_FILE + 1),
            }
            for p, text in files.items():
                (Path(d) / p).parent.mkdir(parents=True, exist_ok=True)
                (Path(d) / p).write_text(text)
            (Path(d) / "leak.py").symlink_to("/etc/hosts")

            s = rx.scan(d)
            self.assertEqual(set(s["files"]), {"README.md", "package.json", "src/start.js", "src/store.py"})
            self.assertEqual(s["readme"], "README.md")
            self.assertEqual(s["manifests"], ["package.json"])
            self.assertEqual(s["entries"], ["src/start.js"])  # from package.json "main"
            self.assertEqual(s["scripts"], {"dev": "node src/start.js"})
            self.assertEqual(s["data"], ["src/store.py"])  # found by content, not path
            self.assertEqual(s["langs"], {"Python": 2, "JavaScript": 1})

            ctx, omitted = rx.pack(s, 300)
            self.assertLessEqual(len(ctx), 300 + 60)  # + the "left out" note
            self.assertGreater(omitted, 0)
            self.assertEqual(rx.pack(s, 100_000)[1], 0)

            # entry points normally come first; a question about users pulls store.py ahead
            plain = rx.pack(s, 100_000)[0]
            asked = rx.pack(s, 100_000, "Where is the User stored?")[0]
            self.assertLess(plain.index("### src/start.js"), plain.index("### src/store.py"))
            self.assertLess(asked.index("### src/store.py"), asked.index("### src/start.js"))

    def test_clone_url(self):
        gh = ("https://github.com/a/b.git", "a/b")
        self.assertEqual(rx.clone_url("a/b"), gh)
        self.assertEqual(rx.clone_url("https://github.com/a/b"), gh)
        self.assertEqual(rx.clone_url("https://github.com/a/b.git"), gh)
        self.assertEqual(rx.clone_url("https://github.com/a/b/tree/main/src"), gh)
        self.assertEqual(rx.clone_url("git@github.com:a/b.git"), gh)
        self.assertEqual(rx.clone_url("https://gitlab.com/x/y.git"), ("https://gitlab.com/x/y.git", "y"))


if __name__ == "__main__":
    unittest.main()
