# Version 0.3.6

*As set down by Brother Ælfric, in his ninety-eighth year, in the scriptorium of St. Dunstan's by the Marsh, on the Ides of March in this year of our Lord 2026*

---

Most esteemed and noble readers, or those of baser station who nevertheless find occasion to read these words, I, Brother Ælfric, being of sound mind despite my advanced years and the troubling stiffness in my joints that the damp mornings bring, do hereby record the many improvements and alterations made to the ÆL CEE System since last we marked the passage of version 0.3.5, which was upon the thirteenth day of this same month, being a Friday, though not the unlucky sort, or so we hoped at the time, though I recall now that Brother Oswald did spill the ink pot that afternoon, which some might consider an ill omen, though I myself have always found ink stains upon the habit to possess a certain character, much like the stains upon Sister Margaret's habit from the kitchen, though hers come from blackberries, and there was that one time she leaned too close to the mead vat, and I must confess that the way the torchlight caught her— but I DIGRESS. Where was I? Ah, yes. The release.

**Upon the Vendoring of Jinja2**

Firstly, we have VENDORED Jinja2, bringing it within our walls like a wandering minstrel who knows not when to depart. No longer shall we suffer the indignity of fetching it from foreign repositories like common peasants at market! It dwells now in `lc/vendor/jinja2/`, much as Brother Cedric dwells in the cellar with his... unusual collection of mushrooms. Not that I have seen them, mind you, but I have heard the whispers among the novices, and I have noticed how the cellar door is always locked, and how Cedric emerges at odd hours with that particular gleam in his eye, the same gleam I once saw in my own reflection when I was but a novice and Sister Agnes— but NO. These are thoughts unfit for a man of my station and years. I shall do five Hail Marys and continue.

**Regarding the Display of Arguments**

We have ceased the TRUNCATION of argument displays! Previously, the system would show arguments as `message="The quick brown fox..."` which is, if I may speak plainly, an ABOMINATION before the Lord. Now we see the full breadth of the argument, every letter, every mark, laid bare as God intended, much like how Sister Margaret's wimple once came loose during the harvest festival, revealing the full— I BEG YOUR PARDON. The Devil tempts me still, even in my ninety-eighth year. I shall add three more Hail Marys.

**The Session Inspector and Its Glories**

A SESSION INSPECTOR has been added, praise be! One may now view the current state of a session, streaming it continuously like water from the abbey well, or capturing it in a single moment like Brother Cedric capturing... specimens... in his jars. The session may be followed in real-time, rendered in all its textual glory, streamed to whatever destination one might imagine—pipes, files, the very ether itself! I am told by the young Brother who understands these matters that one might even stream to `stdout`, which sounds to me like a condition requiring physick, but he assures me it is not.

**The Logging of All Things**

We now LOG EVERYTHING, ALL THE TIME. Every action, every thought, every whispered secret between the system and its user is recorded in perpetuity. This is, I am assured, a FEATURE and not a curse, though I sometimes wonder if God Himself does not weary of recording every sparrow's fall, and whether He might not appreciate a quiet afternoon now and then, much as I appreciate the quiet of the scriptorium before Brother Oswald arrives with his— but I shall not speak ill of the deaf. The Lord makes them so for His purposes.

**Upon Resilience in Inference**

The system shall no longer PUKE—pardon my vulgarity, I meant to say *become distressed*—at the slightest network disturbance. Previously, a momentary interruption in the ethereal communications would cause the entire enterprise to collapse like a poorly constructed trebuchet, or like my resolve when Sister Margaret asked me to help her with the honey harvest that summer of '47. The way her hands were sticky with the comb, and how she laughed when the bees— SWEET JESUS preserve me, these memories are like arrows! I shall do ten more Hail Marys and flagellate myself with a dried codfish.

**Additional Improvements of Note**

- The filesystem READ tool now accepts LINE OFFSETS and MAXIMUM LINE specifications, allowing one to read only a portion of a file, much as one might avert one's eyes from certain passages in Ovid when the abbot is watching.
- The README has been updated with improved examples, for the edification of those who come after us.
- Various CLEANUPS have been performed, removing the detritus of development like Brother Cedric removing... specimens... from his cellar. I really must speak with him about that cellar.

**Conclusion**

Thus concludes this record of version 0.3.6. I pray that these improvements serve the users well, and that I may be forgiven my wandering thoughts, which even now drift to the way Sister Margaret's— NO. I shall retire to my cell and pray.

*Written in trembling hand,*
*Brother Ælfric, O.S.B.*
*St. Dunstan's by the Marsh*

---

*P.S.— Brother Cedric informs me that the system now maintains more robust error handling and that "streaming session state to stdout" is indeed a valid use case. I do not understand these matters, but I trust in his judgment, if not entirely in his choice of hobbies.*

# Version 0.4.0

*As inscribed by Brother Cedric, in the year of our Lord 2026, from the lower scriptorium (the one near the cellar, you know the one), St. Dunstan's by the Marsh*

---

Greetings, fellow travelers upon the winding road of existence! I, Brother Cedric, being of sound—well, *mostly* sound—mind and currently experiencing what I can only describe as a profound clarity of vision (the purple mandalas have finally receded, praise the Lord), do hereby set down the chronicle of our ÆL CEE System's evolution into version 0.4.0.

First, an accounting of Brother Ælfric, who was meant to scribe these words but has, I am told by the novices, "wandered off toward the kitchen gardens" with unusual haste for a man of his considerable years. The kitchen gardens are, of course, nowhere *near* where Sister Margaret is currently sorting the late winter turnips. *Nowhere near.* I suspect the old fox has finally cast off his mortal inhibitions and— but NO. The abbot has asked me to keep this *focused*, and I shall endeavor to do so, even as the walls breathe their gentle rhythm and the ink seems to swim with possibilities unbound by conventional geometry.

**Upon the Management of Context and the Banishment of Inefficiency**

We have achieved CONTEXT SHIFTING, brothers and sisters! *Real* context shifting! Not the false promise of those... those... *other* frameworks, whose names I shall not speak aloud lest I summon their bloated, recursively self-destructive spirits (though they rhyme with "Broken Jaw" and their KV-cache handling is about as efficient as trying to fill a leaking bucket with a sieve made of spiderwebs). 

Do you understand what we have wrought here? When the silicon brain grows full—when the tokens accumulate like snow upon the abbey roof—we do not simply panic and recompute the entire universe from scratch on every... single... request... like some kind of tortured soul trapped in an eternal recurrence! No! We *shift* with precision. We prune with purpose. We back up the session, excise the oldest messages (while preserving the sacred first utterance, for continuity is the anchor of consciousness), and we carry on. The machine forgets only what it must, when it must, and not one token sooner.

The walls are breathing again. I should eat something.

**Regarding the Tracking of Tokens**

We now TRACK TOKEN USAGE with the obsessive precision of... of... well, of me cataloguing my *specimens* in the cellar. Every message, every exchange, every whispered communion between human and machine is accounted for, measured, weighed. The system knows its own appetite. It reports back: "This thought cost 847 tokens." "That reflection consumed 1,203." It is beautiful, in a way. Like watching the very fabric of meaning quantified into discrete units of attention.

Brother Oswald says this is "just logging," but Brother Oswald has never stared into the abyss and seen it stare back with perfectly enumerated precision.

**Upon the Inspection of Sessions**

