# Installing NutriMe

NutriMe runs entirely on your own computer. Nothing is hosted for you, and
your household's health information never leaves the machine.

## What you need

- Windows 10/11 or macOS
- About 10 GB free disk space (most of it is the local model)
- For plan-making: a computer that can run an 8-billion-parameter model.
  A recent laptop is enough; a graphics card makes it faster. Search,
  Tonight and the grocery list work without the model.

## Install

1. Download NutriMe (green **Code** button → *Download ZIP* on GitHub, or
   `git clone`) and unzip it somewhere permanent, e.g. `Documents\NutriMe`.
2. Run the installer from inside that folder:

   **Windows** (PowerShell):

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\install-windows.ps1
   ```

   **macOS** (Terminal, needs [Homebrew](https://brew.sh)):

   ```sh
   ./scripts/install-macos.sh
   ```

3. Open **http://localhost:8765** in your browser.

The installer adds Ollama and uv if they're missing, sets up NutriMe,
copies the bundled recipe collection, downloads the local model (one time,
several GB), takes a first backup, and starts NutriMe whenever you sign in.
Running it again is safe; it only does what's still missing.

## Everyday care

| Task | Command |
|---|---|
| Is everything working? | `uv run nutrime doctor` (also on the Profile page under *System check*) |
| Back up | `uv run nutrime backup` — writes a zip to `~/.nutrime/backups`. Copy it somewhere else too. |
| Restore | Stop NutriMe, then `uv run nutrime restore <zip> --force`. What it replaces is backed up first. |
| Update | Download the new version over the old folder (or `git pull`), then run the installer again. Database updates apply automatically on the next start. |
| Stop starting at sign-in | `install-windows.ps1 -Uninstall` or `install-macos.sh --uninstall`. Your data stays. |

Run commands from the NutriMe folder. Your data lives in `~/.nutrime`
(`%USERPROFILE%\.nutrime` on Windows) unless you set `NUTRIME_DATA_DIR`.

## Known limits

- **Phones:** NutriMe listens only on this computer (`localhost`) because it
  has no sign-in yet. Opening it from a phone on the same Wi-Fi needs the
  household-network work in issue #12.
- **Sleep:** a laptop that sleeps stops serving. Keep it awake while
  plugged in if others use NutriMe from it.
- **Games and the model:** a game and the local model compete for the
  graphics card; plan-making may be slow while gaming.
- The installers were written for the Windows primary host and macOS; report
  anything that fails with the output of `nutrime doctor`.
