import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
import numpy as np
import mplcyberpunk
import json
from bubble_tracker import Bubble


plt.style.use("fast")

def average_between_bigs():
    '''
    json model:
        "1.7": [
        {
            "center": [
                49,
                1080
            ],
            "top": 560,
            "bottom": 1600,
            "height": 1040,
            "width": 98,
            "is_big": true,
            "state": "increasing",
            "id": 137
        }
        ]
    '''
    # Load data
    with open('data.json', 'r') as f:
        data = json.load(f)

    deltas = []
    last_big_time = 0.0 
    for time, bubbles in data.items():
        for bubble in bubbles:
            if bubble['is_big']:
                delta = float(time) - last_big_time
                if delta > 0.5:
                    deltas.append(delta)
                last_big_time = float(time)
    
    # find average delta
    average = sum(deltas) / len(deltas)

    x = np.linspace(0, len(deltas), len(deltas))
    y = deltas

    fig, ax = plt.subplots()
    ax.grid(zorder=0)  # type: ignore
    ax.bar(x, y, color='#2a9d8f', width=0.94,  # type: ignore
           edgecolor="gray", linewidth=0.1, zorder=3)
    plt.title("Время между большими пузырьками", fontsize=20)
    plt.ylabel("Время, с", fontsize=16)
    plt.xticks([])  # disable x axis ticks
    plt.text(0.5, -0.05, f"Среднее время: {average:.2f} с", fontsize=16,
             horizontalalignment='center', verticalalignment='bottom',
             transform=ax.transAxes)  # type: ignore

    plt.show()

    plt.show()
    return average


def on_height():
    '''
    json model:
        "1.7": [
        {
            "center": [
                49,
                1080
            ],
            "top": 560,
            "bottom": 1600,
            "height": 1040,
            "width": 98,
            "is_big": true,
            "state": "increasing",
            "id": 137
        }
        ]
    '''
    # Load data
    with open('data.json', 'r') as f:
        data = json.load(f)

    ay = []
    by = []
    for time, bubbles in data.items():
        for bubble in bubbles:
            top = bubble['top']
            if bubble['is_big']:
                ay.append(top)
            else:
                by.append(top)

    ay.sort()
    by.sort()
    y = np.vstack([ay, by])

    x = np.linspace(0, len(y), len(y))
    fig, ax = plt.subplots()

    ax.stackplot(x, y, color='#2a9d8f')  # type: ignore
    plt.show()

if __name__ == '__main__':
    on_height()
    # print(average_between_bigs())
