import unittest
from types import SimpleNamespace

import wx

from meerk40t.kernel import Service
from testgui.test_gui_k40workspace import descendants, make_context


class HardwareCalls:
    def __init__(self) -> None:
        self.calls = []

    def forbidden_operation(self, *args: object, **kwargs: object) -> None:
        self.calls.append((args, kwargs))

    open = forbidden_operation
    connect = forbidden_operation
    update_status = forbidden_operation
    get_status = forbidden_operation
    query = forbidden_operation
    send = forbidden_operation
    write = forbidden_operation


class USBConnection(HardwareCalls):
    def __init__(self, connected: bool) -> None:
        super().__init__()
        self.connected = connected
        self.local_reads = 0

    def is_connected(self) -> bool:
        self.local_reads += 1
        return self.connected


class SoftwareController(HardwareCalls):
    def __init__(self, connection: object = None) -> None:
        super().__init__()
        self.connection = connection
        self.state = "unknown"
        self.connection_errors = 0


class InaccessibleController(HardwareCalls):
    connection = None
    connection_errors = 0

    @property
    def state(self) -> str:
        raise OSError("fixture status inaccessible")


class TCPTransport(HardwareCalls):
    def __init__(self) -> None:
        super().__init__()
        self._stream = object()


class TestK40Connection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.owns_app = wx.App.Get() is None
        cls.app = wx.App.Get() or wx.App(False)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.owns_app:
            cls.app.Destroy()

    def setUp(self) -> None:
        self.context = make_context("LihuiyuDevice")
        self.parent = wx.Frame(None)
        self.context.gui = self.parent
        self.context.elements = SimpleNamespace(
            ops=lambda: iter(()), elems=lambda: iter(())
        )
        self.device = self.context.device
        self.device.mock = False
        self.device.networked = False
        self.device.controller = SoftwareController()
        self.device.driver = SimpleNamespace(paused=False)
        self.device.tcp = TCPTransport()
        self.queue = []
        self.device.spooler = SimpleNamespace(queue=self.queue)
        self.commands = []
        self.context.kernel.console = self.commands.append
        self.windows = []

    def tearDown(self) -> None:
        for window in self.windows:
            window.Destroy()
        self.context.opened.clear()
        self.parent.Destroy()
        self.app.ProcessPendingEvents()

    def make_window(self) -> wx.Window:
        registered = self.context.lookup("window/K40Workspace")
        self.assertIsNotNone(registered)
        window = registered(self.context, "window/K40Workspace", self.parent)
        self.windows.append(window)
        window.panel.refresh_data()
        return window

    def text(self, window: wx.Window) -> str:
        texts = []
        for child in descendants(window):
            if isinstance(child, wx.TextCtrl):
                texts.append(child.GetValue())
            elif isinstance(child, wx.StaticText):
                texts.append(child.GetLabel())
            elif isinstance(child, wx.ListCtrl):
                texts.extend(
                    " | ".join(
                        child.GetItemText(row, column)
                        for column in range(child.GetColumnCount())
                    )
                    for row in range(child.GetItemCount())
                )
        return "\n".join(texts).lower()

    def assert_no_hardware_calls(self) -> None:
        self.assertEqual(self.commands, [])
        self.assertEqual(self.device.controller.calls, [])
        self.assertEqual(self.device.tcp.calls, [])
        connection = self.device.controller.connection
        if connection is not None:
            self.assertEqual(connection.calls, [])

    def test_ac_u06_1_unopened_usb_is_disconnected_without_probe(self) -> None:
        report = self.text(self.make_window())
        self.assertRegex(report, r"usb[^\n]*disconnected|disconnected[^\n]*usb")
        self.assert_no_hardware_calls()

    def test_ac_u06_1_closed_usb_handle_is_disconnected_without_probe(self) -> None:
        self.device.controller.connection = USBConnection(False)
        report = self.text(self.make_window())
        self.assertRegex(report, r"usb[^\n]*disconnected|disconnected[^\n]*usb")
        self.assert_no_hardware_calls()

    def test_ac_u06_1_open_usb_handle_reports_local_connected_state(self) -> None:
        self.device.controller.connection = USBConnection(True)
        report = self.text(self.make_window())
        self.assertRegex(report, r"usb[^\n]*connected|connected[^\n]*usb")
        self.assertNotIn("disconnected", report)
        self.assertRegex(report, r"passive|software|handle")
        self.assert_no_hardware_calls()

    def test_ac_u06_1_mock_mode_does_not_read_hardware_connection_getter(self) -> None:
        self.device.mock = True
        connection = USBConnection(True)
        self.device.controller.connection = connection
        report = self.text(self.make_window())
        self.assertIn("mock", report)
        self.assertEqual(connection.local_reads, 0)
        self.assert_no_hardware_calls()

    def test_ac_u06_1_network_socket_presence_is_unverified(self) -> None:
        self.device.networked = True
        usb = USBConnection(True)
        self.device.controller.connection = usb
        report = self.text(self.make_window())
        self.assertRegex(report, r"network|tcp")
        self.assertIn("unverified", report)
        self.assertNotRegex(report, r"(?:connection|network|tcp)[^\n]*\bconnected\b")
        self.assertEqual(usb.local_reads, 0)
        self.assert_no_hardware_calls()

    def test_ac_u06_1_network_transport_takes_precedence_over_mock_mode(self) -> None:
        self.device.mock = True
        self.device.networked = True
        usb = USBConnection(True)
        self.device.controller.connection = usb
        report = self.text(self.make_window())
        self.assertRegex(report, r"network|tcp")
        self.assertIn("unverified", report)
        self.assertNotIn("mock transport", report)
        self.assertNotRegex(report, r"(?:connection|network|tcp)[^\n]*\bconnected\b")
        self.assertEqual(usb.local_reads, 0)
        self.assert_no_hardware_calls()

    def test_ac_u06_2_software_pause_and_queue_do_not_claim_physical_progress(
        self,
    ) -> None:
        self.device.controller.state = "pause"
        self.queue.extend((object(), object(), object()))
        report = self.text(self.make_window())
        self.assertRegex(report, r"software[^\n]*pause|pause[^\n]*software")
        self.assertIn("software pause: paused", report)
        self.assertNotIn("software pause: not paused", report)
        self.assertRegex(report, r"queue[^\n]*\b3\b")
        self.assertRegex(report, r"physical[^\n]*(?:unknown|unavailable|not observed)")
        self.assertRegex(report, r"tube[^\n]*(?:unknown|unavailable|not observed)")
        self.assert_no_hardware_calls()

    def test_ac_u06_2_missing_controller_state_remains_unknown(self) -> None:
        self.device.controller = None
        report = self.text(self.make_window())
        self.assertRegex(report, r"controller[^\n]*unknown|unknown[^\n]*controller")
        self.assertEqual(self.commands, [])
        self.assertEqual(self.device.tcp.calls, [])

    def test_ac_u06_2_driver_pause_is_reported_when_controller_is_idle(self) -> None:
        self.device.controller.state = "idle"
        self.device.driver.paused = True
        report = self.text(self.make_window())
        self.assertRegex(report, r"software[^\n]*pause|pause[^\n]*software")
        self.assertIn("software pause: paused", report)
        self.assertNotIn("software pause: not paused", report)
        self.assertRegex(report, r"queue[^\n]*\b0\b")
        self.assertRegex(report, r"physical[^\n]*(?:unknown|unavailable|not observed)")
        self.assertRegex(report, r"tube[^\n]*(?:unknown|unavailable|not observed)")
        self.assert_no_hardware_calls()

    def test_ac_u06_2_missing_software_queue_remains_unknown(self) -> None:
        self.device.spooler = None
        report = self.text(self.make_window())
        self.assertRegex(report, r"queue[^\n]*(?:unknown|unavailable)")
        self.assertNotRegex(report, r"queue[^\n]*\b0\b")
        self.assert_no_hardware_calls()

    def test_ac_u06_3_connection_errors_show_count_and_relevant_next_step(self) -> None:
        self.device.controller.connection_errors = 7
        report = self.text(self.make_window())
        self.assertRegex(
            report, r"(?:connection[^\n]*errors?|errors?[^\n]*connection)[^\n]*\b7\b"
        )
        self.assertRegex(
            report,
            r"check[^\n]*(?:usb|cable|controller)|controller[^\n]*(?:check|retry)",
        )
        self.assert_no_hardware_calls()

    def test_ac_u06_3_inaccessible_status_shows_error_and_keeps_report_available(
        self,
    ) -> None:
        self.device.controller = InaccessibleController()
        window = self.make_window()
        report = self.text(window)
        self.assertIn("fixture status inaccessible", report)
        self.assertRegex(report, r"check|retry|controller window")
        self.assertIn("fixture co2", report)
        window.panel.refresh_data()
        self.assertIn("fixture status inaccessible", self.text(window))
        self.assert_no_hardware_calls()

    def test_ac_u06_3_switch_to_unsupported_device_drops_previous_diagnosis(
        self,
    ) -> None:
        self.device.controller.connection_errors = 71
        window = self.make_window()
        self.assertRegex(self.text(window), r"errors?[^\n]*\b71\b")
        other = Service(self.context.kernel, "fixture-router")
        other.name = "GRBLDevice"
        other.label = "Fixture router"
        other.controller = SoftwareController(USBConnection(True))
        self.context.kernel.add_service("device", other)
        self.context.kernel.activate_service_path("device", other.path)
        window.panel.refresh_data()
        report = self.text(window)
        self.assertIn("fixture router", report)
        self.assertIn("unsupported", report)
        self.assertNotRegex(report, r"errors?[^\n]*\b71\b")
        self.assertEqual(other.controller.connection.local_reads, 0)
        preferences = [
            child
            for child in descendants(window)
            if isinstance(child, wx.Button) and child.GetLabel() == "Preferences"
        ]
        self.assertEqual(len(preferences), 1)
        self.assertTrue(preferences[0].IsEnabled())
        self.assert_no_hardware_calls()

    def test_ac_u06_3_no_active_device_keeps_generic_tools_available(self) -> None:
        self.context.device = None
        window = self.make_window()
        report = self.text(window)
        self.assertIn("no active device", report)
        self.assertRegex(report, r"connection[^\n]*(?:unknown|unavailable)")
        preferences = [
            child
            for child in descendants(window)
            if isinstance(child, wx.Button) and child.GetLabel() == "Preferences"
        ]
        self.assertEqual(len(preferences), 1)
        self.assertTrue(preferences[0].IsEnabled())
        self.assert_no_hardware_calls()