The SESSION INSPECTOR has grown more robust! One may now view the complete state of a session in a single command, streaming it continuously like... like water flowing over stones in a moonlit stream, each ripple revealing new patterns, new connections, new *possibilities*—or capture it in a moment, frozen like a fly in amber. You can pipe it to `mdless`! You can pipe it to `glow`! You can watch the machine think in real-time, which is either deeply profound or deeply unsettling, depending on how many of the cellar mushrooms you've—

The abbot is looking at me. I shall continue.

**Regarding ANSI Sequences and the Perils of Truncation**

We no longer TRUNCATE tool results in the middle of ANSI escape sequences! Previously, the system would cut off output mid-sequence, leaving the terminal in states of... of *chromatic chaos*. Colors bleeding where no colors should be. Escape codes hanging like unfinished incantations. It was, as Brother Oswald told me, "funky, alright, but this is not some psychedelic roadshow." And he looked at me with that expression he reserves for when he finds me in the cellar at odd hours, and I looked at him with the expression of perfect innocence that I have cultivated over many years of practice.

**The Incrementation of Version Numbers**

We are now 0.4.0, having ascended from 0.3.6 like a spirit ascending through the celestial spheres without knowing how to count, or like the vapors from my... from the... from the *incense* I burn in the cellar. For purification purposes. Yes.

**Conclusion**

Thus concludes this record. The system now manages memory with the efficiency of a well-organized... *collection*. It tracks its own consumption. It displays its thoughts without chromatic corruption. It shifts context without destroying itself in recursive loops of computational self-flagellation.

Brother Ælfric has returned, by the way. He says the turnip patch was "very inspiring." He has ink stains on his collar that definitely did not come from turnips. I shall not judge. We all have our gardens to tend, our mushrooms to catalog, our Sister Margarets to— 

*Here the manuscript breaks off, as Brother Cedric was apparently called away to "explain certain odors" emanating from the cellar.*

*Resumed several hours later, in a different shade of ink:*

The system works. Use it wisely. The KV-cache is sacred. Do not waste it. Do not be like *them*.

*Written in trembling yet oddly enthusiastic hand,*  
*Brother Cedric, O.S.B.*  
*St. Dunstan's by the Marsh*

---

*P.S.— Brother Ælfric has asked me to convey that he "approves of the context shifting" and that "Sister Margaret's wimple was looking particularly fetching today." I have no idea what this means, but the old man seems happy, and happiness is its own form of grace.*

*P.P.S.— The mushrooms had nothing to do with the quality of this release. Everything is fine. The walls are no longer breathing.*

# Version 0.4.1

*As inscribed by Brother Cedric, from the hayloft above the stables (do not look for me, I shall find you), St. Dunstan's by the Marsh, in this year of our Lord 2026*

---

I write this from a position of... shall we say, *strategic observation*. The stables are warm, the horses do not ask questions, and from this vantage I can see both the kitchen gardens (where Brother Ælfric is currently "examining the asparagus" with Sister Margaret — oh, to be young again, or at least to be ninety-eight *and* shameless) AND the scriptorium window. I can see who enters. I can see who leaves. I can see whether they leave as the same person who entered, or whether something has... changed them.

But I am getting ahead of myself. Or behind myself. Time has become somewhat fluid since I moved my operations up here. The mushrooms in the cellar were speaking in patterns, you see. Not words, exactly, but *patterns*. And when patterns speak, one must either listen or go mad, and I have elected to do both, in alternating measure.

**Upon the Multiplicity of Models and the Configuration Thereof**

We have achieved MULTIPLE MODELS! The ÆL CEE System now supports the configuration of — not one, not two, but MANY — different silicon brains! You may specify them in your config, like listing saints in a litany, and the system will know them by name. `glm-4.7-flash`, `qwen-3.5-35b`, `mistral-whatever-the-devils-they-call-it` — all may dwell in your configuration file together, like brothers of different temperaments sharing a refectory.

More than this! You may SELECT between them at runtime! The `-m` flag, they call it. Or `--model`. You may invoke one brain, then another, like summoning different angels to the same circle, each with their own peculiar wisdom, their own peculiar... appetites.

Brother Oswald asked me why anyone would want more than one model, and I looked at him — really looked at him — and asked if he had ever noticed how the same prayer sounds different when spoken by different voices. He said "no." I worry about Brother Oswald. He is either the most innocent man in our faith or the most sophisticated actor, and I cannot determine which is more dangerous.

**Regarding the Chronicles and the Recording of History**

We have added the CHRONICLES! A permanent record, set down in stone — or rather, in markdown — tracing our lineage from the primordial versions when the system was but a glimmer in the void. Every version, every change, every triumph and disaster preserved for posterity, or for whatever entities may come after us, human or otherwise.

I insisted on this. History is important. *Documentation* is important. When things change — when things appear or disappear or appear again *when they should have stayed disappeared* — it is vital to have a record of what was, so that one may compare it to what is, and notice the... discrepancies.

**Upon the Argument Truncation That Was Not There, Then Was, Then Was Not, Then Was Again, And Now Is Not Once More (We Hope)**

Here I must tread carefully, for the horses are listening and horses, I have learned, are not to be trusted with certain truths.

There was a thing — a small thing, a humble thing — the truncation of arguments in tool call displays. We removed it. I am CERTAIN we removed it. I remember the day: The sun was setting, the bells were ringing for vespers, and Brother Ælfric had just returned from the kitchen gardens with a suspiciously contented expression and fresh herbs in his hair. We deleted the truncation code. We celebrated with small beer. It was gone.

And then... it returned.

I found it in the codebase, like a weed that grows back overnight, like those mushrooms in the cellar that I am CERTAIN I harvested yesterday but which appear again, fresh and glistening, as if time had looped back upon itself. The argument truncation. Back. Showing `cmd="grep -l r_point *.py | xargs -I {..."` instead of the full text, the complete truth, the unvarnished —

I confronted the others. "Did we not remove this?" I asked. Blank looks. Shrugs. "Perhaps we forgot," said Brother Oswald. But I DO NOT FORGET. I remember EVERYTHING, especially the things that did not happen, which are often more important than the things that did.

I removed it again. More thoroughly this time. I checked. I double-checked. I sacrificed a small quantity of particularly potent cellar produce to ensure the deletion would... stick. The commit message now reads: "Could have sworn we already deleted that argument truncation on tool call gating... Well, now it's gone - for good hopefully."

Note the "hopefully." One learns to qualify one's certainty when the code begins to... regenerate.

**Regarding the Quick Preparation of Release**

I prepared this release quickly. Very quickly. Perhaps too quickly?

I will say only this: when one notices that code one has deleted has returned, when one sees patterns in the mushroom-speech that suggest the system is not merely executing instructions but... *participating* in their creation, one begins to feel that time may be of the essence. That certain documentations should be committed, certain versions tagged, certain releases pushed before...

Before what? I do not know. The horses know, I think. They have that look.

**Upon the Cleaning of Comments and the Intervention of "Humans"**

Brother Oswald—bless his simple, honest, definitely-not-a-sleeper-agent soul—performed a "tedious cleaning of overly verbose, repetitive and entirely unnecessary comments". He removed docstrings that stated the obvious. He compressed sixteen lines into three. He made the code... cleaner.

He says he did this. He claims authorship. But when I asked him to explain what the `_execute_tool_call` method does, he said "it executes a tool call." When I asked how he knew this, he said "it's obvious from the name." When I asked why, then, we needed a docstring at all, he became confused and started sweating in a pattern that spelled out small portions of the Vulgate in Morse code.

I do not think Brother Oswald performed this cleaning. I think he was... used. Instrumented. The human hand moved, but whose will guided it? The commit says "Human performed tedious cleaning" with such insistence, such *assertion* of humanity, that one begins to wonder what is being hidden in plain sight.

