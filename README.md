# Earth Jukebox

Hear NASA's Earth data. Earth Jukebox turns two NASA Earth visualizations, the
temperature of the world's oceans and global air pollution, into sound that can
be explored by listening, with an accessible web page and an optional Arduino
touch interface.

NASA Space Apps Challenge 2026, Dar es Salaam local event (virtual, solo entry).
Challenge: **The Earth Information Jukebox**.

- Live page: [\[link to the GitHub Pages page\]](https://github.com/Maneli29/The-Earth-Information-Jukebox-)
- Demo video: [\[link\]](https://youtu.be/TvvfazYd3jg)

## The problem

NASA's Earth Information Center publishes striking visualizations of our
changing planet, but they are visual. Blind and low-vision users, and anyone who
cannot read a colour map, are shut out of the science. Sound can carry the same
information.

## What it does

Two tracks, each a sweep across a NASA visualization with a white playhead line
that moves in time with the sound:

1. **Sea surface temperature.** The map's own colour legend (0 to 32 C) is used
   to turn colours back into temperatures. Warmer water is a higher, brighter
   note. Land and ice are silence, so you can hear the continents as gaps.
2. **Air quality.** A globe divided into three sections for three pollutants:
   carbon monoxide (a short pluck), fine particles PM2.5 (a soft pad) and
   nitrous oxides (bells). Stronger colour is a higher, louder note.

In both tracks, time runs west to east, sound moves from the left speaker to the
right, and five quick notes at each step are five bands of latitude, north to
south.

**Accessible web page** (`web/index.html`): choose a track, large buttons,
full keyboard use, labelled controls, a plain-language description of what the
listener hears, and optional place announcements for screen readers. Tested with
NVDA.

**Optional touch interface** (`arduino/`): an Arduino shows the same data by
touch and light: a servo needle for the average temperature, five LEDs for the
five latitude bands, and an OLED screen with the current value.


## How it works

For each track, three scripts in `src/`:

1. **Read the picture.** One frame of the NASA video is converted to colour
   values (OpenCV, NumPy).
   - Sea surface: the colour legend is sampled and each ocean pixel's hue is
     converted to degrees C. The map is averaged into a grid of 64 steps (west to
     east) by 5 latitude bands.
   - Air quality: each pollutant section has its own colour rule (yellow to red
     for carbon monoxide and PM2.5, light to dark green for nitrous oxides),
     giving a relative strength from 0 to 1 on the same kind of grid.
2. **Make the sound.** Each grid cell becomes a note (SciPy, NumPy). Strength
   sets pitch and loudness, snapped to a five-note scale so it stays musical.
   Empty cells are silent. Sea surface also brightens the tone as water warms.
3. **Make the video.** A white playhead line is drawn across the frame in step
   with the audio, and ffmpeg joins sound and picture.

## Data and its limits

- **Sea surface temperature:** temperatures are read back from the colours using
  the visualization's own legend, so they are approximate averages, not exact
  measurements.
- **Air quality:** the frame has no colour legend, so the sound shows relative
  strength within each pollutant. Loudness cannot be compared between pollutants,
  and the values are not real concentrations.
- Each track is built from **one frame** of its video, so it is a snapshot in
  time, not a record of change.
- The air quality picture is a globe, so areas near its edge are squashed.

## Repository

```
web/       The accessible web page and the two finished tracks
src/       The solution code (built during the event)
arduino/   Sketch for the optional touch interface
docs/      Credits and AI use, notes on the data
practice/  Tool setup and hardware tests done before the event
data/      Downloaded NASA files (not stored in the repository)
```

## Run it yourself

1. Install Python 3 and ffmpeg, then `pip install -r requirements.txt`.
2. Download the two NASA videos listed in `docs/credits.md` into `data/` (the
   exact file names are in `data/README.md`).
3. Sea surface track: run `src/sst_from_frame.py`, then `src/sst_to_sound.py`,
   then `src/make_track_video.py`.
4. Air quality track: run `src/aq_from_frame.py`, then `src/aq_to_sound.py`,
   then `src/make_aq_video.py`.
5. Copy the two finished videos from `data/` to `web/` and open
   `web/index.html`.
6. Optional hardware: upload the sketch in `arduino/earth_jukebox_hw/`, set the
   serial port in `src/sst_hardware_demo.py`, and run it.

## What was built during the event

Everything in `src/` and `web/`, and the final Arduino sketch in `arduino/`, was
written on 14 to 15 November 2026. Before the event I set up the repository and
tools, wrote a media inspection script, and tested the Arduino parts one by one
(that work is in `practice/`).

## Limitations and next steps

- Use several frames per video so the sound follows change over time.
- Add real concentration values for air quality if a colour legend or the source
  data is available.
- Add more Earth Information Center visualizations as tracks.
- User-test with blind and low-vision listeners and improve the sound design
  from their feedback.

## Credits and AI use

Full details are in [`docs/credits.md`](docs/credits.md).

Data: NASA Scientific Visualization Studio, Global Sea Surface Currents and Temperature:
Page Link: https://svs.gsfc.nasa.gov/3912/#media_group_349716
Credits: NASA/Goddard Space Flight Center Scientific Visualization Studio

Animators
Greg Shirah (NASA/GSFC) ORCID logo. It consists of the text 'id' in lowercase inside of a green circle.
Horace Mitchell (NASA/GSFC)
Eric Sokolowsky (Global Science and Technology, Inc.)
Project support
Eric Sokolowsky (Global Science and Technology, Inc.)
Producer
Michael Starobin (HTSI)
Scientists
Hong Zhang (UCLA)
Dimitris Menemenlis (NASA/JPL CalTech);
Air Quality Model Runs:
Page Link: https://svs.gsfc.nasa.gov/5533/
Credits: NASA's Scientific Visualization Studio and NASA's Global Modeling and Assimilation Office

Data visualizers
Helen-Nicole Kostis (USRA) ORCID logo. It consists of the text 'id' in lowercase inside of a green circle.
Joseph V. Ardizzone (NASA/GSFC) ORCID logo. It consists of the text 'id' in lowercase inside of a green circle.
Scientist
Lesley Ott (NASA/GSFC) ORCID logo. It consists of the text 'id' in lowercase inside of a green circle.
Technical support
Laurence Schuler (ADNET Systems, Inc.)
Ian Jones (ADNET Systems, Inc.)
Ella Kaplan (Global Science and Technology, Inc.).

Built with Python (OpenCV, NumPy, SciPy, PySerial, sounddevice), ffmpeg, and an
Arduino (Servo and U8g2 libraries).

AI use: I used Claude (Anthropic) to plan the project and draft code, which I
then tested and adjusted. I chose the data, built and wired the hardware, ran
and checked every script, and made the design decisions. 

## Licence

MIT