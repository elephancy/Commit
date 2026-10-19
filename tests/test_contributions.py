import base64
import contextlib
from datetime import date, datetime
import io
import shlex
import unittest
from unittest.mock import patch
import zlib

import main


class ContributionTests(unittest.TestCase):
    def test_shape_roundtrip_and_legacy_compressed_tokens(self):
        levels = main.empty_levels()
        levels[0][0], levels[6][52] = 1, 4
        token = main.encode_shape(levels)
        self.assertEqual(main.decode_shape(token), levels)
        raw = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
        compressed = base64.urlsafe_b64encode(zlib.compress(raw)).decode().rstrip("=")
        self.assertEqual(main.decode_shape(compressed), levels)

    def test_invalid_shapes_are_rejected(self):
        for text in ("0", "\n".join(["0" * 53] * 6), "\n".join(["5" * 53] * 7)):
            token = base64.urlsafe_b64encode(text.encode()).decode()
            with self.subTest(text=text[:10]), self.assertRaises(ValueError):
                main.decode_shape(token)

    def test_grid_starts_sunday_and_schedule_excludes_neighbor_year(self):
        self.assertEqual(main.sunday_on_or_before(date(2026, 1, 1)), date(2025, 12, 28))
        levels = main.empty_levels()
        levels[0][0] = 4  # December 28 belongs to the preceding year.
        levels[4][0] = 3  # January 1, 2026 is Thursday.
        self.assertEqual(main.compute_commit_schedule_from_levels(levels, 2026),
                         [datetime(2026, 1, 1, 12)] * 3)

    def test_export_orders_years_and_numbers_daily_commits(self):
        first, second = main.empty_levels(), main.empty_levels()
        first[4][0], second[5][0] = 2, 1
        command = main.build_git_command_from_shapes({2026: first, 2027: second}, [2027, 2026])
        lines = [line for line in command.splitlines() if line.startswith("GIT_AUTHOR_DATE=")]
        self.assertEqual(len(lines), 3)
        self.assertIn("2026-01-01 12:00:00 +0000", lines[0])
        self.assertIn("2026-01-01 #2", lines[1])
        self.assertIn("2027-01-01 #1", lines[2])
        self.assertNotIn("push", command)

    def test_empty_export_and_shell_quoting(self):
        self.assertTrue(main.build_git_command_from_shapes({2026: main.empty_levels()}, [2026]).startswith("# Draw"))
        for value in ("plain", "two words", "owner's name", "$(touch unsafe)", "line\nbreak"):
            self.assertEqual(shlex.split(main.shell_quote(value)), [value])

    def test_dry_run_does_not_checkout_create_commits_or_push(self):
        levels = main.empty_levels()
        levels[4][0] = 1
        arguments = ["main.py", "--shape", "2026:" + main.encode_shape(levels),
                     "--branch", "existing-work", "--dry-run"]
        with patch("sys.argv", arguments), patch("main.run") as run, contextlib.redirect_stdout(io.StringIO()):
            main.main()
        self.assertEqual([call.args[0] for call in run.call_args_list],
                         [["git", "rev-parse", "--is-inside-work-tree"]])


if __name__ == "__main__":
    unittest.main()
