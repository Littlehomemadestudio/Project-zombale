# Dead Signal

**Dead Signal** is an original offline-first 2D corridor survival shooter for Android. It takes broad inspiration from the tension of holding a narrow defensive line, while using its own title, visual language, code, encounter pacing and presentation.

This is the first playable foundation build. The project is intentionally isolated in `android-game/`; the repository's existing Python/Bale projects remain untouched.

## Current build

- Native Android application written in Kotlin.
- Portrait gameplay rendered through a custom `SurfaceView` canvas loop.
- Drag to aim and hold to fire.
- Three enemy archetypes with distinct health, speed and rewards.
- Sidearm and carbine available from the start; breacher unlocks at 180 score.
- Magazine/reserve ammo, reload timing and weapon switching.
- Five-sector Cleanup run and endless Defense mode.
- Barricade damage, repair charges, player health and wave intermissions.
- Local personal-best score storage; no account or network connection required.
- Deterministic simulation tests for spawn reproducibility, firing, reload and loadout.

## Controls

| Input | Action |
| --- | --- |
| Touch and drag in the corridor | Aim |
| Hold in the corridor | Automatic fire |
| Patch button | Restore barricade integrity (limited charges) |
| Reload button | Reload the current magazine |
| Swap button | Change weapon |
| Tap the upper-right HUD area | Pause |
| Tap while paused | Resume |
| Tap after a run ends | Restart the selected mode |

The Breacher unlocks after reaching 180 score in a run. Cleanup is a finite five-sector operation; Defense continues through escalating waves.

## Build

Requirements: JDK 17, Android SDK platform 35 and Android build-tools installed.

From this directory:

```bash
gradle testDebugUnitTest assembleDebug
```

Install the debug APK on a connected device:

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

GitHub Actions builds and uploads `app-debug.apk` for pushes to the `flat-zombie-android` branch and manual workflow dispatches. The workflow runs JVM unit tests before assembling the APK.

## Known limitations in this foundation build

- Combat is a first vertical slice; tuning, additional enemy behaviors, weapon feedback and more encounter variety remain.
- The visual presentation is procedurally drawn with original vector-like shapes; bespoke sprite sheets, animation polish, sound and haptics are not included yet.
- Progress currently stores only the personal-best score. Unlock persistence, settings and richer statistics remain.
- Device performance and touch feel still need physical-device testing across aspect ratios and refresh rates.

## Credits

Original project code and procedural artwork created for this repository. No Flat Zombies code, art, sound or level layouts are included. The reference is used only for high-level genre mechanics.
