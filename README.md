# QuantumPlayground
Homebrew Molecular Geometry Optimisation

## Installation

Install Python 3
https://www.python.org/downloads/

Make a python virtual environment to contain all the project's packages

```
cd C:/
mkdir pyvenv
cd pyvenv
python -m venv QuantumPlayground
cd QuantumPlayground
cd Scripts
activate.bat
```

Download QuantumPlayground source and put it somewhere accessible for you eg. Documents, or dedicated Python folder
If you don't want to use `git`, download zip here: https://github.com/not-matt/QuantumPlayground/archive/main.zip then put this in the MyPython folder

```
mkdir MyPython
cd MyPython
git clone https://github.com/not-matt/QuantumPlayground 
```

Once you have the source downloaded and somewhere you're happy with, cd into the source folder

```
cd QuantumPlayground
```

Run the setup.py script to install all the project's dependencies to the python environment (C:/pyvenv/QuantumPlayground..)
This will take a little while

```
python setup.py develop
```

Manually install pywin32

```
pip install pywin32
python C:\pyvenv\QuantumPlayground\Scripts\pywin32_postinstall.py
```

Optional test: pop open the notebook for an interactive environment

```
jupyter notebook ethane.ipynb
```

If that works, close it, as we now need to install chemview manually. 
The chemview package is no longer maintained and needs some tinkering to get it to work
This is a pain in the ass. NPM is requried for the manual build. You can uninstall it afterwards. 
https://www.npmjs.com/get-npm
If you made it here, give yourself a pat on the back and get a cup of tea. You'll need it.

```
cd C:/pyvenv/QuantumPlayground
git clone https://github.com/gabrielelanaro/chemview
cd chemview
```

If you're on windows: open setup.py and change the following lines:

```
line 81 TO: check_call(['npm', '--version'], shell=True)
```

Back to prompt, time to buld the package using npm. 

```
cd js 
npm install
```

Now to install our modified chemview package

```
cd ..
pip install .
```

Install chemview as a package jupyter can use

```
cd ..
pip uninstall ipywidgets
pip install ipywidgets
jupyter nbextension enable --py --user widgetsnbextension
jupyter nbextension install --symlink chemview
jupyter nbextension enable --user chemview
```

Go to the project github source foler we downloaded (eg. ...\MyPython\QuantumPlayground)
Pop open the notebook and run all the cells, you should see a molecule at the end!

```
jupyter notebook ethane.ipynb
```

![image](https://user-images.githubusercontent.com/32398028/109663274-d296a980-7b63-11eb-807e-717a041cccd2.png)
