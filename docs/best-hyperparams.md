# Hyper-parameter values 
## Default hyper-parameter values

## Best hyper-parameter values
This document contains the best parameter configurations for the optimization algorithms in different scenarios.

### DS1: Execution Time
|  Algorithm  	| No.  Init Samples 	|   Hyper-params  	|
|:-----------:	|:-----------------:	|:---------------:	|
| SHC         	| 9                 	| T=500           	|
| SA          	| 9                 	| T=50, alpha=0.9 	|
| TPE         	| 9                 	| gamma=0.1       	|
| BO(ET-PI)   	| 3                 	| xi=0.1          	|
| BO(GBRT-PI) 	| 3                 	| xi=0.05         	|
| BO(GP-EI)   	| 6                 	| xi=0.2          	|
| BO(RF-PI)   	| 3                 	| xi=0.2          	|


### DS1: Execution Cost
|  Algorithm  	| No.  Init Samples 	|   Hyper-params  	|
|:-----------:	|:-----------------:	|:---------------:	|
| SHC         	| 9                 	| T=50            	|
| SA          	| 9                 	| T=50, alpha=0.5 	|
| TPE         	| 9                 	| gamma=0.1       	|
| BO(ET-LCB)  	| 9                 	| kappa=1.0       	|
| BO(GBRT-PI) 	| 3                 	| xi=0.01         	|
| BO(GP-EI)   	| 3                 	| xi=0.01         	|
| BO(RF-LCB)  	| 6                 	| kappa=1.0       	|


### DS2: Execution Time
|  Algorithm  	| No.  Init Samples 	|   Hyper-params  	|
|:-----------:	|:-----------------:	|:---------------:	|
| SHC         	| 9                 	| T=500           	|
| SA          	| 6                 	| T=50, alpha=0.5 	|
| TPE         	| 9                 	| gamma=0.4       	|
| BO(ET-PI)   	| 3                 	| xi=0.1          	|
| BO(GBRT-PI) 	| 3                 	| xi=0.05         	|
| BO(GP-PI)   	| 3                 	| xi=0.01         	|
| BO(RF-PI)   	| 3                 	| xi=0.2          	|


### DS2: Execution Cost 
|   Algorithm  	| No.  Init Samples 	|   Hyper-params   	|
|:------------:	|:-----------------:	|:----------------:	|
| SHC          	| 9                 	| T=100            	|
| SA           	| 3                 	| T=100, alpha=0.5 	|
| TPE          	| 6                 	| gamma=0.25       	|
| BO(ET-LCB)   	| 6                 	| kappa=1.0        	|
| BO(GBRT-LCB) 	| 9                 	| kappa=1.5        	|
| BO(GP-LCB)   	| 3                 	| kappa=1.0        	|
| BO(RF-LCB)   	| 9                 	| kappa=1.0        	|