# MC-CPU-Compiler
A Compiler for my CPU im building in Minecraft
(And be ready for some terible python code LOL)

# How to Install
1. Downloa source code from GitHub / clone from GitHub
2. Make sure python 3.11 is installed
3. Install pipenv package globally `pip install pipenv`
4. cd into the project folder and run `pipenv install`

### Alternative No Global pipenv package

1. Downloa source code from GitHub / clone from GitHub
2. Make sure python 3.11 is installed
3. cd into the project folder and create a python venv using 3.11 `python -m venv ./venv`
4. Activate the venv `./venv/bin/activate`
5. Install pipenv `pip install pipenv`
6. Install the packages `pipenv install`

# Current Compiler Specs
- auto Memory asignment / variable names
- Macros & Compiletime evaluated Macro Generators

# Syntax (Short), Full see Wiki
## Memory Layout
```c++
#memorylayout [static, static auto, explicit] + [incremental, balanced]
```
### Adress / Variable Declaration
- *static*: define each variable manuel
- *static auto*: automaticly find all variables at compiletime
- *explicit*: no variables, you direcly use memory adresses (no incremental / balanced required)

### Adress balancing
- *incremental*: variables will be resolved from lowest to highest adress
- *balanced*: variables will be resolved to addresses spreded over all 8 RAM segments
