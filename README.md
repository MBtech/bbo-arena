# bbo-arena
**Note: This repository is being updated with the latest version of the code to make it easy to use the optimization algorithms tested in our work. Meanwhile if you want to use the data accumulated for this work for your own research, please take a look at the [Data section](#data).**  

Contact: Bilal @ muhammad.bilal@uclouvain.be

This is the accompanying github repository for our research work:

> **Do the Best Cloud Configurations Grow on Trees? An Experimental Evaluation of Black Box Algorithms for Optimizing Cloud Workloads.** </br>
> Muhammad Bilal, Marco Serafini, Marco Canini and Rodrigo Rodrigues. </br>
> Proceedings of the VLDB Endowment, 13(11). </br>

## Data 
We provide two accompanying dataset:
1. Cloud configuration performance dataset ([repo](https://github.com/MBtech/bbo-arena-dataset))
2. Data from optimization runs ([repo](https://github.com/MBtech/bbo-arena-opt-data))

## Evaluation 
The results from our evaluation of the blackbox algorithms will be included in this repository. 
Best hyper-parameter configuration for two workloads and two objection functions in our evaluation are present [here](https://github.com/MBtech/bbo-arena/blob/master/docs/best-hyperparams.md).

For stats and results from the evaluation take a look at the `docs` directory. Plots and logs will be added soon as well. 

All the plots related to the analysis are in `analysis/plots` directory. 

## Installation
Since I have included scout repo as a submodule if you clone this repo use

`git clone --recurse-submodules https://github.com/MBtech/bbo-arena.git`

Make sure you have python 3.5.2 or above installed on your system
If you are on mac make sure that you have xcode tools installed using

`xcode-select --install`


`apt-get install swig` or `brew install swig@3` if you are on mac. Make sure you have swig 3 and not version 4.

`pip install -r requirements`
