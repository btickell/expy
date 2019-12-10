This is a lightweight experiment tracker built as a wrapper package of 
[`ml-logger'](https://github.com/episodeyang/ml_logger) by [episodeyang](https://github.com/episodeyang)

This is designed to allow multiple runs within one experiment launch, an especially helpful structure when running many tests in parallel for hyperparameter tuning or testing of result variation. This will be extended to run on cloud computing resources as well as locally by allowing remote serving (throughn ml-logger and some added mongo utility).

## Usage:

First set important environment variables:
```
export PROJECT_ROOT=<path/to/project>
export LOG_ROOT=<path/to/target/dir>
```
Next in your python script import expy:

`from expy import tracker`

In your experiment launch script

`tracker.make_experiment(EXPERIMENT_NAME)`

Creates an experiment directory at location PROJECT_ROOT/EXPERIMENT_NAME

Then start a run of your experiment:

`exp_logger = tracker.start_run(EXPERIMENT_NAME, params=param_dict)`

The `start_run` method creates a run with a random ID inside the experiment directory and logs the run to a mongoDB. It also returns an `ml-logger` logger object which can be used to log relevant metrics and files and follows the ml-logge.

## Commandline Interface:
Additionally, expy has a console entrypoint `tracker`.

### annotation
  
  *`tracker note add <expID>` allows user to add notes on the given experiment using a command line editor saved to `path/to/experiment/notes.txt`
  
  *`tracker note read <expID>` displays the contents of `/path/to/experiment/notes.txt`
