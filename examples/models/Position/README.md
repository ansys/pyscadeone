# Position example

The Position example illustrates the use of *fork* in transitions.

The commands `(u)p`, `(d)own`, `(l)eft`, and `(r)ight` can be activated only when the `unlock` signal is true. The position (`x`, `y`) is updated according to the active commands.

If `(c)enter` is set, the position is reset to `(0,0)`. 

If `unlock` and `(c)enter` are set simultaneously, `unlock` has the priority.

 