# man workflow for Alfred

A workflow for [Alfred](http://www.alfredapp.com/) to rapidly open UNIX man pages in any of traditional Terminal, HTML or PDF format.

![Example 1](https://raw.github.com/isometry/alfred-man/master/screenshots/man_example1.png)

![Example 2](https://raw.github.com/isometry/alfred-man/master/screenshots/man_example2.png)

## Releases

- [v1.1 for Alfred 2.4+](https://github.com/isometry/alfred-man/releases/tag/v1.1)
- [v2.x for Alfred 3.1+](https://github.com/isometry/alfred-man/releases/latest)

## Requirements

- [Alfred](http://www.alfredapp.com/) (version 3.0+)
- The [Alfred Powerpack](http://www.alfredapp.com/powerpack/).
- Python 3 (`xcode-select --install` or [Homebrew](https://brew.sh/))

## Usage

Type `man` in Alfred, optionally followed by the section to which you wish to restrict search, followed by a glob pattern to match against man page names.

Action modifiers:

- Shift+Enter: open locally rendered HTML man page in default browser.
- Command+Enter: open PDF man page in default PDF viewer.

## Contributions & Thanks

- [Sebastian](http://www.alfredforum.com/user/145-sebastian/)
