![rich-pyfiglet-banner](https://github.com/user-attachments/assets/b16667f2-4428-4bf5-aad5-5832b5b5da3d)

# Rich-Pyfiglet

![badge](https://img.shields.io/badge/linted-Ruff-blue?style=for-the-badge&logo=ruff)
![badge](https://img.shields.io/badge/formatted-black-black?style=for-the-badge)
![badge](https://img.shields.io/badge/type_checked-MyPy-blue?style=for-the-badge&logo=python)
![badge](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

Rich-PyFiglet is an implementation of [PyFiglet](https://github.com/pwaller/pyfiglet) for [Rich](https://github.com/Textualize/rich).

It provides a RichFiglet class that is fully compatible with the Rich API and can be dropped into your Rich scripts.

*This library is the sister library of [Textual-Pyfiglet](https://github.com/edward-jazzhands/textual-pyfiglet).*

## Features

- Usage in your Rich scripts can be a single line of code with default settings.
- Color system built on Rich can take common formats such as hex code and RGB, as well as a big list of named colors
- Automatically create gradients between colors vertically or horizontally.
- Comes with 4 animation modes built in (up, down, smooth-strobe, fast-strobe).
- Pass in a list of colors for multicolored gradients and animations.
- Manually tweak the gradient quality as well as the animation FPS in order to customize the banner the way you want it.
- Add borders around the banner - The RichFiglet takes border settings as arguments, which allows it to properly account for the border and padding when calculating its available space (without doing this, some terminal sizes would mess up the render)
- Included CLI mode for quick testing.
- The fonts are type-hinted to give you auto-completion in your code editor, eliminating the need to manually
check what fonts are available.

## Try out the CLI

If you have uv or Pipx, you can immediately try out the included CLI:

```sh
uvx rich-pyfiglet "Rich is awesome" --colors green3:purple -a gradient_down
```

or using pipx:

```sh
pipx rich-pyfiglet "Rich is awesome" --colors blue1:magenta3 -h
```

## Documentation

### [Click here for documentation](https://edward-jazzhands.github.io/libraries/rich-pyfiglet/)

## Questions, issues, suggestions?

Feel free to post an issue.

## Thanks and Copyright

Both Rich-Pyfiglet and the original PyFiglet are under MIT License. See LICENSE file.

FIGlet fonts have existed for a long time, and many people have contributed over the years.

Original creators of FIGlet:  
[https://www.figlet.org](https://www.figlet.org)

The PyFiglet creators:  
[https://github.com/pwaller/pyfiglet](https://github.com/pwaller/pyfiglet)

Rich:  
[https://github.com/Textualize/rich](https://github.com/Textualize/rich)

And finally, thanks to the many hundreds of people that contributed to the fonts collection.
