# MC-CPU-Compiler
A Compiler for my CPU im building in Minecraft
(And be ready for some terible python code LOL)

# Current CPU Specs
- 8 bit CPU (math, adress buss, ...)
- 256 bytes RAM (8 32 byte segments)
- 256 instructions ROM (each instruction is 3 bytes (operant, arg1, arg2) = 768 bytes ROM on 256 addresses)


# Current Compiler Specs
- auto Memory asignment / variable names

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
