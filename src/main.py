import PySimpleGUI as sg
from datetime import datetime, timedelta
import Plotter
import Saver
import os
import sys
import numpy as np
import pyvisa
# from requests import request

layout = [[sg.Column([
    [sg.Frame("GPIB connection",
              [
                  [
                      sg.Text(text="Direct port:"),
                      sg.Combo([], key='ports_combo_direct', expand_x=True,
                               size=(50, 10), readonly=True)
                  ],
                  [
                      sg.Text(text="Forwarded port:"),
                      sg.Combo([], key='ports_combo_forwarded', expand_x=True,
                               size=(50, 10), readonly=True)
                  ],
                  [
                      sg.Button('Connect', key="connect_btn"),
                      sg.Button('Refresh', key="refresh_btn"),
                  ]
              ]
              )],
    [
        sg.Text("Folder name:"),
        sg.Input(default_text=datetime.now().strftime(
            "%Y%m%d"), enable_events=True, key='foldername')
    ],
    [
        sg.Text("Waiting for connection...", key='status'),
        sg.Text("", key='saved_file')
    ],
    [
        sg.Button('Download and save MEAS',
                  key="download_btn_meas", disabled=True),
    ],
    [
        sg.Button('Download and save MEAS - MEM',
                  key="download_btn_meas_mem", disabled=True),
    ],
    [
        sg.Button('Download and save MEM',
                  key="download_btn_mem", disabled=True),
    ],
    [
        sg.Multiline('Data', size=(50, 10), key='data_text',
                     autoscroll=True, disabled=True)
    ],
    [
        sg.Text("L. Zampieri - 05/2024", font=('Helvetica', 8)),
    ]
]), sg.Column([[
    sg.Canvas(key='canvas')
]])]]

window = sg.Window(title='HP8757E interface',
                   layout=layout, margins=(100, 100))
window.finalize()

# Prepare plot
plot = Plotter.Plotter(window['canvas'])
plot.first_draw()

# Prepare saver
sv = Saver.Saver('hp8757e')

# Inizialize pyvisa resource manager
rm = pyvisa.ResourceManager()

# Read available GPIB ports


def refresh_ports():
    ports = [res for res in rm.list_resources() if len(res) >
             4 and res[:4] == 'GPIB']
    window['ports_combo_direct'].update(values=ports, value=(
        ports[0] if len(ports) > 0 else ""))
    window['ports_combo_forwarded'].update(values=ports, value=(
        ports[1] if len(ports) > 1 else ""))


refresh_ports()

blink_dot = False
sna = None
sweeper = None

commands_dict = {
    'download_btn_meas': 'OD',
    'download_btn_meas_mem': 'ON',
    'download_btn_mem': 'OM'
}

while True:
    event, values = window.read(timeout=100)
    # print( event )

    if event == 'refresh_btn':
        refresh_ports()

    if event == 'connect_btn':
        try:
            sna = rm.open_resource(values['ports_combo_direct'])
            sna.write_termination = ''

            sweeper = rm.open_resource(values['ports_combo_forwarded'])
            sweeper.write_termination = ''
        except pyvisa.errors.VisaIOError as e:
            sna = None
            sweeper = None

        if (sna and sweeper):

            window['connect_btn'].update(disabled=True)
            window['refresh_btn'].update(disabled=True)
            window['ports_combo_direct'].update(disabled=True)
            window['ports_combo_forwarded'].update(disabled=True)

            window['download_btn_meas'].update(disabled=False)
            window['download_btn_meas_mem'].update(disabled=False)
            window['download_btn_mem'].update(disabled=False)
            window['status'].update("Connected")
        else:
            window['status'].update("Connection failed")
            refresh_ports()

    if event in commands_dict.keys():
        if (sna and sweeper):

            # Download start and end freq from sna
            window['status'].update("Downloading data from sweeper")
            sna.write("PT19;")
            sweeper.write("OPFA;")
            start_f = float(sweeper.read_ascii_values()[0])
            sweeper.write("OPFB;")
            final_f = float(sweeper.read_ascii_values()[0])

            # Download the data
            window['status'].update("Downloading data from sna")
            sna.write(commands_dict[event] + ";")
            ys = sna.read_ascii_values()

            # Compute the x axis assuming linear spacing
            xs = np.linspace(start_f, final_f, len(ys)) / 1e6

            # Add here the saving logic
            window['status'].update("Saving data")
            content = ""
            for x, y in zip(xs, ys):
                content += f"{x:.3e},{y:.3f}\n"
            window['data_text'].update(content)
            filename = sv.save(values['foldername'], content)

            plot.update_data(xs, ys)
            window['status'].update(f"Saved on {filename}")

    if event == 'foldername':
        window['foldername'].update(
            Saver.Saver.clean_foldername(values['foldername']))

    if event == sg.WIN_CLOSED:
        break

window.close()
sys.exit()
