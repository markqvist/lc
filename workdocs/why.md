There comes a moment, usually while watching your third Docker container fail to start, monkey-patching TypeScript directly in `node_modules`, or waiting for a package manager to resolve 581 dependencies you never asked for, when you recognize that your relationship with the machine has become unnecessarily ritualistic, deferred to "higher powers" of inscrutable dimensions (if more than half a million lines of code isn't, what is?), and somehow, through the wild goose-chase of reading make-pretend "documentation", now sits in stark contrast to the very reason you started installing this thing anyway.

Up until very recently, we were bound to spend decades learning the dialects the computer prefers, constructing elaborate incantations for tasks we could have described in plain language in the timespan between blinking our eyes. I should know; I've spent half a lifetime doing exactly that.

The current fashion for "AI agents" has now, with a promise of the opposite, merely relocated this theater to endlessly over-engineered "products", distant data centers (where requests - *everything* "your" agent does - are processed, logged, and monetized by entities whose interests run orthogonal to your own) and the sunk cost of *getting the darned framework to work reliably*.

If you don't see a slight shimmer of farcical irony in this, you should probably just stop reading now.

Against this, consider *if* you could just obtain something smaller than a cat GIF, install it with one command, and possess a fully capable agent in around 15 seconds, that actually *works*.

No orchestration frameworks stacking like geological strata. No configuration novellas. No Terms of Service drafted by committees in languages that require legal exegesis.

A scalpel does not require the mass of a claymore to cut precisely, and competence does not scale in proportion to dependency bloat, though it seems everyone and their aunt has spent the last few years attempting to convince us otherwise: Layering abstraction upon abstraction until the original purpose disappears beneath the ridiculous weight of the infrastructure meant to "support" it.

Contrasts like these have a tendency to grind me a bit, and in the end, I usually just wear down, give up and do *something*. Not necessarily something *perfect*, mind you, but something that's at least *better* in the fundamental domains that I care about.

This also means that it's going to land dead-center in the "I don't get it" category for the 95%. That's the point. It's not *meant* to be everything. It's meant to be *one* thing, that (conversely) *does anything*.

Is that some kind of statement? Maybe. Is it sarcasm? Yes, but probably, it's also the most functional piece of sarcasm you've ever seen.

In reality, the result of this is laughingly simple. The codebase for `lc` - Humanity's Last Command - is 0.5% the size of what we've come to expect of systems like this.

Because that's really all you need: The absolute *minimal* surface layer that provides an interface between the machine, and *machine intelligence*. Once that loop is complete, you just speak the rest.

The point was to *give yourself autonomy*, right?
