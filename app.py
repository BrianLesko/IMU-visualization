# Brian Lesko
# 4/10/2024
# IMU Visualizer app written in pure python

import streamlit as st
import arduino as ard
import numpy as np
import plotly.graph_objects as go
import customize_gui

# Constants
PORT = '/dev/cu.usbmodemCC793F7E2'
#'/dev/tty.usbmodem11301'
BAUD = 9600
DELAY = 0.1
N = 10

# Initialize GUI
gui = customize_gui.gui()
gui.clean_format(wide=True)
gui.about(text="Visualize your IMU data in 3D space.")
st.markdown("## IMU Visualizer")

with st.sidebar:
    st.write("### Connection")
    st.selectbox("Available Ports",ard.arduino.list_ports())

# Initialize Arduino
if "my_arduino" not in st.session_state:
    try:
        st.session_state.my_arduino = ard.arduino(PORT, BAUD, DELAY)
        print(f"Connection to {PORT} successful")
        with st.sidebar:
            st.write(f"Connection to {PORT} successful")
    except Exception as e:
        print("Could not connect to arduino")

# Initialize Streamlit elements
Data = st.empty()
_, col2, _ = st.columns([1, 69, 1])
with col2:
    Fig = st.empty()

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
rolls, pitches, yaws = [], [], []

# Main loop
while True:
    try:
        new_data = st.session_state.my_arduino.read()
    except Exception as e:
        print(e)
        break

    with Data:
        st.write(new_data)

    if not new_data:
        st.error("No data received")
        st.stop()

    # Process data
    try:
        roll, pitch, yaw = map(float, new_data.split(':')[1].split(','))
        roll, pitch, yaw = np.radians([roll, pitch, yaw])
        rolls.append(roll)
        pitches.append(pitch)
        yaws.append(yaw)
    except:
        print("Invalid data")

    # Average last N values
    if len(rolls) > N:
        roll, pitch, yaw = map(np.mean, [rolls[-N:], pitches[-N:], yaws[-N:]])

    # Convert to Cartesian coordinates
    x, y, z = np.cos(yaw) * np.cos(pitch), np.sin(yaw) * np.cos(pitch), np.sin(pitch)
    vector = np.array([x, y, z])
    vector = vector / np.linalg.norm(vector)  # Normalize
    x, y, z = vector

    # Update figure
    fig.data = []
    fig.add_trace(go.Scatter3d(x=[0, x], y=[0, y], z=[0, z], mode='lines', line=dict(width=10, color='red'), hoverinfo='none'))
    fig.add_trace(go.Cone(x=[0.9 * x], y=[0.9 * y], z=[0.9 * z], u=[0.1 * x], v=[0.1 * y], w=[0.1 * z], sizemode="scaled", sizeref=2.5, showscale=False, colorscale=[(0, 'red'), (1, 'red')], cmin=-1, cmax=1, hoverinfo='none'))

    # Update Streamlit elements
    Fig.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})