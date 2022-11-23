# TO DO

## Components

### `Table` class

#### TODO:
- longtable

### `Figure` class

#### TODO:

- subfigures... This will be a pain


## General

- Add some sort of caching
    - take some has of each code block, save along with the output to some hidden file
        - Is it even worth taking a hash? Hidden file could become large for big documents, but surely not concerningly large.
    - Re-use output from cache (especially figures!) for each code block up to the first change - assume that after this change, the output will be different
        - could maybe do some clever tracking on each change to connect blocks together, but this is probably not worth it
- Subfigures
- Expand components to generic environments
    - base class with
        - environment name
        - content (list of strings or other components)
        - list of arguments
            - each argument can be a string, dictionary, or a list of strings and dictionaries
            - need some way to specify which arguments are optional, and the order.
- Some way to recognise verbatim blocks and not try to run them
    - Similar loop to extract code blocks, replacing verbatim with an ID and storing original verbatim
    - Then run normal code block processing loop
    - Then replace IDs with original verbatim
    - inline macros:
        - `\veb`
        - `\lstinline`
        - `\qoinline`
    - Environments:
        - `\begin{verbatim}`
        - `\begin{lstlisting}`
        - `\begin{qolisting}`

- Some way to place the original code block in the output, formatted nicely?
    - maybe add a variable to each code block which is the original code, and allow a user to handle this in the output
- `itemize`/`enumerate` components
- add support for parsing markdown with pandoc?
    - requires pandoc to be installed, \textbf{and} the pandoc python package. Could get very complicated with mixing markdown and latex.
    - Alternative; just implement basics, like bold, italics, lists, inline code, sections etc.
    - Should be able to avoid accidentally parsing non-markdown text as markdown since it will need to be in a `\begin{markdown}...\end{markdown}` environment
- Some toggle for using QoLaTeX packages?


## KWArgs

- Has `KWArgs.value`, which is a dict.
    - `key`s are strings, `value`s are strings or `Arg`s (*not* `KWArgs`)
- Converting to string: 
    - `f"{key} = {{{value}}}" for key, value in self.value.items()`

## Arg

- Each instance of `Arg` should be one argument, i.e. a single token which would be passed inside curly braces
- For most things, a string would be sufficient. Some things would take a list of options, some things would take a list of options and key-value pairs, where order will matter.
- `Arg.value` should *always* be a list, containing either strings or `KWArgs` instances
- When converting to string, each element of the list can just be converted to a string, and then joined with commas, and returned inside curly braces

## OptArg

- Identical to `Arg`, but with square brackets instead of curly braces

## Macro

- `Macro` has a name and list of arguments. Could even inherit from Environment (or vice versa)
- printed as `\name{arg1}{arg2}...`
