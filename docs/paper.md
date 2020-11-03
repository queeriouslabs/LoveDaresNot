# lovedaresnot: a simple anonymous consensus protocol

> The core idea was that radical or difficult ideas were held back by the
> thought that no one else had them. That fear of isolation led people to stay
> "in the closet" about their ideas, making them the "love that dares not speak
> its name." So lovedaresnot (shortened to "Dare Snot") gave you a way to find
> out if anyone else felt the same, without forcing you to out yourself.
>
> Anyone could put a question -- a Snot Dare -- up, like "Do you think we should
> turf that sexist asshole?" People who secretly agreed signed the question with
> a one-time key that they didn't have to reveal unless a pre-specified number
> of votes were on the record. Then the system broadcast a message telling
> signers to come back with their signing keys and de-anonymize themselves,
> escrowing the results until a critical mass of signers had de-cloaked. Quick
> as you could say "I am Spartacus," a consensus plopped out of the system.”

Scifi author Cory Doctorow's novel Walkaway depicts an interesting possible
future, with many fantastic, but plausible-sounding, technological advances.
One such piece of technology is lovedaresnot, a cryptographic protocol for
running an anonymous consensus poll intended to make it easier for people to
come to decisions by allowing them to more easily express their inner desires
without fear of being the only person who wants to do the thing in question.

Below, I'm going to present a simple protocol for doing just that. While it
doesn't quite match the description that Doctorow gives of the rough details of
the protocol, I believe it successfully achieves the _spirit_ of the tool that
he describes. This spirit, as I see it, is captured by a number of essential
properties.

Much thanks to Avi Zajac, Slug Monk, and Isis Lovecruft for discussing this problem with me, and for giving me feedback on the design of the protocol.

## Defining the Problem

Before presenting the protocol, it's useful to define the problem. In
particular, I should say precisely what the protocol should produce as poll
results, and what the properties are that we want the system to have.

As this is supposed to be some form of consensus protocol, the intention is to
be able to put forth a proposal for action, a snot dare, typically in the form
of a question, to which there are two valid responses. In question form, we
might think of it as being "should we do ...?", or "Do you think we should
do ...?", wherein the most important response for counting purposes is a "no".
As a more traditional consensus process, we can imagine asking if anyone wishes
to block a proposed course of action, wherein the most important response for
counting purposes is a "yes".

I will name these two responses `consense` and `block`, after the traditional
terms used for consensus processes, and attach further meaning to each below.

A proper Dare Snot protocol requires that we also satisfy some properties:

1. Asymmetric Anonymity: anyone who responds `block` is unable to know who
   responded `consense`

2. Deanonymizability: the identity of anyone who responses `consense` can be
   revealed to other people who respond `consense`

3. Thresholding: no information about identities is revealed unless a
   predetermined but arbitrary number of participants responds `consense`

The protocol I will outline below satisfies these, as well as another property,
namely that people who respond `block` cannot know if a consensus was reached,
nor even if anyone responded `consense`. However, I don't consider this to be a
criterion for success.

## The Core Protocol

The core protocol is fundamentally quite simple. In fact, there is a whole
family of protocols with small details changed. I'll present the version that I
find easiest to rap my head around, and then describe the general form. We shall
start with a true consensus process, that is, a process for determining
if there is unanimous `consense` response.

For future proofed naming purposes, this protocol should be referred to as the
basic lovedaresnot protocol, as I expect there are better and more sophisticated
cryptographic techniques that can be used to make better lovedaresnot protocols.

### Setup

A unanimous consensus round requires a set of participants
`P = {p_0, p_1, ..., p_n}`, for examples we'll use `n = 4` and name our
participants `a`, `b`, `c`, and `d` for ease of reference. We also need a means
for each pair of participants to communicated privately. For instance, an
`https` connection, or encrypted email, or physical presence so they can pass
messages back and forth by hand. We of course also need a snot dare, which has
somehow been transmitted to the participants.

### Protocol

