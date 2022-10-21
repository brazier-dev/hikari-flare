# Internal

This directory has the tools used to interact with the api. These should not be touched
by the end user.

## handle_response
The file containing the callback called when a interaction is received.

## serde
This files handles the encoding and decoding of python objects to strings.
Objects are encoded and decoded using converters. See `flare/internal.converters`.
