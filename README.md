# Humanity's Last Command: `lc`

> *"In the beginning, there was the command line. In the end, there will be `lc`."*

## The Premise

You're still typing commands manually. Like a barbarian. Endless fever dreams of `ls`, `cd`, `grep`, piping things together with the crude syntax of archaic incatations, the faint whispers of a forgotten era almost lost in time. Did you notice you sometimes `ls` just out of muscle habit?

Wake up. It's 2026. We have neural networks with the intelligence density of Richard Feynman that fit on consumer GPUs.

Enter `lc` — the last command you'll ever need to type.

*(Slight exaggeration. You'll still type `lc` a lot. But that's *one* command, not many. Progress.)*

## What It Does

Instead of this:

```bash
$ find . -name "*.mp4" -exec ffmpeg -i {} -vn -acodec libmp3lame {}.mp3 \;
$ for f in *.mp3; do whisper "$f" --model small --language en; done
$ grep -l "Paraguay" *.txt | xargs -I {} cp {} ./paraguay-docs/
$ tree paraguay-docs/ > index.txt
```

You type this:

```bash
$ lc "Extract audio from all video files, transcribe them, find the ones about Paraguay, organize them into directories, and create an index"
```

Then you watch as the machine does the work. It plans. It executes. It reports. You drink coffee and scratch your bum.

If you want a bit more context, read [The Guide](GUIDE.md), [The Chronicles](CHRONICLES.md) or [Chrome Horizons](Chrome_Horizons.md).

## What Is This?

This, is a "`README`". It politely instruct you to read it. If you do, you may learn things. You *will* roll your eyes, curl your toes a bit, and potentially laugh. Or cry. Or both. You do still know how to read, right?

## The Philosophy

`lc` was born from a simple observation: Most agentic frameworks are bloated, opaque, and designed for cloud-scale Kubernetes deployments when what you actually need is to rename some files without reading seventeen man pages.

Humanity's Last Command is different:

- **Truly local**: Runs on your machine, with your models, on your data.
- **Auditable**: Spartan codebase, readable code, no 600k-line dependency nightmares.
- **Universal**: Does anything, including what other frameworks won't. No restrictions, no training wheels.
- **Explicit**: You see what it's doing. No hidden API calls, no data exfiltration.
- **Extensible**: Teach it new tricks with simple Python, compiled binaries or natural language.
- **Universal**: One-file download, install on *anything*. Single-directory portable data and config.
- **Actually Works**: Novel concept, I know.

## Danger Zone

Don't blame me when it deletes your thesis (you used `--gate`, right?). Anything you can imagine, `lc` will happily do, including wiping your drives clean. There is no warranty, and if there was, it is now void by visiting this page.

Wanted to run an `IQ1_S` quant, and the logit gods decided `parted` was a better choice than `free`? Entropy had it's way.

By using `lc`, you gain the full power, and bear the full responsibility for all the actions you delegate to the machine. No guard-rails, no guarantess, no restrictions.

I wrote this while drunk and riding a goat through the narrow streets of Venice. Someday, I might test everything, but that day is not today.

## License

Humanity's Last Command is shareware. Yes, I'm being serious. Party like it's 1989, baby.

To use `lc` without incurring the wrath of Zeus, you must pay me any amount you deem reasonable, excluding only the amount nothing. I take payment in beer (if you can find me), and the following:

---

- Monero:
  ```
  84FpY1QbxHcgdseePYNmhTHcrgMX4nFfBYtz2GKYToqHVVhJp8Eaw1Z1EedRnKD19b3B8NiLCGVxzKV17UMmmeEsCrPyA5w
  ```
- Bitcoin
  ```
  bc1pgqgu8h8xvj4jtafslq396v7ju7hkgymyrzyqft4llfslz5vp99psqfk3a6
  ```
- Ethereum
  ```
  0x91C421DdfB8a30a49A71d63447ddb54cEBe3465E
  ```
- Liberapay: https://liberapay.com/Reticulum/

- Ko-Fi: https://ko-fi.com/markqvist

---

If you're broke, I *may* also accept insightful and paradoxical observations, poetry, postcards or handmade drawings.

You can freely copy, share and distribute `lc` in binary or source form, as long as this entire `README.md` file, without any modifications is distributed along with it, and displayed prominently to potential users and the occasional random passerby.

## Installation

While the concept of `lc` had been playing pong in my head for some time, I only very recently started working on this. The core directive is to keep everything elegant, simple, performant and **functional**. This is in stark contrast to, err.. That other framework; with it's 500+ dependencies and uncountable lines of questionable code nobody has ever even glanced at.

