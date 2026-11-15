# src

The solution, written during the event (14 to 15 November 2026).

Sea surface temperature track
- sst_from_frame.py: reads the colour legend and turns one video frame into a grid of temperatures
- sst_to_sound.py: turns the grid into a stereo audio track
- make_track_video.py: draws the playhead and joins sound and picture

Air quality track
- aq_from_frame.py: turns one video frame into a grid of relative pollutant strength
- aq_to_sound.py: gives each pollutant its own voice and writes the audio
- make_aq_video.py: draws the playhead and joins sound and picture

Hardware
- sst_hardware_demo.py: plays the sea surface sweep and drives the Arduino in step
  with the sound

Several scripts began as first drafts written with help from Claude (Anthropic);
see docs/credits.md.