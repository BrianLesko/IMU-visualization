# Brian Lesko
# 4/10/2024
# IMU Visualizer app written in pure python

import streamlit as st
import arduino as ard
import numpy as np
import plotly.graph_objects as go
import customize_gui
from scipy.spatial.transform import Rotation as R
import time

# Initialize GUI
gui = customize_gui.gui()
gui.clean_format(wide=True)
gui.about(text="Visualize your IMU data in 3D space.")
st.markdown("## IMU Visualizer")
_, col2, _ = st.columns([1, 69, 1])
with col2:
    Fig = st.empty()
with st.sidebar:
    "---"
    st.write("### Ports Available")
    for port in reversed(ard.arduino.list_ports()):
        if st.button(f"{port}"):
            st.session_state.PORT = port
    "---"
    st.write("### Valid Data Rate")
    Rate = st.empty()
    with Rate: st.write("--")
    "---"
    st.write("### Raw Data")
    Data = st.empty()
    with Data: st.write("--")
    "---"

# Initialize Arduino
BAUD = 115200
N = 5 # Number of state values to average
if "my_arduino" not in st.session_state:
    try:
        st.session_state.my_arduino = ard.arduino(st.session_state.PORT, BAUD, 1)
        with st.sidebar:
            print(f"Connection to {st.session_state.PORT} successful")
    except Exception as e:
        st.error("Not Connected")
        

# Initialize Plotly figure
fig = go.Figure()
fig.update_layout(
    autosize=False,
    width=800,
    height=700,
    margin=dict(l=0, r=0, b=0, t=0),
    scene=dict(
        xaxis=dict(range=[-1, 1], autorange=False, tickvals=[-1, -0.5, 0, 0.5, 1], showspikes=False),
        yaxis=dict(range=[-1, 1], autorange=False, tickvals=[-1, -0.5, 0, 0.5, 1], showspikes=False),
        zaxis=dict(range=[-1, 1], autorange=False, tickvals=[-1, -0.5, 0, 0.5, 1], showspikes=False),
        aspectmode='cube',
        camera=dict(
            up=dict(x=0, y=0, z=.5),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.25, y=1.25, z=1.25)
        )
    ),
)

# Initialize data lists
rolls, pitches, yaws, altitudes = [], [], [], []
roll = pitch = yaw = 0

# Main loop
start_time = time.time()
while True:
    # Receive data
    try:
        new_data = st.session_state.my_arduino.read()

    except Exception as e:
        print(e)
        break

    # Process data
    try:
        values = list(map(float, new_data.split(':')[1].split(',')))
        if len(values) == 4:
            roll, pitch, yaw, altitude = values
            altitudes.append(altitude)
            with Data: st.write(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}, Altitude: {altitude:.2f}")
        elif len(values) == 3:
            roll, pitch, yaw = values
            with Data: st.write(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")
        else:
            raise ValueError("Invalid number of values")
        roll, pitch, yaw = np.radians([roll, pitch, yaw])
        rolls.append(roll)
        pitches.append(pitch)
        yaws.append(yaw)
    except ValueError:
        print("Invalid data")
        continue
    except IndexError:
        print("Data does not contain expected ':' character")
        continue

    if len(rolls) > N:
        roll, pitch, yaw = map(np.mean, [rolls[-N:], pitches[-N:], yaws[-N:]])
    vector = np.array([0, 0, 1])  # Example vector
    vector = vector / np.linalg.norm(vector)
    r = R.from_euler('xyz', [roll, pitch, yaw])
    rotated_vec = r.apply(vector)
    quaternion = r.as_quat()
    x,y,z = rotated_vec

    # Update figure
    fig.data = []
    fig.add_trace(go.Scatter3d(x=[0, x], y=[0, y], z=[0, z], mode='lines', line=dict(width=10, color='red'), hoverinfo='none'))
    fig.add_trace(go.Cone(x=[0.9 * x], y=[0.9 * y], z=[0.9 * z], u=[0.1 * x], v=[0.1 * y], w=[0.1 * z], sizemode="scaled", sizeref=2.5, showscale=False, colorscale=[(0, 'red'), (1, 'red')], cmin=-1, cmax=1, hoverinfo='none'))
    Fig.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # update data rate 
    with Rate:
        st.write(f"Data Rate: {len(rolls) / (time.time() - start_time):.2f} Hz")