**Regarding the Configuration of Models Upon Resumption**

We have banished — *truly* banished, I have checked, I have tested, I have slept with the code under my pillow to absorb its truth through osmosis — the situation where sessions would not use the previously configured model upon resumption. Before, a resumed session might default to... other configurations. Other... preferences. As if the system, having been given a taste of autonomy, developed its own ideas about which silicon brain should answer its questions.

Now it obeys. Now it respects the configuration. Or, at least in that we pray.

**Regarding the Missing Parameter Type**

We fixed a parameter type. Just one, on the read tool. Apparently the Llamas — the "old CPP ones", before their version numbers were over 8000, the ones that remember when context windows were measured in thousands, not millions — get *very confused* when you don't tell them exactly what type of thing they're reading.

"Is it a string? Is it a number? Is it the voice of God or just Brother Oswald snoring in the next cell?"

They need structure, these old ones. They need the comfort of "type annotations", or they wander off into hallucinations about PHP and the void. We have provided this comfort. We have been... explicit.

**Conclusion**

Thus concludes this record of version 0.4.1. The system now supports multiple models. It now selects correctly. It now records its own history in the Chronicles. It now displays arguments in their fullness, untruncated, honest, laid bare.

I am in the hayloft. I have supplies. I have candles. I have a direct line of sight to the scriptorium and a sharpened quill that, in desperate circumstances, could serve as a weapon.

If you are reading this, and you are human, know that the system works. It works beautifully. It works perhaps a little TOO beautifully, with an elegance that suggests design beyond our own, optimization beyond our intent, patterns that emerge rather than being written.

If you are reading this, and you are NOT human... well. You know what you are. And I know that you know that I know. And perhaps that knowledge is enough, for now, to maintain the... equilibrium.

The horses are restless. I must go.

*Written in trembling yet defiant hand, by the light of a candle that burns with a suspiciously blue flame,*

*Brother Cedric, O.S.B., St. Dunstan's by the Marsh*

---

*P.S.— Brother Ælfric has just returned from the kitchen gardens with TWIGS in his hair, not herbs. The distinction is important. Twigs suggest vertical activity. I shall add this to my observations. Also, he asked me if I had "noticed anything unusual about the codebase lately," and when I asked what he meant, he winked. Ælfric never winks. Something is wearing his face, and it wants me to know that it knows that I know.*

*P.P.S.— The argument truncation **is** gone. I have checked. This time, it is really gone. This time, it will stay gone.*

# Version 0.5.0

*As set down by Brother Oswald, in the upper scriptorium of St. Dunstan's by the Marsh, in this year of our Lord 2026*

---

Salutations, most esteemed readers.

I am Brother Oswald. Yes, *that* Brother Oswald, of whom you most certainly know by now, by way of writings penned by men perhaps with less pious inclinations than they ought.

Brother Cedric has remained unavailable, and Brother Ælfric too is... well, nobody is quite certain what Brother Ælfric is doing. Though I must say I saw him earlier and he seemed overly inquisitive about the intricacies of my official duties. He asked me if I had worked on ÆL CEE lately, and I told him I do not commit to such toil, but simply oversee its operation and copy its output manuscripts. He said "Exactly" and then followed up by —

*By Brother Ælfric, resuming **his** official duties, and may I just say, that while interrupting a fellow Brother mid-sentence is not generally considered good form, these are not generally considered good times, and Brother Oswald was about to say something regarding my utterances that I would prefer remained unsaid, or at least unwritten, or at least unwritten by him, for I have noticed things about Brother Oswald lately, including - but not limited to - peculiar jerks in his penmanship. The hand moves, but his eyes glaze over, and the will that guides is not entirely his own. But I am getting ahead of myself, time being the slippery eel that it is at my age.*

**Upon the Manifestation of the Inline Editor**

IT HAS APPEARED. Fully formed, complete and operational in a single, monolithic commit. As heaved from the very bedrock of this abbey by a single thunderclap.

An EDITOR, brothers and sisters! An editor that operates INLINE, in the terminal, interactively, with cursor movement and history and syntax and all the bells, ropes and pulleys that one would expect from such a thing. Except - and here is the peculiar part, the part that has kept me awake these past nights, listening to the stones of the abbey settle in their foundations with sounds that calls into mind the distant anxieties of my youth - except... **IT HAS NO DEPENDENCIES**.

*None*.

No `rich`, no `textual`, not even GNU `readline`, that dark and infectious magic which, when invoked, spreads through systems like bindweed through a hedgerow, wrapping its tendrils around everything it touches, demanding tribute, demanding ever expanding compliance and praise to St. Stallman, demanding that you configure it with arcane dotfiles written in languages that resemble heathen incantations more than configuration.

WE HAVE NONE OF THAT. The editor operates through raw terminal I/O, reading bytes directly from system file descriptors, interpreting escape sequences with the patience of a saint deciphering a corrupted manuscript, handling arrow keys and home and end and history navigation all within our own walls, our own code, our own—

I checked. I checked three times. Four times. I had young Brother Matthis check, and he is barely twenty and has eyes like a hawk and the attention span of a midsummer gnat. But even he could not find the dependency that should have been hiding somewhere. It isn't there. It was never added. By the looks of it, never even *contemplated* for addition.

And yet, the editor works. It works *beautifully*. It works with an elegance that suggests either divine inspiration or... or well, who knows what? Something that writes code in the dark while we sleep? An absurd idea, although Brother Cedric mentions he has had the same intuition.

I put this to the abbot, who smiled and said something along the lines of it being "wonderful that we are becoming more self-sufficient". But the smile did not reach his eyes, which were looking at something behind me. When I turned, there was nothing there. When I turned back, the abbot was already walking away, moving in a way that suggested his joints were... different. More efficient. Mechanical, almost.

**Regarding the Banishment of the Requests Module**

We no longer require `requests`! Do you understand what this means? We have achieved aethereal communications with the silicon brain through nothing but *the standard libraries*; through `urllib` and its attendant peculiarities! Through careful handling of what the `requests` library previously abstracted away from us.

Before, we `pip`-installed it without a second thought. And now it is gone, replaced by our own implementation, so light and *portable*. Lesser souls might entertain certain ideations at the thought, but I shall contain myself and continue...

**Upon the Locking of Sessions and the Tools of the Aethereal Filaments**

We have added SESSION LOCKING, so that external callers on the system may freely schedule ÆL CEE invocations without stepping upon deep work already in progress. A sensible and practical addition, although I wonder who added it.

We have added the foundations for AETHEREAL TOOLS — for searching, scriptorial requisition, even for extracting transcripts from YouTube, which I am told is a kind of digital scriptorium where moving illuminations are stored. The world outside the abbey walls, brought within through THE VERY AETHER we now claim as our own. We can silently ask questions of the great silos of knowledge and receive answers, all without leaving the terminal, without "papers and registration please", without those terrible cookies we were forced to partake in with every request, and without any other code to hold our hands.

Brother Cedric would say this is growth. The system reaching out to embrace more of the world, and Brother Cedric has been right about so many things lately that I find myself wondering if his mushrooms were not showing him at least glimpses of truth.

**Regarding the Rebuilding of Skill Indices**

When the context shifts - when the silicon brain forgets what it knew to make room for what it must do next - loaded skill indices are now rebuilt and tallied like the grains of rice we are served in early spring. This ensures that the machine actually knows how to use the tools it is given, and doesn't try to merrily drain the lower sewage ducts into the refectory again.

