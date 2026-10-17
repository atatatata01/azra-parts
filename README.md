# AZRA community parts

Free parts for [AZRA](https://github.com/atatatata01) — shared by AZRA users, usable by anyone,
for anything. **Every part in this repository is dedicated to the public domain under
[CC0 1.0](LICENSE)**: no attribution required, commercial use allowed.

## Using parts

Open AZRA → **Library** → **Community**. The tab reads [`index.json`](index.json) from this
repository, shows the thumbnails, and downloads a part into your local library in one click. It
works whether or not anyone's PC is on — files are served by GitHub.

## Sharing a part

In AZRA, **Save as Part**, tick **Share with the community (CC0)**, pick a category. No GitHub
account needed. Your part is checked automatically and becomes a pull request here; it is
published when the maintainer merges it.

By sharing you confirm the part is your own work (or already public domain) and you dedicate it to
the public domain under CC0 1.0.

## Layout

```
parts/<category>/<slug>/part.flb    the part (AZRA library format)
parts/<category>/<slug>/thumb.png   thumbnail
parts/<category>/<slug>/part.json   name, category, tags, author (optional), license (CC0-1.0),
                                    format version, sha256 + size of both files, content stats
index.json                          generated from every part.json — do not edit by hand
```

`<slug>` = readable name + the first 8 hex digits of the part's SHA-256, so two parts with the same
name never collide. Categories: `architecture`, `characters`, `furniture`, `hard-surface`,
`mechanical`, `nature`, `props`, `vehicles`, `weapons`, `misc`.

## Moderation

1. The upload server validates every part with AZRA's own loader in a sandboxed process before a
   pull request is opened (size caps, format version, structural checks, thumbnail, hashes).
2. This repository's CI re-validates the PR (`.github/workflows/validate-parts.yml`, pinned
   `azra-part-check` build) and comments the result.
3. The maintainer reviews and merges. `index.json` is rebuilt automatically after the merge.

Report a problem with a published part by opening an issue with its folder path.
