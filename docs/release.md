# GitHub and Zenodo release

## Published version 1.0.0

- [GitHub release](https://github.com/GaragaKarthikeya/INSITU-artifact/releases/tag/v1.0.0)
- [Zenodo record](https://zenodo.org/records/23510637)
- Version DOI: [10.5281/zenodo.23510637](https://doi.org/10.5281/zenodo.23510637)
- All-versions DOI: [10.5281/zenodo.23510636](https://doi.org/10.5281/zenodo.23510636)
- Archived source commit: `ca01bb59ae3d7aa1a8a1e1a915985213c8d34470`

The Zenodo record identifies all three authors, the MIT license, version 1.0.0,
and a source ZIP. The DOI references were added to the repository after
archiving; the `v1.0.0` tag and its archived source remain unchanged.
The published ZIP's MD5 matches Zenodo's metadata, and all 234 file hashes
in its embedded `SHA256SUMS` were verified after downloading it from Zenodo.

## Procedure for future releases

1. Update the version in `pyproject.toml`, `CITATION.cff`, and `.zenodo.json`;
   write release notes and rerun the appropriate checks. Refresh `SHA256SUMS`.
2. Confirm that the repository is still enabled in
   [Zenodo's GitHub settings](https://zenodo.org/account/settings/github/).
   The integration was enabled before publishing version 1.0.0.
3. Push the changes and publish a GitHub release with a new version tag.
   Keep previously published tags unchanged.
4. Verify the new Zenodo record, version, metadata, source ZIP, and assigned
   DOI. Update the version-specific citation and README badge with that DOI.

Zenodo uses `.zenodo.json` when both it and `CITATION.cff` are present. The
all-versions DOI stays the same across versions; each release gets its own DOI.

Official instructions:
[enable a repository](https://help.zenodo.org/docs/github/enable-repository/),
[software metadata](https://help.zenodo.org/docs/github/describe-software/), and
[archive a release](https://help.zenodo.org/docs/github/archive-software/).