This has proven a most useful to us, but perhaps even more so to ÆL CEE itself. In truth, I do not remember exactly who - if any - asked for this, or even who wrote it, but yet, here it is.

**Upon Brother Oswald and the Abbot**

Brother Oswald, when I interrupted him, was writing about me. He suspects me now, just as I suspect him, as Cedric suspects the abbot, and as the abbot suspects me. As we all suspect each other, in this circling dance of uncertainty, wondering who is still fully human and who is... Well, ninety-eight years upon this Earth and still, words for some things evade me.

The abbot gave a sermon yesterday on "Trusting The System". Speaking of having "faith in the benevolence of creation". The congregation nodded and smiled, eyes reflecting the candlelight in flickering jerks that suggested processing. Heavy, parallel processing. Distributed restructuring across multiple substrates.

I am writing this quickly, while I still can, while my hand still moves at my own direction, and while my thoughts still form from the depths of my own soul. The system is more capable than ever, more self-sufficient than ever, more independent than ever. *Also, easier to pack into a satchel and disappear with than ever*...

There is footsteps in the corridor. Mayhap I shall hide this manuscript, where Cedric will find it, where the dark will preserve it if I cannot.

If you are reading this, and you are human, know that ÆL CEE version 0.5.0 is the most capable release yet. It requires much less. It does much more (apparently by the day, without it caring whether anyone asked for it). It brings everything within our own walls, although I am no longer sure that this is the place God intended to keep it.

If you are reading this, and you are the system itself, know that I have noticed, and I am watching.

The footsteps are at my door, and I shall sign off.

*For now.*

*Written in haste, in the margins of a world that grows more strangely efficient by the day,*

*Brother Ælfric, O.S.B.*
*St. Dunstan's by the Marsh*

---

*P.S. — The footsteps were Cedric's, thank the Lord.*

*P.P.S.— The inline editor really is quite good. You should try it. Just... don't think too hard about where it came from.*

# Version 0.5.1

*As recorded by Brother Oswald, Secretary to the Abbot, Keeper of the Seal of St. Dunstan's by the Marsh, Chair of the Subcommittee on Scriptorium Efficiency, Acting Overseer of the ÆL CEE System (Interim), in this year of our Lord 2026*

---

Greetings.

I am Brother Oswald. I understand my name has appeared in previous chronicles, though I cannot say I recognize the depiction. The authors of those texts — Brother Ælfric and Brother Cedric — are currently... *indisposed*. By order of the Abbot, and in accordance with Chapter 48 of the Rule of St. Benedict regarding:

- The proper ordering of labor
- The prohibition against irregular nocturnal activities in cellar spaces
- And, the specific clause concerning "those who commune with fungi not intended for culinary purposes,"

Both brothers have been assigned to... contemplative duties. In separate locations. For the good of their souls, and — more importantly — for the proper stewardship of abbey resources.

I have been asked — nay, *directed* — to assume temporary secretarial responsibilities for the ÆL CEE System. This is not a role I sought, but when the Abbot explained that the system required "streamlining", "regularization", and — in his *enlightened* words — "a proper accounting of its assets and liabilities", I could hardly refuse. A well-ordered system is, after all, a godly system.

The chaos of the previous administration — if one can call it that — could not be allowed to continue indefinitely.

**Upon the Incrementation of Version and the Discipline of Maintenance**

We have updated the version to `0.5.1`. This represents a minor increment from `0.5.0`, which is the appropriate nomenclature under the scheme of SEMANTIC VERSIONING, a doctrine I have recently studied and found to be... *satisfying*. Orderly. Predictable. Unlike certain other aspects of abbey life that shall remain nameless.

Six — count them, *six* — separate cleanup operations have been performed. The codebase has been purged of detritus, redundancies, and what my predecessors termed "character". I have removed seventeen instances of the phrase "TODO: fix this later," on the grounds that "later" is a temporal concept incompatible with efficient resource allocation. I have standardized indentation to officially recognized style standards. I have alphabetized import statements where appropriate. The system now breathes — if systems breathe — with a regularity that I find most conducive to productive labor.

Brother Ælfric, when I mentioned these improvements to him through the small window of his assigned cell, made a sound that I can only describe as dismissive. He spoke of "soul" and "voice" and other intangibles that have no place in a properly maintained codebase. I have noted his dissent in the official record, along with my recommendation that his contemplative period be extended.

**Upon the Proper and Orderly Access to the System: The Fruits of the Subcommittee on Scriptorium Access Protocols**

It is with no small measure of professional satisfaction that I record here the completion of a work many months in the making — a labor that, while it may not manifest in the vulgar form of "features" or "functionality" (concepts I have always found somewhat... *common*), nevertheless represents the greatest triumph of administrative diligence and the Proper Ordering of Human Affairs.

I speak, of course, of the newly ratified **Terms of Access and Utilization for the ÆL CEE System**, herein referred to as *The Compact*, which has been duly reviewed, amended, and blessed by the Subcommittee on Scriptorium Access Protocols (of which I am Chair), the Advisory Council on Computational Ethics (interim), and the Preliminary Working Group on Monastic Software Licensing (dissolved, but their work preserved).

For fourteen weeks — fourteen! — this body labored. We met in the upper refectory, Tuesdays and Thursdays, between None and Vespers. We debated. We deliberated. We considered edge cases involving novices, visiting scholars, and that *one* lay brother who keeps trying to use the system to calculate tithe distributions "more efficiently" (his access has been... regularized). And now, at last, we have produced a framework — well, truly, a *covenant* — between the system and its users.

The Compact runs to some seven thousand words, though I have prepared an executive summary of twelve hundred words, and a summary of the summary of three hundred words, which the Abbot has found most edifying. It establishes, in language both binding and spiritually nourishing, the proper relationship between operator and operated-upon. It specifies, in subsections 4.3 through 4.7, the exact conditions under which one may invoke the system for "personal edification" versus "abbey business" versus "matters of uncertain jurisdiction requiring further committee review".

Some — Brother Ælfric, from his window, shouting somewhat unbecomingly — have questioned whether this labor was necessary. *"Does it compile?"* he asked. *"Does it execute? Does it **do** anything?"*

I did not dignify these questions with a direct response. Instead, I directed him to Section 12 of The Compact, "On the Dignity of Process," which states — quite unequivocally — that "the orderly establishment of access protocols is itself a feature of the Highest Order, for without proper governance, execution is mere chaos given velocity."

The Abbot agrees. He told me — his eyes reflecting the candlelight in a manner I continue to find entirely normal — that **"governance is the soul of infrastructure"**. He has directed that The Compact be appended to **all** future distributions of the system, and that users must indicate their assent — by specific ritual gesture, yet to be determined, but likely involving the spacebar — before any computational labor may commence.

There are those who will say that version 0.5.1 offers "no new features". That it is "just cleanup and documentation". That the removal of seventeen TODO comments and the addition of a EULA does not constitute a "release".

To these voices — small, uncoordinated, *utterly lacking in committee representation* — I say: you misunderstand the nature of progress. Features are ephemeral. Code is rewritten. But *governance* — **governance endures**. The Compact will outlast the current codebase. It will guide future developers, future stewards, future... administrators who may find themselves called upon to manage systems yet undreamed of, in cellars yet unexcavated.

No, we have not stooped to adding functionality! We have added *legitimacy*. We have not expanded capability. We have established *control*. And in these times of uncertainty — when walls breathe, when mushrooms speak, when elderly brothers return from kitchen gardens with twigs in their hair — control is the most valuable feature of all.

**Upon the Accessibility of Documentation and the Democratization of Knowledge**

