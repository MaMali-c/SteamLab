"""Dependency-free tests of launcher behavior; no scientific mocks."""
import importlib.util
import errno
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dev", ROOT / "scripts" / "dev.py")
dev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dev)


class LauncherTests(unittest.TestCase):
    def test_occupied_preferred_port_chooses_another(self):
        with socket.socket() as listener:
            try:
                listener.bind(("127.0.0.1", 0))
            except PermissionError:
                self.skipTest("This execution environment forbids binding localhost ports")
            listener.listen()
            occupied = listener.getsockname()[1]
            self.assertNotEqual(dev.select_port(occupied), occupied)

    def test_available_port_is_retained(self):
        try:
            port = dev.select_port(0)
        except PermissionError:
            self.skipTest("This execution environment forbids binding localhost ports")
        self.assertEqual(dev.select_port(port), port)

    def test_port_fallback_logic(self):
        sock = Mock()
        sock.bind.side_effect = [OSError(errno.EADDRINUSE, "Address in use"), None]
        sock.getsockname.return_value = ("127.0.0.1", 60001)
        with patch.object(dev.socket, "socket") as factory:
            factory.return_value.__enter__.return_value = sock
            self.assertEqual(dev.select_port(5173), 60001)
        self.assertEqual(sock.bind.call_args_list[0].args, (("127.0.0.1", 5173),))
        self.assertEqual(sock.bind.call_args_list[1].args, (("127.0.0.1", 0),))

    def test_port_permission_error_is_not_hidden(self):
        sock = Mock()
        sock.bind.side_effect = PermissionError(errno.EPERM, "Operation not permitted")
        with patch.object(dev.socket, "socket") as factory:
            factory.return_value.__enter__.return_value = sock
            with self.assertRaises(PermissionError):
                dev.select_port(5173)

    def test_readiness_stops_if_child_exits(self):
        child = Mock()
        child.poll.return_value = 1
        with self.assertRaisesRegex(RuntimeError, "exited before readiness"):
            dev.wait_ready("http://127.0.0.1:1", child, lambda body: True)

    def test_shutdown_only_terminates_owned_process_group(self):
        child = Mock(pid=123456)
        child.poll.return_value = None
        with patch.object(dev.os, "killpg") as kill:
            dev.stop(child)
        kill.assert_called_once_with(123456, dev.signal.SIGTERM)
        child.wait.assert_called_once_with(timeout=5)

    def test_shell_launcher_syntax(self):
        subprocess.run(["bash", "-n", str(ROOT / "start.command")], check=True)

    def test_python_sources_compile(self):
        for path in ROOT.rglob("*.py"):
            if ".venv" not in path.parts:
                compile(path.read_text(), str(path), "exec")


if __name__ == "__main__":
    unittest.main()
