# main_gui.py  ── solo parte gráfica ────────────────────────────────
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, VerticalScroll
from textual.widgets import Static, Select, Input, Button, Checkbox, Label, Header, Footer
import serialFunctions as sf   # backend

# ───────────────────────────────────────────────────────────────────
class ConfigPanel(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Label("Baudrate")
        yield Select(
            [("9600","9600"), ("19200","19200"), ("38400","38400"),
             ("57600","57600"), ("115200","115200")],
            id="baud"
        )
        yield Label("Port")
        yield Select(sf.getFilteredPorts(), id="port")

        yield Label("Delay (ms)")
        yield Select([("16","16"),("32","32"),("64","64"),("128","128")], id="delay")
        yield Label("Measures (N)")
        yield Select([("4","4"),("8","8"),("16","16"),("32","32")], id="meas")

        yield Label("Log")
        yield Input(placeholder="/home/username/myData.scv", id="directory")
        yield Checkbox("Save CSV", id="csv")   # guarda los datos
        yield Checkbox("Loop", id="loop_soft") # loop por software

        yield Label("Control")
        yield Button("INIT", id="init", variant="success")
        yield Button("STOP", id="stop", variant="error")

        yield Label("Graph")
        yield Button("PLOT", id="plot", variant="primary")
        yield Input(placeholder="T_sens0 T_sens1", id="plot_vars")
        yield Input(placeholder="first last",          id="plot_range")


# ───────────────────────────────────────────────────────────────────
class DataDisplay(Static):
    def push(self, line:str):
        lines = (self.renderable or "").splitlines()
        lines.append(line)
        while len(lines) > self.size.height:
            lines.pop(0)
        self.update("\n".join(lines))

#self.size.height
class Console(Static):
    def __init__(self, *args, **kwargs):
        super().__init__("", *args, **kwargs)
        self.buffer = []

    def push(self, line: str):
        items=line.split("\n")
        for i in items:
            self.buffer.append(i)
        # Limita el número de líneas con el tamaño de la consola
        if len(self.buffer) > self.size.height:
            self.buffer = self.buffer[-self.size.height:]
        self.update("\n".join(self.buffer))

    def log(self, txt: str):
        self.push(txt)


# ───────────────────────────────────────────────────────────────────
class DataloggerApp(App):
    CSS_PATH = "style.tcss"

    # helpers
    def _cfg(self, wid:str): return self.query_one(f"#{wid}").value
    def _cons(self) -> Console:   return self.query_one("#cons", Console)

    def _update_conn(self):
        port = self._cfg("port")
        baud = self._cfg("baud")
        
        # asegurar que el usuario haya seleccionado algo valido
        if port == Select.BLANK or baud == Select.BLANK:
            self._cons().log("[setup] Waiting port y baudrate...")
            return
        
        if port != "None" and baud:
            msg = sf.open_serial(port, int(baud))
            self._cons().log(f"[setup] {msg}")

    # events
    def on_select_changed(self, e:Select.Changed):
        if e.select.id in ("port", "baud"):
            self._update_conn()

    def on_button_pressed(self, e:Button.Pressed):
        cons = self._cons()
        if e.button.id == "init":
            cons.log(sf.serialInit())
        elif e.button.id == "stop":
            cons.log(sf.serialStop())
        elif e.button.id == "loop":
            cons.log(sf.serialLoop())
        
        elif e.button.id == "plot":
            cons.log(f"[plot] vars={self._cfg('plot_vars')} range={self._cfg('plot_range')}")

    def on_input_submitted(self, e:Input.Submitted):
        if e.input.id == "command":
            cmd = e.value.strip()
            cons = self._cons()
            if cmd:
                cons.log("> " + cmd)
                sf.serialSendCmd(cmd)
                cons.log(sf.serialResponse())
            e.input.value = ""

    # layout
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            ConfigPanel(id="cfg"),
            Container(
                Static("Data:"),
                DataDisplay(id="data", classes="box"),
                
                Static("Terminal:"),
                Console(id="cons", classes="box"),
                
                Input(placeholder="Write and Enter", id="command"),
                id="panel_datos"
            )
        )
        yield Footer()


if __name__ == "__main__":
    DataloggerApp().run()
