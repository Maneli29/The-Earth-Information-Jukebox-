# Credits

NASA Space Apps Challenge 2026, Dar es Salaam (virtual).
Challenge: The Earth Information Jukebox.
Project: Earth Jukebox, sea surface temperature turned into sound.

## NASA data
Global Sea Surface Currents and Temperature:
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
Dimitris Menemenlis (NASA/JPL CalTech)

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
Ella Kaplan (Global Science and Technology, Inc.)

## Software and tools
- Python 3.14-64, with these libraries: OpenCV, NumPy, SciPy, PySerial, sounddevice
- ffmpeg (joining audio and video, shrinking the video)
- Arduino IDE, with the Servo library and the U8g2 library (OLED screen)
- Visual Studio Code, Git and GitHub Desktop
- Windows Paint (reading pixel coordinates of the colour legend)
- [Screen reader used for testing, for example NVDA or TalkBack]

## Hardware
- Arduino Uno starter kit: servo, passive buzzer, LEDs, push button,
  potentiometer, 4-pin I2C OLED screen.


## AI use
AI tools used: Claude (Anthropic).

What the AI helped with:
- Explaining the Space Apps challenge and the Earth Information Jukebox statement.
- Planning the project and the two-day schedule.
- Step-by-step guidance for the GitHub repository, Arduino wiring and testing.
- Drafting code that I then ran, tested and adjusted: the Python scripts
  (media inspection, colour-legend temperature extraction, sonification, playhead
  video, Arduino link), the Arduino sketch, and the first version of the web page.
- Drafting this credits file and the README structure.

What I did myself:
- Chose the challenge and the NASA visualizations.
- Built and wired the Arduino hardware and tested each part.
- Measured the colour legend positions in the image and checked the results
  against the original map.
- Ran every script, listened to the results, and chose and adjusted the sound
  mapping and the web page.
- Recorded the demo video 