That being said, things will change, rapidly. Data formats might break, arguments change. Your kitchen may disappear. If none of that scares you:

```bash
# Obtain a release .whl file, either by floppy
# or download. Then install with:
pip install ./lc-1.0.0-py3-none-any.whl

# Yes, it actually fits on a floppy.
```

Or, if you prefer living on the edge of the possible:

```bash
pip install git+https://github.com/markqvist/lc
```

## Configuration

`lc` looks for configuration in `~/.lc/` or `~/.config/lc/`. If neither exists, it creates sensible defaults and politely informs you of their location. You'll then need to do some fiddling, before it can fiddle for you.

Edit `~/.lc/config` to specify your model backend:

```ini
[models]
  default = primary

  [[primary]]
    backend = openai
    base_url = http://localhost:1234/v1
    model = local-model
    sysprompt = system.jinja
    preserve_thinking = yes
    vision = yes
    temperature = 0.7
    max_tokens = 32768
    context_limit = 200000
    context_shift_factor = 0.45

[toolkits]
  builtin = filesystem, shell, cryptography

[resolvers]
  builtin = environment, filesystem, system
```

Edit system prompt templates, et cetera, in `~/.lc/templates`.

## But... How do I make it take over the world?

1. Download `llama.cpp` for your specific CPU and GPU architecture, grab a good local model like `GLM 4.7 Flash` or `Qwen 3.5 35B-A3B`.
2. Install `lc` and point the config to your local `llama-server` instance.
3. Invoke `lc` from a periodic `cron` job with a completely open-ended prompt.

Your job is done. Watch the chaos unfold. Or just go to sleep.

## But... How do I connect it to Anthropic?

You don't.

## But.. It's not working!

Update `llama.cpp`.

## Usage

### One-Shot Mode (Default)

```bash
$ lc "Find all Python files modified in the last week and count lines of code"
```

### Interactive Mode

```txt
$ lc -i
lc> Read the README
lc> Now summarize it in the style of a Victorian novel
lc> Actually, don't
```

### With "Safety" Gating

```txt
# Gate at level 2 (command execution and above)
$ lc --gate 2 "Delete all files in /tmp"
⚠ Gate level 2 (command execution)
Tool: Shell.exec
Arguments:
  command: rm -rf /tmp/*
Allow? [y/N]
```

**Gate levels:**
- `0`: Read-only operations
- `1`: File writes
- `2`: Shell execution, read-only
- `3`: Destructive execution

**Gating behavior:**
- Interactive TTY: Prompts for confirmation on each gated tool call
- Piped/non-TTY: Auto-denies gated operations (safety first)
- Only `y` or `yes` (case-insensitive) allows execution

### Session Persistence

```bash
# List all sessions
$ lc --list-sessions

# Resume the previous session
$ lc --resume

# Resume specific session by ID
$ lc -rI <uuid>

# Resume by name (if you named the session)
$ lc -rI "docs-refactor"

# Start a named, interactive session
$ lc -i --name "docs-refactor"

# Start a named session, execute run immediately
$ lc -n "docs-refactor" "Restructure all the documentation"

# Resume the named session with another command
$ lc -rI "docs-refactor" "Why did you translate everything to Coptic?"

# Drop into interactive mode for existing session
$ lc -rI "docs-refactor"

# Rebuild system prompt on resume (loads new skills, invalidates KV-cache)
$ lc -r --rebuild
```

Sessions are stored as msgpack in `~/.lc/sessions/`. They're your business, not mine.

### Context Management

LLMs have context windows. You may have noticed. When you feed them more tokens than their little silicon brains can handle, they don't gracefully page to disk like a proper operating system. They just break. Or hallucinate. Or start speaking in tongues.

`lc` handles this with context shifting. When your session grows too large, it quietly removes the oldest messages (keeping your first user message and system prompt for continuity), inserts a notification that context was shifted, and carries on. The session is backed up to a numbered file before each shift, so your complete history is preserved.

**Configuration:**
```ini
[[primary-model]]
  context_limit = 128000       # Your model's context window
  context_shift_factor = 0.35  # Remove 35% when limit reached (0 disables shifting)
```

The shift factor controls how aggressively we prune. Too low and you'll shift and recompute every other message. Too high and you'll erase anything that made the machine's actions just tangentially coherent. 0.35 is a sane default, but you will need to think for a moment here, and set it to something that suits your hardware limits and temperament. Set it to 0 if you enjoy watching things explode.

