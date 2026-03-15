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

If you want a bit more context, read [The Guide](./GUIDE.md) or [Chrome Horizons](./Chrome_Horizons.md).

## The Philosophy

`lc` was born from a simple observation: Most agentic frameworks are bloated, opaque, and designed for cloud-scale Kubernetes deployments when what you actually need is to rename some files without reading seventeen man pages.

Humanity's Last Command is different:

- **Truly local**: Runs on your machine, with your models, on your data.
- **Auditable**: Spartan codebase, readable code, no 600k-line dependency nightmares.
- **Universal**: Does anything, including what other frameworks won't. No restrictions, no training wheels.
- **Explicit**: You see what it's doing. No hidden API calls, no data exfiltration.
- **Extensible**: Teach it new tricks with simple Python or compiled binaries.
- **Actually Works**: Novel concept, I know.

## Danger Zone

Don't blame me when it deletes your thesis (you used `--gate`, right?). Anything you can imagine, `lc` will happily do, including wiping your drives clean. There is no warranty, and if there was, it is now void by visiting this page.

Wanted to run an `IQ1_S` quant, and the logit gods decided `parted` was a better choice than `free`? Entropy had it's way.

By using `lc`, you gain the full power, and bear the full responsibility for all the actions you delegate to the machine. No guard-rails, no guarantess, no restrictions.

Also, don't assume any safety or security features actually work. At least half of it is still placeholders. I wrote this while drunk and riding a goat through the narrow streets of Venice. Someday, I might test everything, but that day is not today.

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

While the concept of `lc` had been playing pong in my head for some time, I have so far spent `<=` 3 days on this. Funny how it already works better than OpenClaw.

Things will change, rapidly. Data formats might break, arguments change. Your kitchen may disappear. If none of that scares you:

```bash
# Obtain a release .whl file, either by floppy
# or download. Then install with:
pip install ./lc-0.3.6-py3-none-any.whl

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
[model]
backend = openai
base_url = http://localhost:1234/v1
model = local-model
api_key = not-needed-for-local

[toolkits]
builtin = filesystem, shell, cryptography

[resolvers]
builtin = environment, filesystem, system
```

Edit system prompt templates, et cetera, in `~/.lc/templates`.

## But... How do I make it take over the world?

1. Download `llama.cpp` for your specific CPU and GPU architecture, grab a good local model like `GLM 4.7 Flash` or `Qwen 3.5 35B-A3B`.
2. Install `lc` and point it the config to your local `llama-server` instance.
3. Invoke `lc` from a periodic `cron` job with a completely open-ended prompt.

Your job is done. Watch the chaos unfold. Or just go to sleep.

## But... How do I connect it to Anthropic?

You don't.

## Usage

### One-Shot Mode (Default)

```bash
$ lc "Find all Python files modified in the last week and count lines of code"
```

### Interactive Mode

```bash
$ lc -i
lc> Read the README
lc> Now summarize it in the style of a Victorian novel
lc> Actually, don't
```

### With Safety Gating

```bash
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

### Context Management (Or: How I Learned to Stop Worrying and Love the KV-Cache)

LLMs have context windows. You may have noticed. When you feed them more tokens than their little silicon brains can handle, they don't gracefully page to disk like a proper operating system. They just break. Or hallucinate. Or start speaking in tongues.

`lc` handles this with context shifting. When your session grows too large, it quietly removes the oldest messages (keeping your first user message and system prompt for continuity), inserts a notification that context was shifted, and carries on. The session is backed up to a numbered file before each shift, so your complete history is preserved.

**Configuration:**
```ini
[model]
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

Unlike certain other frameworks that shall remain nameless (but rhyme with "ShmopenClaw"), `lc` doesn't try to outsmart llama.cpp's native context handling. We manage *when* to shift, the inference server handles *how*. This means no mysterious compaction loops, no recursive self-destruction, no 3AM debugging sessions wondering why your agent suddenly forgot how to count. The KV-cache is recomputed only when actually necessary, not on *every*... *single*... *request*.

You'll see the shift notification in the conversation transcript. The model sees it too, so it knows context was lost. Your first user message is always preserved - continuity matters, even when memory doesn't.

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

## Writing Resolvers

Resolvers provide context for the system prompt:

```python
from lc.resolver import Resolver, Context

class GitResolver(Resolver):
    def resolve(self, context: Context):
        # Return dict of variables, or None
        return {"git_branch": "main"} if is_git_repo() else None
```

## Skills

Skills for `lc` are different. They can contain anything needed to do anything. Documentation, domain knowledge, operating procedures, tools, code, a pre-compiled Commodore 64 emulator to pretend you're still young. Needless to say, this is frightening. You be the judge on how to handle this.

Create the skills you need, and drop them in `~/.lc/skills/`:

```
skills/
└── database/
    ├── SKILL.md          # Procedures and guidelines
    └── __init__.py       # Optional tools
```

Skills load on demand (or pin them to load immediately). The agent can request skills it needs.

## Safety

`lc` can execute shell commands and destroy your computer. This is a feature, not a bug.

> With great power, etc., etc.

Use `--gate` when experimenting. Use `--gate=3` when letting children use it. Use your judgment: Always.

The tool gating system asks for confirmation before destructive operations. But remember: **you are the final safety mechanism**. Review what it plans to do. The AI does not have your context, your intent or any remorse. But it may very quickly have your backups.

## Limitations

- Does not make your coffee or drink it for you (yet)
- Cannot read your mind (working on it)
- Will not fix your architecture decisions
- Context windows are finite; very complex tasks may need breaking down

## Why Not Just Use…

- **Bash scripts?** You enjoy writing them?
- **Python scripts?** For one-offs? Really?
- **ChatGPT?** Copy-paste. Copy-paste. Copy-paste.
- **Other agent frameworks?** 600,000 lines of TypeScript. Docker. Kubernetes. Your data in someone else's "cloud". We rest our case.

## Contributing

Found a bug? Have an improvement? Send me a patch over LXMF. No, I don't use GitHub. Keep it minimal. Keep it auditable. No chit-chat. Resist the urge to add microservices.

## Acknowledgments

- To the open-source LLM community, for making local inference viable
- To the reader, for getting this far without rolling their eyes too hard

---

*"The command line is dead. Long live the command line."*
