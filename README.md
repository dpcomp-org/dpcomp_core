# DpComp Core Setup

## Example Environment

The following environment variables must be set.

```bash
export DPCOMP_CORE=$HOME/Documents/dpcomp_core
export PYTHON_HOME=$HOME/virtualenvs/PyDpcomp
export PYTHONPATH=$PYTHONPATH:$DPCOMP_CORE
export DPCOMP_LOG_PATH=$HOME/logs
export DPCOMP_LOG_LEVEL=DEBUG
export HOSTNAME=
```

Once initialization has been run, the virtual environment can be restored with
the following command.

```bash
source $PYTHON_HOME/bin/activate
```

## Initialization

Be sure to setup the environment (describe above) first. You will need to install 
several packages. The following commands should work for debian systems.

```bash
sudo apt-get install python-virtualenv gfortran liblapack-dev libblas-dev 
sudo apt-get install libpq-dev python-dev libncurses5-dev swig
```

Next, create a virtual environment for python by entering the commands below.

```bash
mkdir $DPCOMP_LOG_PATH
virtualenv $PYTHON_HOME
source $PYTHON_HOME/bin/activate
cd $DPCOMP_CORE
pip install -r resources/requirements.txt
```

Finally, after instantiating the virtualenv, compile the C libraries as follows.

```bash
cd $DPCOMP_CORE/dpcomp_core/monolithic
./setup.sh
```


# Testing

Execute the following in the base of the repository.

```bash
nosetests
```

### A specific module

```bash
nosetests test.system.test_experiment:TestExperiment
```