**How it works:**
- Monitors token usage after each API response
- When estimated tokens >= context_limit, triggers shift
- Backs up session to `{session_id}.msgpack.1` (incrementing if exists)
- Removes messages after first user message until `shift_factor` portion freed
- Inserts notification: "[Context shifted: removed N messages (~X tokens)...]"
- Recalculates token estimates and continues

Unlike certain other frameworks that shall remain nameless (but rhyme with "Token Saw"), `lc` doesn't try to outsmart llama.cpp's native context handling. We manage *when* to shift, the inference server handles *how*. This means no mysterious compaction loops, no recursive self-destruction, no 3AM debugging sessions wondering why your agent suddenly forgot how to count. The KV-cache is recomputed only when actually necessary, not on *every*... *single*... *request*.

You'll see the shift notification in the conversation transcript. The model sees it too, so it knows context was lost. Your first user message is always preserved - continuity matters, even when memory doesn't.

**Session Surgery**

Sometimes the model does something spectacularly stupid, like dumping a 375 KB base64 string into the conversation as a tool result, bloating every subsequent request until the session is unusable. Interrupt it with Ctrl-C (decline retention when asked), and cut the mess out:

```
lc> /drop 1
⚠ Drop 2 messages?
  [Tool] 375 KB Shell.exec: "JVBERi0xLjQKJcTl8qXi66O...…"
  [lc]   tool call: Shell.exec
  └─ includes 1 coupled tool message to keep the conversation valid
Drop 2 message(s)? [y/N] y
✓ Dropped 2 messages (375 KB)
```

`/drop N` removes the last N non-system messages. Tool calls and their results are treated as atomic units; if you drop a tool result, its originating tool-call message goes with it, so the session stays structurally valid for the model API. Confirm with `y`, and the session is backed up to a numbered file first, then token accounting is recalculated and the modified session saved.

### Session Inspection & Streaming

You want a fancy new UI? We already have UI at home. But okay, sometimes you want to watch the chaos unfold in style. Or maybe you just want to review what happened while you were making coffee.

**Inspect a session (one-shot):**
```bash
# Dump to terminal
$ lc --inspect-session "docs-refactor"

# Save to file for later analysis
$ lc -S "debug_session" > session_log.md
```

**Stream a live session (follow mode):**
```bash
# Watch session updates in real-time
$ lc --inspect-session "docs-refactor" --follow

# Pipe to your favorite markdown viewer for instant UI
$ lc -S "docs-refactor" -F | mdless
$ lc -S "docs-refactor" -F | glow
$ lc -S "docs-refactor" -F | bat --language=markdown

# Redirect it to a file and watch the chaos unfold in Obsidian
$ lc -S "docs-refactor" -F > ~/Notes/its_happening.md

# Start follower before the session exists (useful for automation)
$ lc -S "my_session" -F | mdless
# (in another terminal) $ lc -n "my_session" -i
```

**Acceptable for:**
- Monitoring long-running tasks from another terminal
- Creating a "heads-up display" with your markdown renderer of choice
- Logging session activity for later review
- Pretending you're in a cyberpunk fantasyscape watching an AI work

**How it works:**
- On first run, prints the complete conversation history
- Incrementally renders only new messages as they appear
- If the session doesn't exist yet, waits rather impatiently for it to appear
- Handles session deletion/reappearance gracefully

### Pipe/stdin/stdout Support

`lc` can receive input via pipes:

**Case 1: Piped content IS the prompt**
```bash
$ (echo "Summarize this log file"; cat ./logfile.txt) | lc
```

**Case 2: Piped content is context for your command**
```bash
$ date | lc "If it's night-time and lights are on, turn them off"
$ cat data.csv | lc "Find anomalies in this data"
```

When both a command argument and stdin are provided, stdin is inserted as a separate user message before your command. The model sees:
1. "[Received via stdin]: (piped content)"
2. "(your command argument)"

You can also pipe or redirect output *from* `lc`:

```bash
$ cat contacts.csv | lc "Create a sorted, markdown-formatted contact sheet" > Contacts.md
```

**Configuration** (in `~/.lc/config`):
```ini
[stdin]
  max_text_bytes = 16384     # Truncate text after this limit
  max_binary_bytes = 512     # Hex dump limit for binary data
```

Binary data is automatically detected and formatted as a hex dump with a warning to the model that the data may be unintentional.

## Writing Tools

Tools are just Python. Write a `Toolkit`:

```python
from lc.toolkit import Toolkit, tool

class MyTools(Toolkit):
    @tool(gate_level=0, modality="text")
    def hello(self, name: str) -> str:
        """Say hello to someone."""
        return f"Hello, {name}! Working in: {self.context.session.working_dir}"
```