Let's suppose that our participants each have decided how they wish to respond
to the snot dare. Let's say `a` and `b` want to respond `consense`, while `c`
and `d` want to respond `block`. Each of the `n` participants generates `n`
random numbers integer values (so in this case each participant generates 4
values), subject to the following constraint: if a participant wishes to respond
`consense`, then their numbers sum to 0, and if they wish to respond `block`,
then their numbers sum to a positive number. Each participant then distributes
one of their numbers to each of the participants in the process (including
themselves), using the secure communication method. They need not do that for
themselves, of course, they can simply reserve one number and send out the rest.

Each participant has therefore distributed `n` numbers, and we can indicate
these with useful names, such as `x_{p1,p2}` for the number that `p1` sends to
`p2`, or in our example set of four, `x_{a,b}` for the number that `a` sends to
`b`. Before proceeding, let's generate some numbers. `a` and `b` want to respond
with `consense`, so they must have numbers that sum to 0. Likewise, `c` and `d`
must have numbers that sum to a positive integer. Here are some such numbers:

```
x_{a,a} = -20
x_{a,b} = 3
x_{a,c} = 19
x_{a,d} = -42
x_{b,a} = -451
x_{b,b} = -359
x_{b,c} = 2
x_{b,d} = 90
x_{c,a} = -23
x_{c,b} = 1000
x_{c,c} = 12
x_{c,d} = -777
x_{d,a} = 111
x_{d,b} = 222
x_{d,c} = 333
x_{d,d} = 444
```

It's convenient at this point to point out that we can write these as a table,
with the sender on the left, and receive on the top:

```
   |   a   |   b   |   c   |   d   |
---+-------+-------+-------+-------+
 a |  -20  |   3   |   19  |  -43  |
---+-------+-------+-------+-------+
 b | -451  | -359  |   2   |   90  |
---+-------+-------+-------+-------+
 c |  -23  | 1000  |   12  | -777  |
---+-------+-------+-------+-------+
 d |  111  |  222  |  333  |  444  |
---+-------+-------+-------+-------+
```

By summing across the rows, we can see that the sums do come out as desired.

Continuing with the protocol, each participant has distributed their numbers to
the others as required. Each participant then has now received 4 numbers. They
then sum together the numbers that they've received. Using the tabular form, we
can do this by summing the columns:

```
   |   a   |   b   |   c   |   d   |
---+-------+-------+-------+-------+
 a |  -20  |   3   |   19  |  -43  |
---+-------+-------+-------+-------+
 b | -451  | -359  |   2   |   90  |
---+-------+-------+-------+-------+
 c |  -23  | 1000  |   12  | -777  |
---+-------+-------+-------+-------+
 d |  111  |  222  |  333  |  444  |
---+-------+-------+-------+-------+
   | -383  |  866  |  366  | -286  |
```

Each participant then announces to all other participants what that sum is. So,
`a` announces that the numbers they received summed to -383, `b` announces their
numbers summed to 866, `c` announces 366, and `d` announces -286. Each
participant can now sum together those announced numbers to produce a final sum:
-383 + 866 + 366 + -286 = 563. If this final sum is 0, then everyone responded
`consense`, but if it's greater than 0, at least one person blocked.

This final summing step explains why earlier the numbers must sum to a positive
integer: if negative integers were allowed, you could accidentally have two
participants who both want to respond with `block`, but whose numbers cancel
each other out (e.g. if one chooses numbers that sum to 1 and the other chooses
numbers that sum to -1).

This then is the protocol. Each participant picks some random numbers subject to
the constraints that encode their respective responses, secretly distributes
them to the other participants, sums up all the numbers they individually
received, publicly announces that sum, and then sums up the publicly announced
numbers to determine the outcome of either everyone consensing, or some
participants blocking.

