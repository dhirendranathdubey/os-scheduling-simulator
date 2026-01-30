import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

# ---------------- Utility ---------------- #
def random_color():
    return (random.random(), random.random(), random.random())

# ---------------- Scheduling Algorithms ---------------- #
def fcfs(processes):
    processes.sort(key=lambda x: x[1])
    start, completion = 0, []
    for p in processes:
        start = max(start, p[1])
        ct = start + p[2]
        completion.append((p[0], p[1], p[2], ct))
        start = ct
    return completion

def sjf_np(processes):
    processes.sort(key=lambda x: (x[1], x[2]))
    time, done, completion = 0, [], []
    while len(done) < len(processes):
        ready = [p for p in processes if p not in done and p[1] <= time]
        if ready:
            p = min(ready, key=lambda x: x[2])
            start = max(time, p[1])
            ct = start + p[2]
            completion.append((p[0], p[1], p[2], ct))
            time = ct
            done.append(p)
        else:
            time += 1
    return completion

def srtf(processes):
    n = len(processes)
    remaining = [p[2] for p in processes]
    complete, time, done, result = 0, 0, [False]*n, []
    timeline = []
    while complete < n:
        idx = -1
        min_bt = 999999
        for i in range(n):
            if processes[i][1] <= time and remaining[i] > 0:
                if remaining[i] < min_bt:
                    min_bt = remaining[i]
                    idx = i
        if idx == -1:
            time += 1
            continue
        timeline.append((time, processes[idx][0]))
        remaining[idx] -= 1
        if remaining[idx] == 0:
            complete += 1
            ct = time + 1
            result.append((processes[idx][0], processes[idx][1], processes[idx][2], ct))
            done[idx] = True
        time += 1
    return result, timeline

def round_robin(processes, tq):
    queue, time, completion, timeline = [], 0, [], []
    remaining = {p[0]: p[2] for p in processes}
    arrived = {p[0]: p[1] for p in processes}
    order = [p[0] for p in processes]

    while remaining:
        for p in order:
            if p in remaining and arrived[p] <= time:
                bt = remaining[p]
                exec_time = min(bt, tq)
                for t in range(exec_time):
                    timeline.append((time+t, p))
                time += exec_time
                remaining[p] -= exec_time
                if remaining[p] == 0:
                    completion.append((p, arrived[p], 0, time))
                    del remaining[p]
    return completion, timeline

def priority_np(processes):
    processes.sort(key=lambda x: (x[1], x[3]))
    time, done, completion = 0, [], []
    while len(done) < len(processes):
        ready = [p for p in processes if p not in done and p[1] <= time]
        if ready:
            p = min(ready, key=lambda x: x[3])
            start = max(time, p[1])
            ct = start + p[2]
            completion.append((p[0], p[1], p[2], ct, p[3]))
            time = ct
            done.append(p)
        else:
            time += 1
    return completion

def priority_p(processes):
    n = len(processes)
    remaining = [p[2] for p in processes]
    complete, time, done, result = 0, 0, [False]*n, []
    timeline = []
    while complete < n:
        idx = -1
        min_pr = 999999
        for i in range(n):
            if processes[i][1] <= time and remaining[i] > 0:
                if processes[i][3] < min_pr:
                    min_pr = processes[i][3]
                    idx = i
        if idx == -1:
            time += 1
            continue
        timeline.append((time, processes[idx][0]))
        remaining[idx] -= 1
        if remaining[idx] == 0:
            complete += 1
            ct = time + 1
            result.append((processes[idx][0], processes[idx][1], processes[idx][2], ct, processes[idx][3]))
            done[idx] = True
        time += 1
    return result, timeline

def hrrn(processes):
    time, done, completion = 0, [], []
    while len(done) < len(processes):
        ready = [p for p in processes if p not in done and p[1] <= time]
        if ready:
            hr = []
            for p in ready:
                wt = time - p[1]
                ratio = (wt + p[2]) / p[2]
                hr.append((ratio, p))
            p = max(hr, key=lambda x: x[0])[1]
            start = max(time, p[1])
            ct = start + p[2]
            completion.append((p[0], p[1], p[2], ct))
            time = ct
            done.append(p)
        else:
            time += 1
    return completion

