Help me plan a simple python engine/API for terminal (text-mode) based arcade games, to teach kids programming. 

The engine will enable creating classics like pong, snake, rogue, sokoban, tetris ... 

It will leverage modern terminal capabilities, such as colors and emoji (for simple "sprites").

Because one important goal of this framework is to teach programming, the 
- it must be very simple and get out of the way as much as possible
- there will be two flavors of the API: 
    1. class-based
    2. function-based    
    Students might start with the function-based API if they are very new to programming, then graduate to using the class-based api.

The engine will function as follows:
- There is a display loop as follows:
    * the loop runs at an optional fixed fps or at max refresh (fps=None).
    * The display is entirely redrawn at every loop
    * Primitives are provided to place characters at integer coordinates
    * The game developer needs to provide the inner part of the display loop, which uses the primites to draw the entire display from a blank state
    * display size is configurable
    * as mentioned before, color and emoji are supported, as well as ascii line drawing characters

Input will be handled between updates. Similar to the display loop, a single handler will be written to handle all input. 

The coder will write the actual game loop themselves. A typical loop would look like :

```
while main_loop:

    get_input(...)
    update_state(...)
    draw_screen(...)
```

Please help me plan this engine / API.

Write the detailed plan in `spec.md`.