import pandas as pd
from math import radians, sin, cos, sqrt, atan2

def gps2midi(df, outfile="stork_melody.mid",
             pitch_scale=(60, 64, 67, 69, 72),  # C pentatonic
             time_factor=1/10000):
    """
    Convert stork GPS track to monophonic melody MIDI.
    df columns: timestamp (datetime64), location-lat, location-long,
                height-above-ellipsoid, ground-speed.
    Requires midiutil (pip install midiutil) available.
    """
    from midiutil import MIDIFile
    m = MIDIFile(1)
    m.addTrackName(0, 0, "Stork Melody")
    m.addTempo(0, 0, 120)
    t0 = df['timestamp'].iloc[0]
    lat_min, lat_max = df['location-lat'].min(), df['location-lat'].max()
    lon_min, lon_max = df['location-long'].min(), df['location-long'].max()

    for _, row in df.iterrows():
        lat_norm = (row['location-lat'] - lat_min) / (lat_max - lat_min)
        lon_norm = (row['location-long'] - lon_min) / (lon_max - lon_min)
        pc_index = int(round((0.6*lat_norm + 0.4*lon_norm)*(len(pitch_scale)-1)))
        pitch_class = pitch_scale[max(0, min(pc_index, len(pitch_scale)-1))]
        alt = row['height-above-ellipsoid']
        octave_shift = 0 if alt<=500 else 12 if alt<=1500 else 24
        pitch = pitch_class + octave_shift
        t_sec = (row['timestamp'] - t0).total_seconds()*time_factor
        duration = 0.5
        vel = int(min(max(row['ground-speed']*15 + 40, 40), 110))
        m.addNote(0, 0, pitch, t_sec, duration, vel)
    with open(outfile, "wb") as f:
        m.writeFile(f)