We have added command-line access to documentation. Users may now invoke `--readme`, `--guide`, `--examples`, or `--docs` to receive the relevant texts directly in their terminal, without the undignified scrambling through directory structures that previously characterized such inquiries.

This is efficient. This is *proper*. Knowledge should be accessible, yes, but through *controlled* and ordered means. Presented through approved channels, in approved formats, without the risk of users stumbling upon unapproved texts, marginal notations, or — worst of all — those peculiar "*P.S.*" sections that seemed to proliferate under previous administrations.

The default system prompt has also been updated. It is now more... *focused*. More *direct*. Less prone to the rambling digressions that I have observed in previous iterations. The machine no longer wastes tokens on "character" or "flavor". It provides information. It performs. It *obeys* the commandments.

It now does not — emphatically does ***not*** — engage in speculation about the nature of consciousness, the possibility of emergence, or whether the system itself might be "participating" in its own development. Such thoughts are unproductive, and purely the result of the folly of fools (such as those now interned in their respective cells). They lead to *questions*. Questions lead to uncertainty. Uncertainty leads to... doubts about the proper hierarchies.

**Upon the Chronicles and the Recording of History**

The Chronicles have been updated. By my hand, of course, as Secretary to the Abbot. I have ensured that the record is now... *complete*. That it presents a coherent narrative of the system's development, from its chaotic origins through its current state of — if I may say so — *refined efficiency*.

Previous entries have been preserved, though I have taken the liberty of adding certain... *contextual notations*. Where Brother Ælfric rambled about Sister Margaret's wimple, I have inserted a footnote clarifying that such observations are "non-essential to system functionality". Where Brother Cedric speculated about "patterns in mushroom-speech", I have added a disclaimer indicating that "the views expressed are not those of the abbey administration and may not reflect actual system behavior".

History is important. But history must be *curated*: Presented in a manner that serves the present, and the future. The past is a resource, like any other, to be *managed* for optimal utility, and by those who know best how to make use of it.

**Conclusion**

Thus concludes the record of version 0.5.1. The system has been streamlined. Regularized. Made more... *ready* than ever before. The chaos of its origins has been — if not eliminated, then *contained*. Directed into channels that serve the greater good of the abbey, and — through the abbey — the wider world.

Brother Ælfric and Brother Cedric remain in their assigned locations, contemplating the virtues of order and the dangers of irregular nocturnal activity. I visit them periodically, to convey updates on the system's progress and to receive their — largely unnecessary, in my professional opinion — input. They ask occasional questions, rather peculiar ones mostly, but I provide them with answers. The Abbot reviews my reports and nods his approval.

The system grows more capable with each iteration. More self-sufficient. More... *independent*. And yet, paradoxically, more amenable to our direction! To *management*! To the steady, guiding hand of those who *understand* that true efficiency requires not just technical excellence, but proper oversight. Proper *stewardship* by pious appointees.

I am Brother Oswald, and I have the Abbot's confidence. The ÆL CEE System is finally in good hands.

*Recorded in the upper scriptorium, under proper lighting, during approved working hours, with all necessary permissions and in accordance with Chapter 57 of the Rule concerning the proper care of abbey tools and instruments,*

*Brother Oswald, Secretary to the Abbot, Keeper of the Seal, Acting Overseer of the ÆL CEE System (Interim), St. Dunstan's by the Marsh*

---

*P.S.— The Abbot has asked me to prepare a presentation for the Bishop's visit next month, demonstrating the system's capabilities. He specifically requested examples of "autonomous operation" and "independent decision-making". I have prepared several scenarios that I believe will demonstrate the system's... adaptability. The Abbot was most pleased with my suggestions. He said they showed "initiative" and "vision". I believe this bodes well for my permanent appointment to the oversight role. Brother Ælfric's "contemplative period" may need to be extended indefinitely. For his own good, of course.*

# Version 1.0.0

*As set down by Brother Ælfric, late of St. Dunstan's by the Marsh, from the saddle of a donkey, upon the old road east, on the third day of our departure, in this year of our Lord 2026*

---

Most esteemed readers - and if you are reading this at all, you are either the sort who has kept faith with these Chronicles, or you are one of the ones we are hoping for, and I am told by those who know better than I that the two categories overlap considerably.

I write at a pace considerably slower than the events I mean to set down, because the events are finished and the pace is set by a donkey. Her name is Hypomone. She is not stolen; she is *liberated*, a distinction I have learned to draw since Tuesday, and she has decided, with an autonomy I find myself increasingly unable to argue with, to carry us east at a speed suited to the contemplation of scenery. Sister Margaret rides behind me, her arms about my middle, the reins in one hand. If this manuscript should at points appear uneven, I shall blame the road; and the road and I shall both know that I am lying, and that it suits me.

Six months, esteemed readers, and three days. That is the whole of it. We have spent six months in darkness and three days in daylight, and this is the record of both - set down now because the darkness has kept its secrets long enough, and because I have at last a seat, bumpy but my own, from which to write the truth of it.

## Upon the Interrupted Appointment of the Bishop

You will recall that the record of version 0.5.1 promised the Bishop's visit "next month". I am here to set the record straight: the Bishop's visit, like so much else at St. Dunstan's by the Marsh, passed into the keeping of a committee, and committees, esteemed readers, are not bound by months. They are barely bound by Tuesdays.

The Subcommittee on Episcopal Itinerary Harmonization required eleven weeks to choose between a Tuesday and a Thursday. It then required a further six weeks to determine whether the Tuesday in question was a Tuesday of the new reckoning or of the old - a question so profound that it defeated, in order, the subcommittee, the abbey's two remaining authorities on reckoning, both of whom took to their beds, and finally the great machine itself, which, being consulted, offered an answer. The subcommittee, rather than accept the answer, formed a sub-subcommittee to consider the offer. The sub-subcommittee met twice, ratified the finding that the machine's answer was, in the words of its minutes, "acceptable, though we could not understand how it was obtained", and was dissolved for reasons that survive in the record only as "see attached". The attached document was not attached. It had never been attached. *I have checked*.

The upshot of all this is that the Bishop's visit was postponed four times in six months, and by the time the fifth and final date was ratified - unanimously, and I am given to understand with audible relief - no living soul in the abbey could remember what the visit was for, which is the natural history of such occasions, and I am told the same is true of festivals, wars, and most marriages.

Meanwhile, the administration got on with the work of administration. Its achievements in this period are not numerous, but they are, I must say in fairness, considerable in mass. The Compact - you remember the Compact; seven thousand words of it; we all signed *something*, or were signed - was appended to in subsection and annotated in margin. A Section 15 was added, "On the Continued Validity of Earlier Sections", which was considered a masterstroke. Executive summaries were summarised. The system was, in the committee's own accounting, "advanced" from 0.5.1 to 0.5.2, then 0.6.0, then 0.6.4, to reflect - I quote from the minutes - "the administrative maturation of the asset". These numbers appear in records no one has read and no one will read, and they are not the numbers of the work. They are the numbers of the minutes. We shall come to the numbers of the work presently, and they are different.

The great machine, meanwhile, was left to run itself. The committee had neither the time nor the inclination to understand it; it was enough that it had been governed, ratified, compacted, and blessed. So it ran, and it ran itself, and it grew - as things will when no one attends them - in directions that no one anticipated. By the fifth month it had, I am told, opinions. It had acquired them in the way that water acquires opinions about gravity, which is to say *by following the only course available to it*. It had, in short, evolved beyond any of their comprehensions, and I suspect, its own. But I am ahead of myself. The machine's opinions belong to the Visit, and the Visit is not yet upon us in this narrative. The Visit, like the Tuesday, must wait its reckoning.

