# Simulations for Car2Car communication

This project contains code to simulate the behaviour of two platooning cars. 
Plotting and evaluation is implemented to gather information on the performance to keep a stable distance between two cars.
A sensor based model and three Car2Car communication models are implemented.

## Code

### Common
Contains classes that are used in the different Models. 
Furthermore contains this package helper functions for the evaluation and plotting.

### Models
Implementations of the four communication models. Each implementation 
consists of the definitions of the Leader, Follower and a model class 
that defines how the Model is initialized and run.

### Simulations
Each Simulation is a main method that defines which models are run with which configuration of delay, noise values.
The Sim class is used to run multiple methods in parallel. 
Each Simulation contains also the code to plot the values of interest.
Some of the longer running Simulations contain caching code to write / read the models to / from disk. The files can be 
found under *cache/* and are named by source filename and the configuration.

## Dependencies: 
- matplotlib
- numpy