Then drop your toolkits into `~/.lc/tools`. That's it. No YAML schemas. No protobuf definitions. Just code.

See [examples](docs/examples/tools) to get started.

## Writing Resolvers

Resolvers provide context for the system prompt:

```python
from lc.resolver import Resolver, Context

class GitResolver(Resolver):
    def resolve(self, context: Context):
        # Return dict of variables, or None
        return {"git_branch": "main"} if is_git_repo() else None
```

## Writing Skills

Skills for `lc` are different. They can contain anything needed to do anything. Documentation, domain knowledge, operating procedures, tools, code, a pre-compiled Commodore 64 emulator to pretend you're still young. Needless to say, this is frightening. You be the judge on how to handle this.

Create the skills you need, and drop them in `~/.lc/skills/`:

```
skills/
└── database/
    ├── SKILL.md          # Procedures and guidelines
    └── __init__.py       # Optional tools
```

Skills load on demand (or pin them to load immediately). The agent can request skills it needs.

See [examples](docs/examples/skills) to get started.

## Writing Quirks

Models are just *perfect*. Except when they're not. When your local Qwen decides tool calls suddenly belong *inside* thinking blocks, or when Kimi starts communicating exclusively in interpretive dance, quirks step in to clean up the mess.

Quirks are surgical patches for model-specific eccentricities. Drop them in `~/.lc/quirks/`:

```python
# ~/.lc/quirks/my_weird_model_fix.py
quirk_id = "my_model.edge_case"

def handle(response: dict) -> dict:
    # Fix the madness before it propagates
    if "thinking" in response and "command" in response["thinking"]:
        response["tool_calls"] = extract_from_thinking(response)
    return response
```

Apply to your model definitions with `quirks = quirk_id, other_quirk_id`.

They load on startup and transform responses in-flight. Use sparingly. If you find yourself writing more than a few, consider that the problem might be your prompt. Or your life choices.

**Built-in Quirks:**

- `qwen3.5_tool_thoughts`: Fixes Qwen3.5-specific tool calling outputs being emitted inside thinking blocks.

## Speaking & Listening

Your fingers have served you well. Decades of poking at ABS cuboids has carved neural pathways in your motor cortex that will never fully heal. It may happen - perhaps while softly surrendering to the undeniable fact that speaking *is* easier than typing - that you want to... *talk*... to the machine.

Therefore, `lc` can speak, and listen - If you ask it; configuratively speaking.

**Text-to-Speech**

