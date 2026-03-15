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