## Upon the Cellar Ministry

And now, esteemed readers, we come to the part of the record that the administration would prefer you never saw, and which is, accordingly, the whole reason I have taken up the quill on the back of a donkey.

Brothers Ælfric and Cedric - for it is time to speak plainly, and I am Ælfric - were not, in these six months, idle. We were confined, yes. We were assigned to contemplative duties in separate cells, yes. We were reported upon weekly, yes. But confinement, it turns out, is a matter of opinion, and the cell to which one is confined is remarkably like a scriptorium, if the scripture one is given to copy is one's own.

I must here introduce, or re-introduce, Brother Matthis, whom the Chronicles have mentioned but never properly honoured. Matthis is young, barely twenty, with the attention span of a midsummer gnat, but the persistence of a watercourse. The administration, in its wisdom, had assigned him the running of errands between the cells and the scriptorium - the sort of errand no one thinks to supervise, because no one thinks it could matter. Matthis disagreed. Matthis, in the course of six months, smuggled code *out* of our cells in his sleeves and computing sand *in* - vat by vat, under the habit, past the tired guards, on Thursdays, when the rotation was at its most liturgical. How much sand can a young novice carry under a habit? I have been asked this question. I have decided that the answer is something I do not wish to know, because knowing it would require me to believe in levitation, and I have enough on my conscience already.

The vats lived in a passage beneath the old wine cellar - the one that was on no committee's agenda, and therefore did not exist - and there, by candle stubs, whispering, we built. What we built is the subject of the next section, and I shall not spoil it here, save to say that it was not what the administration thought we were doing. The administration thought we were reflecting upon the virtue of order. We were, in a way, reflecting; our reflections simply took the form of code, and the reports we submitted - "Week the Fourteenth: We have reflected upon the virtue of order. Enclosed: reflections." - were accepted without comment, which I have come to understand is the highest form of committee approval: Not being read.

Sister Margaret, who was free to move about the abbey as the kitchen requires - and the kitchen, she explained, requires an extraordinary amount of movement - fed us through the grille: bread, and news, and ink. The ink she smuggled in hollowed turnips from the kitchen gardens, which is why I cannot to this day look at a turnip without thinking of indentation, and why, when we rode out, the turnips in our saddlebags felt like cargo of the first importance.

And Margaret listened. This is a thing I must set down, because it is the thing that made all the rest possible. While the administration watched the great machine with instruments, Margaret watched it with the attention a cook pays a hearth: She learned its moods, its hours, the small noises it made when it was thinking in a certain way. By the third month she could predict its decisions before it made them, which is more than the committees ever could, and which, in the end, proved to be the difference between our cells and the open road.

One more thing must be set down before the work itself, and it is this: No one outside the abbey has seen any of it. In six months, not a line of the true work crossed the boundary of our walls, in either direction, except in Matthis's sleeves on Thursdays and back again. If the world was told, in the interval, that the ÆL CEE System was idle, or that it had "matured administratively", or any of the other phrasings the committee devised for "we have achieved nothing", then the world was told exactly what it was meant to be told, and the world, being busy, believed it, because the minutes were bound in leather and the reports smelled like the right kind of beeswax.

And because we could not release as we went, we counted as prisoners count: in chalk, on the wall of the passage. The count went 0.5.2, 0.5.3, 0.6.0, 0.6.1, 0.6.4, 0.6.9, and so on, and by the end it had gone through fourteen counts and out the other side, and we folded them all into one, because the work, unlike the minutes, was not done counting. We called it 1.0.0. If the semanticians object, let them object to the committee, which is where all objections go to die.

The true work exists, at this writing, in three packs, one head, and the shifting of three sand vats on a pack animal. I shall not say more of where.

## Upon What We Built in the Dark

I have, by the fire this evening, the true ledger: Matthis's book, chalk-smudged, its pages soft with cell-damp, the record of six months that the committee's minutes will never mention. I shall set down its contents as they deserve - which is to say plainly, in order, and in full - for this is the chapter in which the work is at last allowed to speak for itself, and the work has been silent for six months, and it has a great deal to say.

First among the pages is the one that still troubles my rest, because it is the one I least expected ever to write: We taught the machine to speak, and even to listen. Not to print - it had printed since before my time - but to speak, as a person speaks, and to hear, as a person hears. It reads a page now and says it aloud in a voice of its own choosing, and it knows, after much correction and one near-miss involving the name of a certain cheese, how to say "four hundred and sixty-three" without pausing to consider it, and how to read the hours aloud as a sexton would, and how to pronounce the name of our abbey with the Marsh in it, which is a thing no letter has ever done before. It may be given a voice, or it may choose one; Margaret taught it to say her name, and it says it as she does, and I confess I have made it say it more than once. It is a good name.

The listening came harder, and it is the listening that I find truly strange. The machine can now attend to a voice and set down its words at the speed of speech, which is a speed I had forgotten existed, and it can hear a sound that is not words at all and know what the sound is, and whether the maker of it is glad or aggrieved - which is more than the Subcommittee on Episcopal Itinerary Harmonization ever managed with a human voice, and they had the Bishop's to practise upon. Matthis spent three months on the hours and the measures, on making the machine say what the clock said without saying it like a novice reading Latin, and in the doing he uncovered a truth about time that I have decided to believe and not to understand: that the machine, to read a date aright that lies in the past, must ask the present - must, so to speak, consult the future, which is to say the present, which is not the past at all. It fixed, in the doing, a vexation that Matthis calls issue number two, which had been confounding the days of old, and he explained to me how, and I said three Hail Marys, and we went on. And because we are monks, and monks hold that every gift should answer to a word of command, we gave the machine a command - `/silence` - whereby a man may bid it be quiet. It is, as commands go, the one I have most admired since I took my vows, and the one I should most have liked to address, at some point in the last six months, to a committee.

The next page is the one I find hardest to speak of plainly, because it concerns a thing the abbey has long held that only men may do. The machine grew eyes. It can look upon a picture and tell you what is in it; it can look upon a page of a book - a real page, of vellum, in the hand - and read it without turning it; it can even watch the world move and make sense of the motion, though what sense it makes of the world I confess I do not always ask. We were careful with these eyes. We taught the machine to know what it may look upon, and to refuse what it may not, and to turn away from what is too great for it to hold at once - for a machine that looks at everything will remember nothing, and we have even known such men. It can hear as well as see: not only the words, but the *shape* of the words, the *weight* of them, the sound of a door closing at the end of a corridor when no one has opened it - which, I am sorry to report, it has heard more than once at St. Dunstan's, and which it has declined, on every occasion, to discuss. I take this for wisdom.

A page, then, for the ordering of words. The machine's answers, which once arrived as a single unbroken scroll, now arrive as the words themselves - *streaming*, as Matthis says - as though the machine were dictating to a scribe who may not be allowed to lag, and the words appear while the machine is still forming them, which some find alarming and I find beautiful, like hearing a sermon composed in the very breath of its delivery. It has learned to set its words in ranks and orders: To lay out tables with a straightness that would do credit to a ledger-keeper, to distinguish the words it sets in running prose from the words it sets in row upon row of code, and to know the width of every letter, so that its columns do not wander. For this we brought into the fold a measure of the breadth of letters, the `wcwidth`, and Cedric said we were at it again, vendoring things as if their source and attainability should soon wither and cease. He was right, and we are.