# ---------------- Streamlit UI ---------------- #
st.set_page_config(page_title="OS Scheduling Simulator", layout="centered")


st.title("⚡ OS Scheduling Simulator")
st.caption("👑 Owner: Dhirendra Dubey")

st.write("Select an algorithm and provide process details 👇")

algo = st.selectbox("Select Scheduling Algorithm", [
    "FCFS", "SJF (Non-Preemptive)", "SRTF (Preemptive)",
    "Round Robin", "Priority (Non-Preemptive)", "Priority (Preemptive)", "HRRN"
])

n = st.number_input("Number of Processes", min_value=1, max_value=10, value=3)

arrival_times, burst_times, priorities = [], [], []

st.subheader("👉 Enter Process Details")
for i in range(int(n)):
    at = st.number_input(f"Arrival Time P{i+1}", min_value=0, key=f"at{i}")
    bt = st.number_input(f"Burst Time P{i+1}", min_value=1, key=f"bt{i}")
    pr = 0
    if "Priority" in algo:
        pr = st.number_input(f"Priority P{i+1}", min_value=1, key=f"pr{i}")
    arrival_times.append(at)
    burst_times.append(bt)
    priorities.append(pr)

tq = 0
if algo == "Round Robin":
    tq = st.number_input("Enter Time Quantum", min_value=1, value=2)

if st.button("🚀 Run Scheduling"):
    processes = [(f"P{i+1}", arrival_times[i], burst_times[i], priorities[i]) for i in range(int(n))]
    result, timeline = [], []

    if algo == "FCFS":
        result = fcfs(processes)
    elif algo == "SJF (Non-Preemptive)":
        result = sjf_np(processes)
    elif algo == "SRTF (Preemptive)":
        result, timeline = srtf(processes)
    elif algo == "Round Robin":
        result, timeline = round_robin(processes, tq)
    elif algo == "Priority (Non-Preemptive)":
        result = priority_np(processes)
    elif algo == "Priority (Preemptive)":
        result, timeline = priority_p(processes)
    elif algo == "HRRN":
        result = hrrn(processes)

    # Show Table
    st.subheader("📊 Scheduling Result")
    cols = ["Process", "Arrival", "Burst", "Completion"]
    if "Priority" in algo:
        cols.append("Priority")
    df = pd.DataFrame(result, columns=cols)
    df["Turnaround"] = df["Completion"] - df["Arrival"]
    df["Waiting"] = df["Turnaround"] - df["Burst"]
    st.dataframe(df)

    # Show Average
    st.write(f"**Average Turnaround Time:** {df['Turnaround'].mean():.2f}")
    st.write(f"**Average Waiting Time:** {df['Waiting'].mean():.2f}")

    # Fancy Gantt Chart - Timeline Style
    st.subheader(" Gantt Chart ")
    fig, ax = plt.subplots(figsize=(10, 3))
    colors = {}
    if timeline:
        for t, p in timeline:
            if p not in colors:
                colors[p] = random_color()
            ax.broken_barh([(t, 1)], (10, 9), facecolors=(colors[p]))
            ax.text(t+0.5, 14, p, ha='center', va='center', fontsize=8, color="black")
    else:
        y = 10
        for row in result:
            start = row[1]
            bt = row[2]
            p = row[0]
            if p not in colors:
                colors[p] = random_color()
            ax.broken_barh([(start, bt)], (y, 9), facecolors=(colors[p]))
            ax.text(start + bt/2, y+4, p, ha='center', va='center', color="white", fontsize=9, fontweight="bold")
            y += 10

    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_title("CPU Execution Timeline")
    ax.grid(True, axis='x')
    st.pyplot(fig)
