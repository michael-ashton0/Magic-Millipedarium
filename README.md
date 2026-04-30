# Magic Millipedarium
Code for a museum exhibit to showcase the bioluminescence of magic millipedes (Motyxia sequoiae) enhanced by uv light.

Controlled via rpi pico or rpi 4

# System Architecture

The system is a psuedo state machine, where state changes based on functions.

It implements a small collection of dfplayer mini functions, several of which were written by chatGPT

Writes to a file for each narration cycle ran to keep track of attendance numbers in the exhibit

# Key Components

DFPlayer mini - Audio module
Microcontroller - Rpi Pico or Pi 4; attached labeled files for each

# Getting Started

Pico - Flash pico with pico.py, should run automatically

Pi 4 - Load pi4.py onto the device, then run `python pi4.py`

    - Program utilizes the gpiozero library, install via `pip install gpiozero` or your preferred package manager

# Design notes

The pseudo state machine was selected for micropythons lack of match-case support, so functions are instead used to alter states.

The pi4 was written according to the same design for consistency and ease of maintenance.

Timing variables can be altered in the top of each file.