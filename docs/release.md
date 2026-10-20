# GitHub and Zenodo release

The intended repository is `GaragaKarthikeya/INSITU-artifact`, version `v1.0.0`.
Repository metadata is already in `CITATION.cff` and `.zenodo.json`; Zenodo
uses `.zenodo.json` when both are present. Do not add a guessed DOI.

1. Create the public GitHub repository, push this isolated repository, and
   inspect its files and `docs/validation.md`.
2. Sign in to [Zenodo](https://zenodo.org/account/settings/github/), link the
   intended GitHub account, sync repositories, and enable
   `GaragaKarthikeya/INSITU-artifact`. Enable the repository **before** publishing its
   first GitHub release.
3. Publish a GitHub release tagged `v1.0.0` using `RELEASE_NOTES.md`.
4. Wait for Zenodo's archive record and verify its authors, license, version,
   source archive, and DOI. Add the actual DOI and badge to the repository
   afterwards. Record any DOI metadata changes in the next source revision.

GitHub CLI commands, once authenticated and the local repository is committed:

```bash
gh repo create GaragaKarthikeya/INSITU-artifact --public --source=. --remote=origin --push
# Enable this repository in Zenodo before the next command.
gh release create v1.0.0 --target main --title 'INSITU v1.0.0' \
  --notes-file RELEASE_NOTES.md
```

If that GitHub repository already exists, inspect its contents first and attach
the appropriate remote; do not overwrite an existing project. The accompanying
source ZIP is also suitable for manual upload, but this release is prepared for
the requested GitHub integration.

Official instructions:
[enable a repository](https://help.zenodo.org/docs/github/enable-repository/),
[software metadata](https://help.zenodo.org/docs/github/describe-software/), and
[archive a release](https://help.zenodo.org/docs/github/archive-software/).
