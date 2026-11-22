# LjL-Droid

An F-Droid repository for LjL's Android apps, so the family can install them and get updates
automatically:

| App | Package |
|---|---|
| [EarthPing](https://github.com/LjLies/EarthPing) | `io.github.ljlies.earthping` |
| [WakeBridge](https://github.com/LjLies/WakeBridge) | `io.github.ljlies.wakebridge` |

**Repository address:** <https://ljlies.github.io/LjL-Droid/repo>

There is no server to run. GitHub Actions builds the repository and GitHub Pages serves it.

## How it works

1. Each app's own build workflow publishes a **GitHub Release** `v<versionName>` with the APK
   signed with the release key, whenever a push to its `main` changes `versionName`.
2. Every hour, [`publish.yml`](.github/workflows/publish.yml) here downloads the newest signed
   APKs from those releases ([`scripts/fetch_releases.py`](scripts/fetch_releases.py)), builds
   and signs the F-Droid index with `fdroid update`, and deploys it to GitHub Pages. When nothing
   changed, it stops before deploying.
3. F-Droid on the phones checks the repository and offers the update.

The apps aren't rebuilt here: the repository ships exactly the APKs from the releases. Their
metadata ([`metadata/`](metadata)) only accepts APKs signed with LjL's release key
(`AllowedAPKSigningKeys`), so a debug build or anyone else's APK can't get in.

The newest 3 releases of each app are offered (`keep:` in [`apps.yml`](apps.yml)). Older ones go
to the archive repository.

## Adding an app

1. Give the app the same signing and release steps as the others (see
   [LjLies/Android-Development](https://github.com/LjLies/Android-Development) for the signing
   part).
2. Add its repository to [`apps.yml`](apps.yml).
3. Add `metadata/<applicationId>.yml`, copying an existing one.

## Setting it up (once)

### 1. Make this repository public

GitHub Pages only works for private repositories on paid plans. The published site is public
anyway, and nothing secret is stored here: the keys are in encrypted secrets.

**Settings → General → Danger Zone → Change visibility → Public.**

### 2. Name the branch `main`

The workflow publishes from `main`. If the repository's only branch has another name:
**Settings → General → Default branch → rename** to `main`.

### 3. Turn on GitHub Pages

**Settings → Pages → Build and deployment → Source: GitHub Actions.**

### 4. Create the repository signing key

F-Droid checks that the index is signed by the same key every time. That key is what the phones
trust, separate from the app release key. Create it on your computer, in the same private folder
as the release key:

```bash
keytool -genkeypair -v -keystore ~/android-keys/fdroid-repo.p12 -storetype PKCS12 -alias repo -keyalg RSA -keysize 4096 -validity 10000 -dname CN=LjL-Droid
```

```bash
chmod 600 ~/android-keys/fdroid-repo.p12
```

Back it up with the release key. If it's lost, a new key means everyone has to remove the
repository from F-Droid and add it again. (The apps stay installed and keep updating.)

### 5. Add the secrets

Here, in **LjLies/LjL-Droid**:

```bash
base64 -w0 ~/android-keys/fdroid-repo.p12 | gh secret set FDROID_KEYSTORE --repo LjLies/LjL-Droid
```

```bash
gh secret set FDROID_KEYSTORE_PASS --repo LjLies/LjL-Droid
```

Private app repositories need a token so that this workflow can read their releases: a
[fine-grained personal access token](https://github.com/settings/personal-access-tokens/new)
(resource owner LjLies, **Only select repositories**, permission **Contents: Read-only**), set
with `gh secret set APPS_TOKEN --repo LjLies/LjL-Droid`. None is needed while every app in
`apps.yml` is public.

### 6. Publish

Merge the release-step changes in the app repositories. Each one's next build on `main`
publishes its current version as a release. Then run **Actions → Publish → Run workflow** here
(or wait for the hourly run). The run's summary shows the "add to F-Droid" link.

## Installing on a phone

1. Install [F-Droid](https://f-droid.org) (or Droid-ify, Neo Store, …).
2. On the phone, open <https://ljlies.github.io/LjL-Droid/repo/> and tap the link, or scan its
   QR code from another screen. F-Droid asks to add the repository.
3. Find the apps in F-Droid and install them.

An app installed earlier from a **debug** build has a different signature: Android refuses the
update. Uninstall it once (that deletes its data, so note its settings), then install it from
F-Droid.
