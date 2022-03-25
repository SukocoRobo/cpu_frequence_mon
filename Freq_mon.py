"""
freq-mon.py
It collects CPU frequencies per core over specific time period and interval, does some basic statistic and visualizes them.
Copyright (C) 2021  Malte Biermann

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import subprocess
import threading
import time
import pandas as pd
import matplotlib.pyplot as plt
import feather


def get_freqs():
    cmd = 'cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq'  # immer gleiche reihenfolge?
    freqs = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    return freqs.stdout.decode('utf-8').splitlines()


def init_vars():
    l_freqs = get_freqs()
    d_cores = {}
    i_coresNr = len(l_freqs)
    for i in range(i_coresNr):
        d_cores[i] = []
    return (d_cores, i_coresNr)


def freq_append(d_cores, l_freqs, i_coresNr):
    for i in range(i_coresNr):
        d_cores[i].append(int(l_freqs[i]))
    return d_cores


def to_df(d_cores):
    df = pd.DataFrame.from_dict(d_cores)
    df.columns = df.columns.astype(str)
    df.to_feather('data')
    return df


def analyze(df):
    print(df.head(), df.shape)
    print(df.describe())
    p_l = df.plot(figsize=(20, 15))
    plt.savefig('fig-line.png')
    p_b = df.plot.box(figsize=(20, 15))
    plt.savefig('fig-box.png')


if __name__ == '__main__':
    readfile = True
    if readfile != True:
        totalstarttime = time.time()
        set_totalduration_sec = 60
        set_sample_freq = 10

        sample_duration_sec = 1 / set_sample_freq
        nr_samples = set_totalduration_sec * set_sample_freq

        d_cores, i_cores_nr = init_vars()

        mean_dur_sec = 0
        for j in range(nr_samples):
            starttime = time.time()
            l_freqs = get_freqs()
            d_cores = freq_append(d_cores, l_freqs, i_cores_nr)
            endtime = time.time()
            dur_sec = endtime - starttime
            mean_dur_sec = (mean_dur_sec * j / (j + 1)) + (dur_sec * (1 / (j + 1)))
            remtimetosleep_sec = sample_duration_sec - mean_dur_sec
            time.sleep(remtimetosleep_sec)

        totalendtime = time.time()
        total_duration_sec = totalendtime - totalstarttime
        print(f'mean_duration:{mean_dur_sec:.3f}s, total_duration:{total_duration_sec:.3f}s')
        # print(d_cores)
        df = to_df(d_cores)

    else:
        df = feather.read_dataframe('data')

    analyze(df)