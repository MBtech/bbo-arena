# bbo-arena

## Blackbox optimization algorithms (under test)
- SMAC -> There is a problem with SMAC on MacOS
- CMA-ES -> CMA-ES doesn't seem to have bounds on the search space and it is designed completely for a continuous search space
- GpyOpt


## Installation
Since I have included scout repo as a submodule if you clone this repo use

`git clone --recurse-submodules https://github.com/MBtech/bbo-arena.git`

Make sure you have python 3.5.2 or above installed on your system
If you are on mac make sure that you have xcode tools installed using

`xcode-select --install`

Make sure you have swig 3 and not version 4.
`apt-get install swig` or `brew install swig@3` if you are on mac
`pip install cython`
`pip install smac[all] cma gpyopt`