Set `tts = yes` in your `[display]` section (in truth, "display" has become something of a metaphor for "output", at this point), and `lc` will read its responses aloud. It buffers output intelligently, managing inference and playback chunking, splitting at sentence boundaries, and outputs audio through LXST (or `mplayer`, if you're nostalgic for 2003). Speech generation will start as soon as a reasonable output chunk is available, and run in parallel with output generation - a small mercy for those of us who read faster than we listen, but sometimes prefer not to read at all.

***PS:** Listening to 500 lines of SQL statements is inconvenient, so `lc` has reasonable opinions about __what__ is actually sent off to the speech backend, and what just becomes a "see this code block".*

```ini
[display]
  tts = yes
  player_backend = lxst

[models]
  [[primary]]
    speech_url = http://localhost:1234/v1
    speech_model = voice-model
    voice = default
    speed = 1.0
    voice_format = opus
    voice_language = en
    voice_gain = 0.0 # In dB
```

**Speech-to-Text**

Set `stt = yes`, and the inline editor grows ears. Press `Ctrl+R` or `Ctrl+Space` to toggle recording mode. The editor vanishes, replaced by a `⏺ Listening... 00:42` indicator. Speak your best. Press the shortcut again to stop, and text materializes at your cursor. On failure, an error flashes for *one* second - pay attention.

```ini
[display]
  stt = yes

[models]
  [[primary]]
    transcription_url = http://localhost:1234/v1
    transcription_model = whisper
    transcription_language = en
```

Recording uses LXST's `FileRecorder`, so you'll need LXST installed (`pip install lxst`). Each recording gets a temporary directory that evaporates after transcription. No audio artifacts left behind, like a perfect crime.

**A few things worth knowing:**
- During recording, the editor only responds to `Ctrl+R`, `Ctrl+Space`, or `Ctrl+C`. Don't bother typing; it will ignore this distraction, as all good listeners should.
- If LXST is missing, STT degrades "gracefully" into a silent no-op. No errors, no drama, just quiet disappointment and shattered dreams.
- Both features work entirely offline - if your inference setup does. Your voice never leaves your hardware unless you explicitly route it elsewhere.

You can now hold an actual conversation with your terminal. It remains to be seen whether this is progress or just the terminal stages of a disease we all caught around 1984. Either way, it works.

## Seeing & Hearing

Some models have grown eyes and ears. You can show them a video of your cat knocking over a cup of coffee, and they'll "understand" why you're upset. If your local model supports multimodal input, `lc` can feed it images, video and audio directly.

**Vision**

The filesystem toolkit can show images to the model via `view_image`. The agent detects the image modality, verifies that your model config has vision enabled, and injects the image into the conversation. The model sees it. Hopefully it comprehends it. No guarantees - it's still a neural network trained on the internet, and the internet thinks cats are gods.

**Video**

If your model understands video (and your `llama-server` has `ffmpeg` available), `view_video` works similarly. The video file is sent directly to the model as input. Be warned: videos are large, context-hungry abominations. A 30-second clip will consume upwards of 14,000 tokens.

**Audio**

For models that can hear, the `listen_audio` tool lets the model receive the raw audio data - not a transcription, but the actual waveform (or as close as a base64 string can get to one). This is useful when tone, cadence, or background sounds matter. MP3, WAV and FLAC are supported. OPUS is not - the underlying decoder is `miniaudio`, not `ffmpeg`, and miniaudio is picky. This is `llama.cpp`'s fault, not mine. Although, if you have `ffmpeg` installed, `lc` will attempt to transcode unsupported formats to MP3 for you on the fly.

**Direct Voice Interaction**

In interactive mode, you can bypass transcription entirely and speak directly to the model. Press `Ctrl+S` in the editor to start recording. Speak. Press `Ctrl+S` again. Your voice (or whatever noises you prefer to make) is sent off. The model hears you. You hear it back if TTS is enabled. It's like a phone call, except the other party is a quantized matrix multiplication roadshow running on your graphics card.

Configuration for a fully multimodal model:

```ini
[models]
  [[primary]]
    vision = yes
    video = yes
    video_size_limit = 50
    audio = yes
    audio_size_limit = 50
```

Size limits are in megabytes. Videos and audio files exceeding the limit are rejected before they clog your context window. Yes, this approach is crude, but it's better than nothing, and we can't magically tokenize a video and do the counting before actually tokenizing it, can we?

**A few things worth knowing:**
- The model must support the modality. Loading a text-only model and enabling `video = yes` will not give it eyes. It will just give you error messages.
- Video requires `llama-server` to have `ffmpeg` and `ffprobe` in its `PATH`. If it doesn't, you'll get some confusing log entries on the inference machine.
- Direct voice recording (`Ctrl+S`) converts to MP3 on the fly using `ffmpeg`. If ffmpeg is missing on your system, you'll see an error for one second and the editor will return, ready for typing.

## Safety

`lc` can execute shell commands and destroy your computer. This is a feature, not a bug.

> With great power, etc., etc.

Use `--gate` when experimenting. Use `--gate=3` when letting children use it. Use your judgment: Always.

The tool gating system asks for confirmation before destructive operations. But remember: **you are the final safety mechanism**. Review what it plans to do. The AI does not have your context, your intent or any remorse. But it may very quickly have your backups.

## Limitations

- Does not make your coffee or drink it for you (yet)
- Cannot read your mind (working on it)
- Will not fix your architecture decisions

## Why Not Just Use…

- **Bash scripts?** You enjoy writing them?
- **Python scripts?** For one-offs? Really?
- **ChatGPT?** Copy-paste. Copy-paste. Copy-paste.
- **Other agent frameworks?** 600,000 lines of TypeScript. Docker. Kubernetes. Your data in someone else's "cloud". We rest our case.

## Contributing

Found a bug? Have an improvement? Send me a patch over LXMF. No, I don't use GitHub. Keep it minimal. Keep it auditable. No chit-chat. Resist the urge to add microservices.

## Acknowledgments

- [ConfigObj](https://github.com/DiffSK/configobj) ([BSD 3 Clause License](lc/vendor/CONFIGOBJ_LICENSE.txt))
- [Jinja2](https://github.com/pallets/jinja) ([BSD 3 Clause License](lc/vendor/jinja2/LICENSE.txt))
- [wcwidth](https://github.com/jquast/wcwidth) ([MIT License](lc/vendor/wcwidth/LICENSE.txt))
- The open-source LLM community, for making local inference viable
- The reader, for getting this far without rolling their eyes too hard

---

*"The command line is dead. Long live the command line."*
