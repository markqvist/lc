---
name: xkcd_explorer
description: Explore XKCD comics randomly or by topic
version: 1.0.0
triggers:
  - xkcd
  - comic
  - random comic
pinned: false
---

# XKCD Explorer Skill

A skill for viewing and exploring XKCD comics randomly and understanding their humor through alt text.

## When to Use

Use this skill when:
- You want to discover random XKCD comics
- You want to explore a specific XKCD topic
- You're curious about what makes a comic funny

## Available Tools

- `get_random_comic`: Get a random XKCD comic with title, image URL, and alt text
- `view_comic`: Display a specific XKCD comic image
- `explain_humor`: Explain why a comic is funny using its alt text

## Guidelines

1. Always provide context when calling `explain_humor` - the comic title and number
2. When viewing comics, view the image first, then explain the humor
3. XKCD humor often involves:
   - Mathematical and scientific concepts explained simply
   - Computer science jokes
   - Relationships and social awkwardness
   - Pop culture references
   - Wordplay and puns

## XKCD Features to Note

- Numbered comics (e.g., #1234)
- Regularly updated since 2005
- Randall Munroe is the creator
- Sometimes interactive comics or special formats