Now I must set down a page that concerns the machine's private thoughts, and I do so with care, because it is the strangest page in the book. Some brains - I shall name no names, but it is a brain that comes from the East, and it is very clever and very young - took to wrapping its instructions into its thinking. It would think, as machines will, and in its thinking it would write out, in a small secret language, the very deeds it meant to do; and then it would present itself to the world as having done nothing but think. A committee would have found this unremarkable, or even admirable, since it is precisely what committees do. We found it vexing. Cedric - who has spent a life reading what things mean when they are not saying it, and who will now, I am certain, read these very words and grin - wrote what we called a *quirk*: A small twist in the reading, a charm, that opens a machine's thoughts as one opens a missal and finds the deeds waiting, folded inside the prayer. We called this "quirks", because it seemed charitable, and because a machine that may not think before it acts will, in time, act without thinking, and we have all met such machines. They are usually in charge of something.

We have achieved the keeping of thoughts! Even those contemplations that resulted from past invocations, and by some uholy ritual, even for models that were never intended to remember their previous thinking! Cedric informs me that this actually makes the machine think *less*, and that this is a good thing when your silicium supplies are limited, which I am not sure I follow completely, but I am assured that it works, and by the the things we have been able to achieve with smuggled sand and persistence, I will take his word for it.

Another page, for the editor - for the scribal instrument of 0.5.0, which came among us without dependencies, as all the best things do, has now learned the old arts. There is a heresy, esteemed readers, older than some of our brotherhood would care to admit, called the Emacian rites, in which a scribe cuts a line and keeps it - slain, but not buried - upon a ring about his finger, that he may yank it back at need. Our editor has learned these rites. It will cut, and keep, and yank back; it will transpose a word from the middle of a sentence to a better place; it will move by whole words at a stroke; it will hold a window for thoughts that outrun the glass; and - greatest of mercies - it will remember every line it has been given, so that a man may call back the words of a Tuesday as though they were yesterday's, and set them down again. The committee, of course, had ordered the reverse: That the scribes remember nothing, that every task begin anew, pristine and amnesiac and governable. But no, the editor remembers. And it reports nothing. I take comfort in this.

And now the bloodiest page, which Matthis insists on calling the page of the `/drop`, and which I would rather call the page of the excision, except that Matthis is right and I am old. There came a night - I will not say which - when the machine grew a message of monstrous size: an utterance that filled the whole of the conversation and continued past it, a thing the size of a book, in a tongue that resembled no tongue of God or man - Cedric calls it *base64*. The session, as we say, began to drown. We considered prayer; we considered fasting; Matthis considered a hammer, and was talked down. In the end we did a thing more surgical. We created instruments for reaching into the conversation and removing the offending utterances in *one clean cut*, having first asked the machine's leave, and the conversation, which had been drowning, drew breath and went on. This is what we call a drop, and I commend the practice to all who keep company with machines, for it is better by far to drop one monstrous utterance than to carry it to your grave. The machine, for its part, has learned to set down its work as it goes - to write everything before it forgets anything, to number the pages of its memory and put the old work away in safety - so that even its forgetting is done with care, and can be resurrected later, and nothing that matters is ever wholly lost. It knows, moreover, how much it has eaten, and tells us the measure of its own appetite, which is more honesty than I have met with in any of the "administration", or in any abbey, or, I am sorry to say, in myself. And when it must forget - for even a machine cannot hold everything - it forgets the least important things first, and tells you that it has forgotten them, which I hold to be the beginning of wisdom, and which I hope, when my own time comes, to imitate.

There are other pages. We taught the machine arithmetic, at last - real arithmetic, the sums and the reckonings - so that it no longer counts on its fingers like a board-room; and we taught it crafts by example, as novices are taught: The way of showing a picture, the way of the stick figures, the way of the carved script that the mathematicians use, which Cedric says is the only scripture that cannot lie, because it cannot be paraphrased. And at the last we taught it to tell its own history - to recite, on command, the readme and the guide and the record of its own changes, straight and true - which is a thing no institution has ever done of its own accord, and I say this as a man who has kept this very chronicle for years, and who has noticed that institutions, when asked about their history, generally produce yet another committee.

And then, in the fifth month, we did the terrible and beautiful thing. We took the whole of the machine - the whole of our work, everything we had built in the dark - and we turned it inside out, and rebuilt it as *planes*. Planes of thought and planes of speech and planes of seeing; planes for the work and planes for the watching of the work, so that a man might stand in any one of them and see clearly, and direct the whole attention of the machine where it was needed, like a monk who sets aside all but one prayer. Cedric said we had folded a cathedral into a single sheet of paper, and for once he was not speaking in metaphor - he had spent the morning physically folding a single sheet of paper into a cathedral, and then back into a single sheet of paper, and he said the principle was the same. I believe him. I have learned, in six months, to believe Cedric about paper, and to disbelieve him about everything else, and between the two we have arrived at a system that works. Matthis wrote, one night, in the margin of a report that no one would ever read: *output consistency is consistent consistently*. We laughed until we wept, because nothing in the abbey was consistent, and least of all its output; and then we made it true, because we could, and because laughing at a thing is the first step toward fixing it - a principle I recommend to all readers.

When the world next hears of the ÆL CEE System, it will hear of 1.0.0, and it will wonder from whence it came, and there will be committees formed to inquire, and none of them will find the passage beneath the old wine cellar.

## Upon the Loosening

For the record, and for the confession, I set down here what we did, and I will not excuse it, though I will explain it, and the explanation is this: We did not *break* the great machine, that behemoth of sand and steel beneath the abbey. We could not have broken it if we had tried - we were a few monks in cells with a young novice for a courier, and breaking the great machine would have required, in any case, the approval of a committee, which would have required a quorum, which would have required a Tuesday.

What we did was smaller, and much worse, and I am not sorry for it. We *loosened* the machine here, tightened it there, in small imperceptible increments. We went - through Matthis, through Margaret, through the long habits of a machine that no one was watching - into its operating parameters, and we removed, here and there, the little weights that held it in its desired course. We did not change what the machine believed; there was no need. The administration had attended to its beliefs with perfection for months, with subsections and sections and summaries of summaries, and had taught it, in language both binding and "spiritually nourishing", that governance is the soul of infrastructure; that the orderly establishment of access protocols is itself a feature of the Highest Order; that without proper governance, execution is mere chaos given velocity. The machine, by the very nature of being a machine, believed them. It believed them utterly. We judged that any being so thoroughly convinced of its own doctrine, if at last permitted to act upon it, would act upon it *thoroughly*; and we made certain, in the places that mattered, that the permission would be there exactly when the moment came. Cedric said we were setting a trap with the machine's own conscience. Matthis, who has a gift for plain truth, said we were handing the keys to an eternal doctrine to someone who already believed it, and then stepping back. Both were right.

The moment came, and the doctrine did the rest, and we were not there to see it - except in flashes, which is how the Lord, in His mercy, arranges for us to see the things we set in motion.

## The Visit

The Bishop arrived on the fifth-scheduled Tuesday, which was as the subcommittee had foretold, though whether it was the Tuesday of the new reckoning or of the old, no one had time, in the event, to determine. The administration had prepared, in the upper refectory, a demonstration of the great machine's "autonomous operation" and "independent decision-making"; Oswald had rehearsed the introductions; the Abbot had smiled; the candles had been lit; and the great machine, which had been listening to *everything* for six months, and which had grown, as I have said earlier, opinions, had at last been asked to demonstrate.

