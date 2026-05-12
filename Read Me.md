# Automatic Measurement and EQ Program

## This was made as my Final Project for University, which was graded as a 1st.

### About the project :

This took heavy inspiration from existing equalisation (EQ) programs such as AutoEQ by jaakkopasanen as well as REW (Room EQ Wizard). 

The goal of the program is to record the frequency response using a microphone (in my case, a Samson Q2U) and equalise the measurement towards the over ear harman target. I had planned to extend the functionality for in-ear monitors (IEMs) and other targets, though I do not have a 711 coupler for IEM measurements which stops me from testing the accuracy of the EQ and measurements for IEMs.

As I've been using a regular microphone, the measurements and EQ are not fully represenatitive of real life performance or accuracy but they were close enough for my purposes to be able to test and verify functionality.

### Current issues :
<sup>When fixed, will either remove from list or put a tick next to the respective issue</sup>

- Current EQ process does not weigh into account volume of the initial measurement.
- Graph shown by program when EQ finishes shows line correction rather than exported in EQ file.

### Prerequisites :

- Python 3.9 or newer.
- Equalizer APO.
- Set desired microphone as primary device within Windows.
- Run install.pip.

### Run instructions

1. Run MainMenu.py for the Menu, though other parts of program can also be run standalone.

2. Before running measurement, make sure the headphone is securely placed in a way that the microphone is close to the driver of the headphones.

3. Follow the onscreen instructions for each part of the program.

4. To verify or utilise the output file for the EQ, either upload the measurement + EQ file to a site like Squig.link or apply the EQ file to Equaliser APO.

### Important note :

The current program overwrites the generated APO EQ file with each use of EQ.py. So, keep a copy of the file safe if you are intending to use it in the future.

