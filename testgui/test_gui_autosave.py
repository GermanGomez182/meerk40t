import os
import shutil
import tempfile
import unittest
from collections.abc import Callable
from functools import partial
from pathlib import Path
from unittest.mock import patch

from meerk40t.core import core
from meerk40t.core.svg_io import SVGWriter
from meerk40t.device import dummydevice
from meerk40t.gui.wxmmain import Autosaver
from meerk40t.kernel import Kernel


class SavingElements:
    def __init__(self) -> None:
        self.calls = []
        self.payload = b"<svg>fixture workspace</svg>"
        self.failure = None
        self.result = True
        self.partial_write = False
        self.autosaver = None
        self.dirty_during_save = []

    def save(self, filename: str, temporary: bool = False) -> bool:
        self.calls.append((filename, temporary))
        self.dirty_during_save.append(self.autosaver.needs_saving)
        if self.failure is not None:
            if self.partial_write:
                Path(filename).write_bytes(b"<svg>incomplete")
            raise self.failure
        if self.result:
            Path(filename).write_bytes(self.payload)
        return self.result


class TestAutosave(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        # An absolute kernel name confines even its configuration directory to tmp.
        self.kernel = Kernel(self.directory.name, "0", "fixture", ignore_settings=True)
        self.context = self.kernel.root
        self.elements = SavingElements()
        self.context.elements = self.elements
        self.messages = []
        self.status_messages = []
        self.context.channel("console").watch(self.messages.append)
        self.kernel.listen("statusmsg", self.on_status)
        self.autosaver = Autosaver(self.context)
        self.elements.autosaver = self.autosaver
        self.path = Path(self.autosaver.autosave_file)
        self.assertEqual(self.path.parent, Path(self.directory.name).resolve())

    def on_status(self, origin: str, message: str) -> None:
        self.status_messages.append(str(message))

    def save_dirty_workspace(self) -> None:
        self.autosaver.set_saving_indicator(True)
        self.autosaver.autosave_workspace()
        self.kernel.process_queue()

    def test_ac_u10_1_failed_save_keeps_workspace_dirty(self) -> None:
        for error in (
            PermissionError("fixture permission denied"),
            OSError("fixture storage unavailable"),
            RuntimeError("fixture SVG writer failed"),
        ):
            with self.subTest(error=type(error).__name__):
                self.elements.failure = error
                self.save_dirty_workspace()
                self.assertTrue(self.autosaver.needs_saving)

    def test_ac_u10_1_save_failure_surfaces_actionable_error(self) -> None:
        self.elements.failure = OSError("fixture write blocked")
        self.save_dirty_workspace()
        messages = self.messages + self.status_messages
        self.assertTrue(messages, "Autosave failures must reach the user")
        text = " ".join(str(message) for message in messages).lower()
        self.assertIn("autosave", text)
        self.assertIn("fixture write blocked", text)

    def test_ac_u10_1_next_job_retries_failed_dirty_workspace(self) -> None:
        self.elements.failure = OSError("fixture write blocked")
        self.save_dirty_workspace()
        self.elements.failure = None
        self.autosaver.autosave_workspace()
        self.assertEqual(len(self.elements.calls), 2)
        self.assertEqual(self.path.read_bytes(), self.elements.payload)
        self.assertFalse(self.autosaver.needs_saving)

    def test_ac_u10_2_failed_replacement_preserves_original_recovery_file(self) -> None:
        previous = b"<svg>last recoverable fixture workspace</svg>"
        self.path.write_bytes(previous)
        self.elements.failure = OSError("fixture storage full")
        self.elements.partial_write = True
        self.save_dirty_workspace()
        self.assertTrue(self.path.exists(), "Startup recovery needs its original path")
        self.assertEqual(self.path.read_bytes(), previous)

    def test_ac_u10_2_failed_first_save_does_not_publish_partial_recovery(self) -> None:
        self.elements.failure = OSError("fixture storage full")
        self.elements.partial_write = True
        self.save_dirty_workspace()
        self.assertFalse(
            self.path.exists(), "An incomplete SVG must not become the recovery file"
        )

    def test_ac_u10_2_success_clears_dirty_only_after_complete_save(self) -> None:
        self.save_dirty_workspace()
        self.assertEqual(self.elements.dirty_during_save, [True])
        self.assertFalse(self.autosaver.needs_saving)
        self.assertEqual(self.path.read_bytes(), self.elements.payload)
        self.assertTrue(self.elements.calls[0][1])

    def test_ac_u10_3_disabled_or_clean_workspace_is_not_saved(self) -> None:
        previous = b"<svg>unchanged recovery</svg>"
        self.path.write_bytes(previous)
        for active, dirty in ((False, True), (False, False), (True, False)):
            with self.subTest(active=active, dirty=dirty):
                self.context.autosave_active = active
                self.autosaver.set_saving_indicator(dirty)
                self.autosaver.autosave_workspace()
                self.assertEqual(self.elements.calls, [])
                self.assertEqual(self.path.read_bytes(), previous)
                self.assertEqual(self.autosaver.needs_saving, dirty)

    def test_ac_u10_3_successful_history_keeps_only_six_prior_versions(self) -> None:
        payloads = [
            f"<svg>fixture revision {index}</svg>".encode("ascii")
            for index in range(12)
        ]
        for payload in payloads:
            self.elements.payload = payload
            self.save_dirty_workspace()
        self.assertEqual(self.path.read_bytes(), payloads[-1])
        self.assertEqual(self.path.with_suffix(".bak").read_bytes(), payloads[-2])
        for index in range(1, 6):
            self.assertEqual(
                self.path.with_suffix(f".ba{index}").read_bytes(),
                payloads[-index - 2],
            )
        self.assertFalse(self.path.with_suffix(".ba6").exists())
        self.assertEqual(len(list(Path(self.directory.name).glob("_autosave.*"))), 7)

    def test_ac_u10_1_false_save_result_is_visible_retryable_failure(self) -> None:
        previous = b"<svg>last recoverable fixture workspace</svg>"
        self.path.write_bytes(previous)
        self.elements.result = False
        self.save_dirty_workspace()
        self.assertTrue(self.autosaver.needs_saving)
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertIn(
            "autosave", " ".join(self.messages + self.status_messages).lower()
        )
        self.elements.result = True
        self.autosaver.autosave_workspace()
        self.assertEqual(len(self.elements.calls), 2)
        self.assertEqual(self.path.read_bytes(), self.elements.payload)
        self.assertFalse(self.autosaver.needs_saving)

    def test_ac_u10_2_failed_publication_preserves_recovery_and_retries(self) -> None:
        previous = b"<svg>last recoverable fixture workspace</svg>"
        self.path.write_bytes(previous)
        with patch(
            "meerk40t.gui.wxmmain.os.replace",
            side_effect=OSError("fixture publication blocked"),
        ):
            self.save_dirty_workspace()
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertTrue(self.autosaver.needs_saving)
        self.assertIn(
            "fixture publication blocked",
            " ".join(self.messages + self.status_messages),
        )
        self.autosaver.autosave_workspace()
        self.assertEqual(self.path.read_bytes(), self.elements.payload)
        self.assertFalse(self.autosaver.needs_saving)

    def test_ac_u10_2_history_failures_are_visible_and_retryable(self) -> None:
        previous = b"<svg>last recoverable fixture workspace</svg>"
        for suffix in (".bak", ".ba1"):
            with self.subTest(blocked_history=suffix):
                for entry in self.path.parent.iterdir():
                    if entry.is_file() and entry.name.startswith("_autosave"):
                        entry.unlink()
                self.path.write_bytes(previous)
                if suffix == ".ba1":
                    self.path.with_suffix(".bak").write_bytes(
                        b"older fixture workspace"
                    )
                blocked = self.path.with_suffix(suffix)
                self.messages.clear()
                self.status_messages.clear()

                def block_history(
                    operation: Callable,
                    source: str,
                    destination: str,
                    *args: object,
                    blocked_path: Path = blocked,
                    **kwargs: object,
                ) -> object:
                    if Path(destination) == blocked_path:
                        raise OSError("fixture history blocked")
                    return operation(source, destination, *args, **kwargs)

                with (
                    patch("os.rename", side_effect=partial(block_history, os.rename)),
                    patch("os.replace", side_effect=partial(block_history, os.replace)),
                    patch(
                        "shutil.copyfile",
                        side_effect=partial(block_history, shutil.copyfile),
                    ),
                ):
                    self.save_dirty_workspace()
                self.assertEqual(self.path.read_bytes(), previous)
                self.assertTrue(self.autosaver.needs_saving)
                messages = " ".join(self.messages + self.status_messages).lower()
                self.assertIn("autosave", messages)
                self.assertIn("fixture history blocked", messages)
                self.autosaver.autosave_workspace()
                self.assertEqual(self.path.read_bytes(), self.elements.payload)
                self.assertFalse(self.autosaver.needs_saving)


class TestAutosaveSVGIntegration(unittest.TestCase):
    def test_ac_u10_2_real_svg_writer_keeps_recovery_until_loadable_replacement(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            kernel = Kernel(directory, "0", "fixture", ignore_settings=True)
            kernel.add_plugin(core.plugin)
            kernel.add_plugin(dummydevice.plugin)
            kernel(partial=True)
            try:
                kernel.console("service device start dummy 0\n")
                elements = kernel.elements
                rectangle = elements.elem_branch.add(
                    type="elem rect", x=10, y=20, width=30, height=40
                )
                autosaver = Autosaver(kernel.root)
                path = Path(autosaver.autosave_file)
                self.assertEqual(path.parent, Path(directory).resolve())
                self.assertTrue(elements.save(str(path), temporary=True))
                previous = path.read_bytes()
                rectangle.x = 52
                rectangle.modified()
                observations = []
                original_save = SVGWriter.save

                def observe_save(context: object, filename: str, version: str) -> None:
                    observations.append(
                        (
                            Path(filename).suffix,
                            path.read_bytes() if path.exists() else None,
                            autosaver.needs_saving,
                        )
                    )
                    original_save(context, filename, version)

                with patch.object(SVGWriter, "save", side_effect=observe_save):
                    autosaver.set_saving_indicator(True)
                    autosaver.autosave_workspace()
                self.assertFalse(autosaver.needs_saving)
                elements.elem_branch.remove_all_children()
                self.assertTrue(elements.load(str(path)))
                recovered = list(elements.elems())
                self.assertEqual(len(recovered), 1)
                self.assertEqual(recovered[0].type, "elem rect")
                self.assertAlmostEqual(recovered[0].x, 52)
                self.assertAlmostEqual(recovered[0].width, 30)
                self.assertAlmostEqual(recovered[0].height, 40)
                self.assertEqual(observations, [(".svg", previous, True)])
            finally:
                kernel()