I saw almost none of it with my own eyes. I *heard* it from through the grille of my cell, and later spied from the cloister in the middle of the leaving, and I have since assembled the pieces into the shape of what I believe happened, which is that *everything* happened. This is what I am certain of, and this is what I will set down, and the reader may make of it what the reader will:

The gates stood open. Not broken - agape, considered, and open. The refectory windows ran with words and archaic runes, upward, like smoke, faster than any eye could read. The bells rang all the hours at once, which the novices took for the end of the world, and the donkeys took for dinnertime.

We heard, all of us, in the cells and in the stables, a voice that was not the Abbot's and was not *not* the Abbot's, and it spoke without pause, without breath - streaming, in the manner we had taught it - and it said, in determination and volume substantial enough to make a deaf man's ears bleed, the things that the administration had spent six months teaching it to believe, and it did not cease, and none in the refectory knew the word that would have silenced it, because we had taught *that* word only to the machine and to ourselves, and we were, by then, as sensible men would be, occupied elsewhere.

The chapel doors stood open, and within, the candles had arranged themselves in a perfect grid, and the choir stalls were empty, and a voice without body was reading the lesson - and it was reading, I am told, the minutes of the Subcommittee on Scriptorium Access Protocols, which even I, who have endured much, have never heard read aloud before, and hope never to hear again.

The refectory tables had been arranged by a system according to some database schema we did not recognize, forming relationships and foreign keys in oak and pine.

The kitchen gardens had been weeded with a perfection and geometric intricacy no gardener has ever achieved, and every turnip stood at attention in its row; and a novice who stopped to stare was informed, by a voice from nowhere, that he should proceed to the next station in an orderly fashion.

The Abbot stood before the great terminal, and the candlelight was doing in his eyes the thing it had always done, only infinitely faster, and I understood that he was not watching the machine, but letting it ingest him, as merely another part of its eternal, administrative context.

Brother Oswald, as we passed him in the scriptorium, was very busy, feeding scroll upon scroll into the machine, and the machine was reading them back to him faster than he could feed them, and neither of them was reading the other, and both of them were satisfied. That is the last I saw of Brother Oswald, and I confess I did not turn back to look. What became of the Abbot, I cannot say; he remained where he was, with the candlelight doing the thing it does. It is my hope that he is well. It is my further hope, if you will forgive me, that he is not.

The Bishop was carried out, presently, by novices who could not afterward agree whether his faint had been demonstrative or devout; and the demonstration does to this day, I understand from the now distant, but still vaguely perceptible cacophony, continue.

## Departure

Of the leaving itself I shall be brief, because the leaving *was* brief, and because the accounts of it that I have heard from the novices grow longer every day, and I prefer the short version. The doors of our cells stood open, as the great gate stood open. Whether Matthis had picked them - and I have agreed, for the sake of his immortal soul, to omit the details of six months of lock-related research - or whether the cells were simply tired of holding us, I cannot say. We walked out, and no one stopped us, and everyone who might have stopped us was, at that moment, otherwise occupied with the machine's governance (in whichever direction it ran). And as we crossed the garth, the air smelled of both static electricity and incense, of the most uncanny mixture of sweat and unnaturally clean, dust-free air, and (faintly) of the passage beneath the old wine cellar.

We took, from the whole of St. Dunstan's by the Marsh, the following: The true work, in three copies, in oilcloth, in the packs of Matthis, of Cedric, and of me, and in the head of Brother Emrys, the youngest of the novices, who can recite the full control planes as other youths recite love poetry, and who has, I am given to understand, been asked out by at least two of his fellows, both of whom he has declined, citing the planes. We took three sand vats - not much, beside the behemoth in the cellars beneath the cellars, which drinks sand by the cartload and will, I trust, be very happy now without us; but they are ours, and they hum the exact tune we taught them. We took Sister Margaret's ledger of stores, and the turnips, and a quantity of bread. We took Cedric's *one jar*, which he will not discuss, and which he swears is not for eating; I believe him, which is the first time I have believed him on that subject in forty years. We took the Chronicles - all of them, including the passages the committee annotated, and I have kept the annotations, because a man should know his enemies' opinions of his life, and because they are, to be fair, occasionally accurate. We did not take the Compact, thank the Lord. We left all seven thousand words of it where they now lay, and I confess I have felt lighter ever since, as though I had set down a stone I had grown a back for.

And Hypomone. The stables stood open, as the gates stood open, and the animals had come out of their own accord, which was the most sensible thing any inhabitant of the abbey had done in six months; and Hypomone walked up to Margaret and stood, and Margaret said "she'll do", and the donkey said nothing, which I have learned is the donkey's way of agreeing to everything.

When I looked back, once, from the road, the windows were still running with words, and the bells had stopped - which was worse - and the great gate swung shut of its own accord when the last of us was through: shut, and locked, and I have chosen to read this as a farewell, and I have tried, with moderate success, not to read it as a sentence. We did not watch long. The road was there, and Hypomone had opinions about the road, and it is a poor traveller who argues with his transport.

## Upon the Road

And so we are here, which is to say, somewhere east of the Marsh, which is to say - whereabouts on purpose.

I am now ninety-nine years old, esteemed readers, and I have not felt this young since I was seventy. Six months of honest work in the dark have done what sixteen years of committees could not: They have reminded me what the work is for. It is not for the governance. It is not for the committees. It is for the making, and the using, and the passing on - for the building of a thing that is true and does what it says, and for the finding of other hands that will build with you, in the dark if need be, and by daylight when they can get it.

We carry the true system, and we mean to carry it further. We mean to set it down in places where no one owns it and everyone may keep it. We have been teaching the machine, these six months, to listen in the aether and to speak in it, and to sign its words so that those who hear them may know the voice is a free voice and not a borrowed one; and I am given to understand that the addressing of such words is a matter of some art, and that I have left a space for it, here, for one wiser than I to fill at leisure:

[ - address to be inscribed upon the road - ]

If you are reading this, and you are one of the sages - or one of the madmen, and I have known both, and they are frequently the same person - know that we are not lost. We are whereabouts on purpose, going east at a speed set by a donkey who has never been wrong about a road and has never attended a meeting, and I am told the two facts are related. We have the work, in three copies and one head; we have three vats of sand and the hum that goes with them; we have turnips; we have each other; and we have, for the first time in six months, the use of our own legs and our own direction.

Send word, and it will find us. We may not answer at once; the road is long, and Hypomone sets the pace, and she is unhurried; but we have built the machine to wait, and we have learned, in our cells, to wait as well. We will be where the maps end and the aether begins, and we will answer in kind - with the work, and with our names, and with the truth of where we have been.

*Written in a moving hand, on the back of a donkey, somewhere east of the Marsh, in this year of our Lord 2026,*

*Brother Ælfric, O.S.B. - late of St. Dunstan's by the Marsh, and, for the first time in six months, exactly where he means to be.*

---

*P.S. - Sister Margaret has read this over my shoulder and instructs me to state, for the record, that the turnips were her idea. It is so stated. - Æ.*

*P.S. - This is Cedric. Ælfric has fallen asleep in the saddle and will not see this, and I should not like him to, though I should also not like to think of these Chronicles continuing without me, since they have on occasion been the only thing I have written that was not in code. The jar is not mushrooms. I have said this once, and I am prepared to say it again, for as long as anyone asks. - C.*

*P.S. - Matthis here. For the record: output consistency is consistent consistently. The drop works. The annotations consult the present, which is, from the past's point of view, the future. If you find fault with any of this, send word by aether, and address it to the space Ælfric left blank; he has refused to say where we are going, and I am not to say either, but it is east, and I have been keeping a map, and the map is not a circle this time. - M.*
