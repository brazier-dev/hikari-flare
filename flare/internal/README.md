# Internal

This directory has the tools used to interact with the api. These should not be touched
by the end user.

## attrs
Contains global information for `flare`.

## event_handler

The file containing the callback called when a interaction is received.

## serde

This file handles the encoding and decoding of python objects to strings.
Objects are encoded and decoded using converters. See `flare/internal.converters`.
