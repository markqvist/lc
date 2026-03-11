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

## The Philosophy

`lc` was born from a simple observation: most agentic frameworks are bloated, opaque, and designed for cloud-scale Kubernetes deployments when what you actually need is to rename some files without reading seventeen man pages.

This is different:

- **Local-first**: Runs on your machine, with your models, on your data.
- **Auditable**: Small codebase, readable code, no 600k-line dependency nightmares.
- **Explicit**: You see what it's doing. No hidden API calls, no data exfiltration.
- **Extensible**: Teach it new tricks with simple Python.
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

You can freely copy, share and distribute `lc` in binary or source form, as long as this entire `README.md` file, without any modifications is distributed along with it, and displayed prominently to potential users and the occasional random passerby.

## Installation

```bash
# For now: Install directly from repository
# No guarantee the code is in a working state
# at the point in time you do this.
pip install git+https://github.com/markqvist/lc

# When I get my act together and publish to PyPI:
# pip install some_funky_package_name
```

Or, if you prefer living on the edge of the possible:

```bash
git clone https://github.com/markqvist/lc
cd lc
pip install -e .
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
builtin = filesystem, shell

[resolvers]
builtin = environment, filesystem, system
```

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
$ lc --gate "Delete all files in /tmp"
# lc will ask for confirmation before executing - maybe
```

Gate levels:
- `0`: Read-only operations (always allowed)
- `1`: File writes (gated)
- `2`: Shell execution, read-only (gated)
- `3`: Destructive execution (gated)

### Session Persistence

```bash
$ lc -i --resume
# Continue previous session
```

Sessions are stored as msgpack in `~/.lc/sessions/`. They're your business, not mine.

## Writing Tools

Tools are just Python. Create a `Toolkit`:

```python
from lc.toolkit import Toolkit, tool

class MyTools(Toolkit):
    @tool
    def hello(self, name: str) -> str:
        """Say hello to someone."""
        return f"Hello, {name}! Working in: {self.context.session.working_dir}"
```

Register in config:

```ini
[toolkits]
custom = mymodule.MyTools
```

That's it. No YAML schemas. No protobuf definitions. Just code.

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

Skills bundle domain knowledge. Drop them in `~/.lc/skills/`:

```
skills/
└── database/
    ├── SKILL.md          # Procedures and guidelines
    └── __init__.py       # Optional tools
```

Skills load on demand (or pin them to load immediately). The agent can request skills it needs.

## Safety

`lc` can execute shell commands and destroy your computer. This is a feature, not a bug. With great power, etc., etc.

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
