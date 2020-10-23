# LoveDaresNot

An implementation of a protocol for Cory Doctorow's LoveDaresNot

CAUTION: This is a PROTOTYPE and a DEMONSTRATION. This software should NOT be
used for actual anonymous consensus processes and should be assumed to be
vulnerable to all sorts of unknown attacks, both to the software itself and to
the protocols it uses. Its purpose is to facilitate a conversation about the
protocols and to provide a baseline of functionality for others to replicate in
actually secure software.

## Overview

This implementation of LoveDaresNot is a simple Flask-based web app that is
expected to be run reverse proxied through an HTTPS server such as Caddy. It
assumes that all connections are secure and encrypted, and therefore does not
perform any actual encryption itself.

The app presents a locally accessible web UI which the user can use to perform
single round yes/no rating of consensus items that have been proposed external
to the program.

The software also provides an automatic multiround system for communicating
consensus items to the participants in a fully anonymous way layered on top of
the single round protocol.

This implementation does not provide any sort of identity management tools: the
only way to establish a set of consensors is by manually providing the list of
IP addresses for the consensors. Each consensor is then contacted and either a
single round consensus is set up, or a multi-round listener is set up.
