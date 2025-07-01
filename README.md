# silver-nitrate

This is a collection of Python utilities used by [the Flickr Foundation](https://www.flickr.org/).
It allows us to share certain functions and common code across all our projects.

Think of it as a souped-up version of `utils.py`.

This library is primarily for our use, but the code is fairly generic and may well be useful in other projects.
If you want to use it, copy/paste the code (and the associated tests!) into your own project rather than adding a dependency on this library.

<figure>
  <a href="https://www.flickr.com/photos/podsville/3912488857">
    <img src="https://live.staticflickr.com/3438/3912488857_78a5103b69_c_d.jpg">
  </a>
  <figcaption>
    <em>Builder's Photo of 2-8-0 Locomotive No 1402 "James Archbald," built in 1930 by the Delaware & Hudson Railroad.</em>
    Scan of a silver-halide photo print.
    Photo from Bill Harrison <a href="https://www.flickr.com/photos/podsville/3912488857">on Flickr</a>.
  </figcaption>
</figure>

## What's in this library?

This library contains shared functions that are a bit too complicated to copy/paste between different projects.

*   `nitrate.cassettes` -- pytest fixtures for working with vcrpy to record HTTP requests.
*   `nitrate.flickr_login` -- deal with the parts of the Flickr OAuth login process that are the same for every app.
*   `nitrate.json` -- encode/decode JSON in a type-preserving way.
*   `nitrate.mock_passwords` -- a pytest fixture to mock the keyring module.
*   `nitrate.types` -- helpers for validating Python types at runtime.
*   `nitrate.xml` -- type-safe helpers for finding matching elements or text in an XML document.

## Why did you pick this name?

We wanted to pick a name that was:

1.  More interesting than "utils"
2.  Had a connection to photography
3.  Wasn't taken on PyPI

Silver nitrate was a key chemical in the early days of photography, especially in the 19th and early 20th centuries.

Photographers would coat glass plates with a mixture of chemicals, including silver nitrate.
Because silver nitrate reacts when exposed to light, when you put the plate in a camera and open the shutter, different areas would react differently to create an image on the plate.
You could then develop this plate into a photograph.

This code is key to our work at the Flickr Foundation, so it's a fitting name.

## Development

If you want to make changes to the library, there are instructions in [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

This project is dual-licensed as Apache-2.0 and MIT.
