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

The inter-consensor communication happens via endpoints under the `/api`
path, while the local endpoints are directly under `/`.

## Usage

The use of the app is separated into three main stages.

The first stage involves setting up a group of consensors who are participating
in the consensus process. This establishes an on going automatic multiround
process that makes it possible for the consensors to propose consensus items.
The second stage involves proposing consensus items. The third state involves
voting on those items.

### Stage 1: Setup

In stage 1, the IP addresses of the consensors are entered into the setup form
by the person managing the consensus process. They submit the form, and their
computer communicates with the IP addresses and establishes a consensus process
among them.

### Stage 2: Snot Dares

In stage 2, which can be repeated arbitrarily many times, a consensus item is
proposed. The consensus item is entered into the New Snot Dare form, and on
submitting it, it is then sent to the other participants via the automatic
multiround process.

### Stage 3: voting

In stage 3, a consensus item is voted on by the consensors. When a consensor
gives their vote, it is appropriately decomposed into the relevant data to send
to the other consensors and then sent. When consensors receive data, they
combine it with what they already have, and whenever all of the consensors' data
has been received, the consensor sends a message with the apparent consensus
result.

## Software Components

The software is broken into three main components:

1. the server, which manages the UIs and the API
2. the protocol interface, which provides a concrete interface to running
   the protocol in a way abstracted from the particular substrate, transport
   mechanism, UI, etc.
3. the round algorithms, which provides a protocol-independent means to compute
   the individual pieces of information such as whether or not there is
   consensus and what the content of a consensus item is.

The third component, the round algorithms, are precisely those components of the
protocol which do not rely on the act of communication, and which therefore
constitute the mathematical core of the protocol. The protocol interface
therefore simply composes the round algorithms together in appropriate ways as
part of a communicative process, and does not itself contain any real protocol
logic outside of structuring the communication.
