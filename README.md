# Vocalysis

**Vocalysis** is a Python package that provides a simple interface to a range of acoustic voice measures using [Praat](https://www.fon.hum.uva.nl/praat/) via the [Parselmouth](https://parselmouth.readthedocs.io/en/stable/) library. It allows researchers and developers to extract meaningful statistics from voice recordings—such as pitch, jitter, shimmer, harmonicity, intensity, and more—without having to manually interact with Praat.

---

## `get_voice_report()`: The Quickest Way to Analyze a Voice Recording

The `get_voice_report()` function is the easiest way to get a comprehensive summary of key voice features from an audio file. It combines several lower-level functions into a single call and returns a dictionary with pitch, jitter, shimmer, harmonicity, intensity, and voicing statistics.

### Example

```python
from vocalysis import get_voice_report

report = get_voice_report("example.wav")

# Access specific values
print(report["Pitch"]["mean_pitch"])       # e.g., '142.537 Hz'
print(report["Shimmer"]["shimmer_local"])  # e.g., '4.123 %'
```

## Helper Functions: Access Individual Acoustic Measures

In addition to `get_voice_report()`, **Vocalysis** provides several lower-level functions that compute individual acoustic measures. These functions can be used on their own if you want more control or only need specific features.

### `measure_pitch()`: Extract Pitch Statistics

The `measure_pitch()` function calculates key pitch statistics (in Hz) from an audio file or Parselmouth objects. You can provide either a file path, a `Sound` object, or a `Pitch` object as input.

```python
from vocalysis import measure_pitch

stats = measure_pitch(audio_path="example.wav")

print(stats["mean"])    # e.g., '142.537 Hz'
print(stats["median"])  # e.g., '140.123 Hz'
```

