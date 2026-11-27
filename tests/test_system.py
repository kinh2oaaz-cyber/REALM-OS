"""System info tests."""

from __future__ import annotations

import unittest

from system.info import list_processes, os_description, python_version, system_info


class TestSystem(unittest.TestCase):
    def test_system_info_keys(self) -> None:
        info = system_info()
        for key in ("os", "python", "cpu_count_logical", "memory_total"):
            self.assertIn(key, info)

    def test_list_processes(self) -> None:
        procs = list_processes(limit=5)
        self.assertLessEqual(len(procs), 5)
        if procs:
            self.assertIn("pid", procs[0])
            self.assertIn("name", procs[0])

    def test_strings(self) -> None:
        self.assertIsInstance(os_description(), str)
        self.assertIsInstance(python_version(), str)


if __name__ == "__main__":
    unittest.main()
