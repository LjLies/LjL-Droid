# LjL-Droid

An F-Droid repository for LjL's Android apps:

| App | Package |
|---|---|
| [EarthPing](https://github.com/LjLies/EarthPing) | `io.github.ljlies.earthping` |
| [WakeBridge](https://github.com/LjLies/WakeBridge) | `io.github.ljlies.wakebridge` |

**Repository address:** <https://ljlies.github.io/LjL-Droid/repo>

## Installing on a phone

1. Install [F-Droid](https://f-droid.org) (or Droid-ify, Neo Store, …).
2. On the phone, open
   [this link](https://fdroid.link/#https://ljlies.github.io/LjL-Droid/repo?fingerprint=A54E24739F3816E0BDD8DCBF87FB3B72E744462E4E4E8DE1A5914713F6190DE0),
   or scan the QR code at <https://ljlies.github.io/LjL-Droid/repo/> from another screen.
   F-Droid asks to add the repository.
3. Find the apps in F-Droid and install them. Updates are then offered like any other app's.

The repository's signing key fingerprint is
`A54E24739F3816E0BDD8DCBF87FB3B72E744462E4E4E8DE1A5914713F6190DE0`.

An app installed earlier from a **debug** build has a different signature, and Android refuses the
update. Uninstall it once (that deletes its data, so note its settings), then install it from
F-Droid.

## How it works

There is no server: GitHub Actions builds the repository and GitHub Pages serves it.

1. Each app's own build workflow publishes a **GitHub Release** with the APK signed with the
   release key.
2. Every hour, [`publish.yml`](.github/workflows/publish.yml) downloads the newest signed APKs
   from those releases ([`scripts/fetch_releases.py`](scripts/fetch_releases.py)), along with the
   app's fastlane metadata (descriptions, changelogs, screenshots) from its newest release. It
   then builds and signs the F-Droid index with `fdroid update` and deploys it to GitHub Pages.
   When nothing changed, it stops before deploying.
3. F-Droid on the phones checks the repository and offers the update.

The apps aren't rebuilt here: the repository ships exactly the APKs from the releases. Their
metadata ([`metadata/`](metadata)) only accepts APKs signed with LjL's release key
(`AllowedAPKSigningKeys`), so a debug build or anyone else's APK can't get in.

The newest 3 releases of each app are offered (`keep:` in [`apps.yml`](apps.yml)). Older ones go
to the archive repository.

## Adding an app

1. Give the app the same signing and release steps as the others.
2. Add its repository to [`apps.yml`](apps.yml).
3. Add `metadata/<applicationId>.yml`, copying an existing one. Texts and screenshots in the app's
   own `fastlane/metadata/android/` take precedence over the ones there.