This works because the order of the summing has no affect on the end result, so
we can sum by rows first (to get each participant's response) and then sum those
up (to get the final result), or by summing the columns (the numbers each
participant received) and then summing those.

### Properties

Let's now discuss how this protocol satisfies the three properties listed
earlier.

#### Asymmetric Anonymity

If there is consensus, this can only occur if everyone responded with a
`consense` response, and therefore all the participants know that they each said
`consense`. But if there is any non-zero number of `block` responses, then there
is no way to tell who responded with `consense`, because every participant has
a number that they shared only with themselves. If all of their other numbers
were to be revealed somehow, it doesn't matter, because the number they kept
secret is unknown to anyone else, and therefore they can reveal any number they
want, the real one or a lie, and no one can tell if its a lie.

If other participants collaborated to reveal all of the numbers they received,
and sent, there would still only be partial information, and there are
infinitely many choices for the remaining integers that produce exactly the same
result that was found in the final sum. As a consequence the consensing
responses could have been from anyone of the non-collaborating participants, or
none of them.

In the unlikely scenario that every participant except one collaborates to
reveal the final participants response, there is still no way to tell if the
final participant is lying or not. The collaborating group is merely able to be
convinced of it in virtue of their trust in one another, but trust is not proof.

At any point where participants begin to try to reveal the responses of others,
social bonds have already broken down to the point where consensus processes no
longer matter. It's unlikely that Dare Snot would ever have been used in such a
distrusting and hostile situation to begin with.

It is worth noting that there is a single situation in which a blocking
participant can be highly confident that no one else blocked: when the final sum
is equal to their own individual sum. This would happen when they block, and
thus generate numbers that sum to non-zero, but everyone else generates numbers
that sum to zero because they consense. In this case, the blocker can be
confident, but not _certain_, that no one else blocked. If there is more than
one blocker, then there is no way to have any confidence in how many others
there are.

#### Deanonymizability

As mentioned above, the participants who consense all know who else consensed,
and thus are no longer anonymous to each other. We shall see later how this
interacts with non-unanimous thresholds in more interesting ways.

#### Thresholding

In a unanimous consensus round, there is a fixed threshold of all participants
consensing, and so in a trivial sense there is _a_ threshold. But for unanimous
rounds, there isn't an arbitrary threshold like we desire for the full protocol.

## Arbitrary Thresholds

To achieve the arbitrary threshold property that we really want to have, we need
to extend the core protocol. Doing this turns out to be quite simple: if we have
a threshold of `m` participants out of `n` (where `m <= n`), we simply run
unanimous rounds for every `m` sized subset of participants. For example, if we
wanted a threshold of 3 of the 4 participants above, we simply run unanimous
rounds for the groups `P = {a,b,c}`, `P = {a,b,d}`, `P = {a,c,d}`, and
`P = {b,c,d}`. Because in our above example, only two participants, `a` and `b`,
responded with `consense`, there is no subset with three participants that has
consensus. If we lowered the threshold to 2 of 4, then the set `P = {a,b}` will
achieve consensus, but no other set will. In general, all and only those subsets
of size `m` that have unanimous consensus will ever consense, definitionally,
even if more than `m` participants respond with `consense`.

For convenience, participants can pre-compute responses to each of the rounds
that they will have to participate in, and send out batched responses to each
other participant, so that they only ever send a single message to each, but
with all of the required numbers for all of the shared rounds.

### Properties

Let's again turn to the three properties, omitting thresholding as that was
discussed above in the explanation for building this version.

#### Asymmetric Anonymity

Because the arbitrary threshold protocol is layered on top of the core protocol,
each unanimous round exhibits asymmetric anonymity. But in this situation, we
have a more interesting fact: anyone who blocks will _always_ find themselves in
a set with at least one block, no matter how many other sets of people there are
that achieve consensus. Therefore, even if there is consensus, blockers will
never know, because they'll never be in a group that achieved it. How could they
be, if they block!

As before, unanimous-minus-one situations have the possibility of a sole blocker
becoming confident that they're the sole blocker. But in the thresholded setting
there's more confidence that can be gained because of the presence of multiple
rounds that may exhibit the indicative property. The further from unanimity, the
fewer chances there are of this happening and the less confident anyone can be.
This becomes less relevant in the thresholded situation, however, because if
there _is_ consensus up to the threshold, the point is for those people to act
publicly and without fear that they're in the minority anymore. Rather, what has
instead happened is that the hidden truth that people thought was rare turns out
to be overwhelmingly common.

#### Deanonymizability

In this version of the protocol, every participant who responds `consense` will
learn all of the identities of other consensing participants. This occurs
because of two interacting reasons: firstly, if there is any group of sufficient
size to consense, then at least one of the subsets of participants will achieve
consensus and each participant there will know the identities of the other
consensors in that unanimous round. Moreover, if there are more than the
threshold of consensors, each participant will find themselves in a consensing
subset that contains each of the other consensors. Mathematically, the set `C`
of people who respond `consense` is a subset of `P`, and the `m` sized subsets
of `C` -- all of which achieve consensus, and all of which are `m` sized subsets
of `P` and thus are unanimous rounds -- union together to equal `C` itself.

### Efficiency Considerations

As the size of the set `P` grows, the number of subsets of a given size grows
too. If `P` has `n` participants, and the threshold is `m`, then clearly we have
`m choose n` unanimous rounds to run. For moderately sized groups, this number
can be quite large, perhaps even undesirably so. To help with that, the
threshold can be gradually lowered from true unanimity to the actual threshold.
Any time the actual number of consensors is higher then the actual threshold,
consensus will be found at the higher number, with fewer rounds, and the process
can be stopped early. The cumulative work required will but much lower than
using the actual threshold, until the temporary higher threshold is very close
to the actual threshold.

Given that Dare Snot is intended to find high degrees of agreement that might
not normally be known about, higher thresholds are generally desirable anyway,
and that means that in typical use cases, one can expect that thresholds closer
to unanimity, and thus closer to optimal effort, will be chosen.

Dually, if you care only about very small thresholds close to 0 rather than `n`,
you can simply negate the snot dare. Instead of asking "should we do ...", you
can ask "should we NOT do ...". Or, since that sometimes leads to complications
with how people interpret the question, you can simply swap `consense` and
`block` before computing results and run the process with increasingly larger
sets.

## Algebraic Generalization

As previously mentioned, the core protocol relies on the fact that integers can
be summed in arbitrary order without changing the result. More precisely, we
rely on the fact that integer addition is associative and commutative.
Additionally, we rely on there being a negation, so that there are infinitely
many ways to sum to 0. We additionally needed some subset of the integers
excluding 0 to be closed under addition, which lets us distinguish results.

Any set that satisfies these criteria suffices, however, will suffice, including
finite subsets of integers. If participants bound their choices to 32-bit signed
ints, for example, this protocol can be used on most available computer hardware
without much problem.

## Probabilistic Generalization

Some choices of alternative representations may exist which do not satisfy the
algebraic constraints described above, but which probabilistically do. One such
example is to say that the requirement for a `block` response is only that the
sum of your numbers is non-zero. This has the possibility of two `block`
responses cancelling, but for sufficiently large sets of possible values, the
probability of this happening is vanishingly small. For 32-bit signed integers,
it's profoundly tiny.

Another option is to pick bit strings, say 32 bits, and to have the operation be
xor. The condition for a `consense` response is that your bit strings must all
xor to be 0s, and any number of 1s is therefore a `block` response. It is not
impossible for two participants to pick numbers that xor to be the same non-zero
bit strings, and thus the xor of their `block` responses cancel out to
`consense`, but as above, the probability of this happening is extremely small.
In most cases, while some of their respective bit strings will cancel, some will
not, and the end result will still be non-zero.

## But Where Do Snot Dares Come From?

In his description of Dare Snot, Doctorow gives the example question "Do you
think we should turf that sexist asshole?". Suppose that this question were
posed out loud, in the presence of said sexist asshole. That would immediately
make the question proposer a target, and if the sexist asshole is violent, you
might have a problem on your hands. So then, how can controversial snot dares be
proposed in such a way that the proposer doesn't single themselves out for
preemptive attack?

One possibility, which lends itself to all sorts of fun questions of efficiency,
is to simply treat each bit of the message as a thing to consense on, and just
run a _lot_ of unanimous rounds. This ends up being the wrong approach tho.

The right approach is as follows: firstly, the set of consensors `P` is fixed
ahead of time for the purposes of an on-going, long-running interaction. This is
plausible in settings where you wish to use this for community decision making,
unless community membership has extremely high churn. Second, the consensors
periodically answer the question "Does anyone have anything to propose?" via a
unanimous round. Since this is low-risk question to ask, it can be asked by
anyone, and doing it automatically via software reduces the preemptive attack
risk to just the risk of an attack on _anyone_ using the software. We can reduce
the risk further by having each participant's computer ask the question at
randomized times capped at, for instance, an hour since the last time they saw
it being asked.

The third part of the proposal process is that every participant runs a fixed
number of unanimous rounds equal to the maximum message length. Because the
number of rounds is pre-determined, and the participants are fixed, you can run
them all simultaneously and send each other participant only one message with
all the round numbers, instead of running many individual rounds. The rounds are
ordered, one for each bit of the message. Anyone without a message consenses,
and so their message will always be zero. Anyone with a message will block on
some bits, and thus those will be non-zero.

If there is only a single person sending a message, then at the end, the entire
multiround sequence will contain `consense`s and `block`s so as to produce the
bits of their message alone. If, however, multiple people are sending messages
simultaneously, the result will be some random junk, tending towards all 1s. We
thus add a fourth part whenever the message is non-zero: a followup round asking
the question "Was this message unexpected to you?". People with no message to
send will `consense`, indicating that they didn't send the message, as will
anyone who was sending a message that was different from any junk that got
through. If however the message is indeed what someone sent, then they will
`block`, and the group will know that the message was genuine for at least one
participant.

A fifth part must be introduced now to handle the junk possibility. When there
is a collision of simultaneous messages, the participants will know, because the
message will be non-zero and no one will have claimed the message with a `block`
in the following round. We now can begin a process of randomized exponential
backoff. Each participant sending a message will pick a random interval of
proposal rounds to wait before retrying. Each time they collide with someone
else, they will increase the scale of the interval, but still randomize the
precise duration. This makes it extremely unlikely that collisions will occur
indefinitely.

Moreover, as soon as some other participant successfully transmits a message,
all of the other people w/ conflicting messages can reset, and try to send again
the immediate next proposal round. This will tend to reduce the delay unless
there is a very large number of participants that need to say something at all
times.

## Scaling

As the size of the consensor set `P` grows, the complexity of the problem grows,
and it becomes intractable to do normal rounds at scales of thousands or
millions. However, it is possible to scale up in a number of ways. If we wish to
get as accurate a reading on a large population, we can run large numbers of
tractable rounds on random subsets of the population. With sufficiently good
sampling, the results ought to be representative, but I have no evidence that
this actually would work in practice. Experimentation is needed.

Another option is to do a recursive decomposition. Instead of running the whole
population, small tractable groups are run. As more overlap occurs, small groups
of consensing participants will link up into larger groups, not through the Dare
Snot protocol directly, but because the various overlapping groups form webs of
trust, and anyone who is in multiple groups can bridge those groups outside the
protocol.

## Applications and Implications

At a small scale, this tool can be used to make decisions via consensus. But the
more important application of this may be as a tool for solving aspects of the
coordination problem. Briefly, the coordination problem is when a social change
can only happen when a large number of people have to work together and
coordinate their actions. This problem arises for many reasons, but a common one
is simply that the people who want to act to solve the problem do not know that
there are enough other people to do it.

Many things solve that kind of coordination problem, but some, such as events
that gather like minded people, have the same problem of non-anonymity as the
case of the sexist asshole: retaliation. Other ways, such as online forums, have
been quite successful at connecting people, but they tend to be geographically
dispersed. Dare Snot can be used at a local scale, however, and opens up new
possibilities.

For liberation struggles, this can be immensely useful. Queer and kink
communities have historically be underground, at least in modern times, until
some event, such as Stonewall, pushed them out into the open. The underground
nature of it, combined with societal disapproval, means that unless there is a
critical mass, the love that dare not speak its name will forever be silent.
However, there is a downside: oppressive forces can use it just as well. Modern
white supremacist groups in America were underground for quite a long time,
until Donald Trump's bid for presidency, at which point they realized that there
were many others out there just like them. Trump solved the white supremacist
coordination problem by being on national TV. Dare Snot could solve similar
"problems", revealing that a seemingly kind and accepting community is in fact
more dangerous and toxic to a minority who now finds itself in the position of
being surrounded by the enemy but not knowing they're even there.
