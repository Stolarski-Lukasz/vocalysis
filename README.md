# Vocalysis

**Vocalysis** is a Python package that provides a simple interface for extracting a range of acoustic voice measures using [Praat](https://www.fon.hum.uva.nl/praat/) via the [Parselmouth](https://parselmouth.readthedocs.io/en/stable/) library.

Below is a list of all available functions, along with brief descriptions and usage examples.

&nbsp;
## `measure_pitch()`

Computes basic pitch statistics (in Hz) from an audio file (WAV or another format supported by Praat) or a precomputed Parselmouth object.

The function returns a dictionary with the following keys:

- `'median'`: Median pitch
- `'mean'`: Mean pitch
- `'std'`: Standard deviation of pitch
- `'min'`: Minimum pitch
- `'max'`: Maximum pitch

All values are formatted as strings with the "Hz" unit (e.g., `"142.537 Hz"`).

**Example:**

```python
from vocalysis import measure_pitch

stats = measure_pitch(audio_path="path/to/speech.wav")
print(stats["mean"])  # e.g., '142.537 Hz'
```

&nbsp;
## `measure_pulses()`

Computes pulse-related statistics from an audio file (WAV or another format supported by Praat) or a precomputed Parselmouth object.

The function returns a dictionary with the following keys:

- `'num_pulses'`: Total number of glottal pulses  
- `'num_periods'`: Number of periods between pulses  
- `'mean_period'`: Mean period in seconds (e.g., `"0.0050364095 seconds"`), or `None` if not computable  
- `'std_period'`: Standard deviation of period in seconds (formatted as string), or `None`  

**Example:**

```python
from vocalysis import measure_pulses

stats = measure_pulses(audio_path="path/to/speech.wav")
print(stats["mean_period"])  # e.g., '0.0050364095 seconds'
```

&nbsp;
## `measure_voicing()`

Computes voicing statistics from an audio file (WAV or another format supported by Praat) or precomputed Parselmouth objects.

The function returns a dictionary with the following keys:

- `'unvoiced_fraction'`: Percentage of unvoiced frames (e.g., `"12.345%"`)  
- `'num_voice_breaks'`: Number of detected voice breaks  
- `'degree_voice_breaks'`: Total duration of voice breaks as a percentage of the signal duration (e.g., `"4.789%"`)  

**Example:**

```python
from vocalysis import measure_voicing

stats = measure_voicing(audio_path="path/to/speech.wav")
print(stats["num_voice_breaks"])  # e.g., 15
```

&nbsp;
## `measure_jitter()`

Measures jitter statistics from an audio file (WAV or another format supported by Praat) or precomputed Parselmouth objects.

The function returns a dictionary with the following keys:

- `'jitter_local'`: Local jitter as a percentage (e.g., `"4.123%"`)  
- `'jitter_local_absolute'`: Local absolute jitter in seconds (e.g., `"0.000123"`)  
- `'jitter_rap'`: Relative average perturbation (RAP) jitter as a percentage  
- `'jitter_ppq5'`: 5-point period perturbation quotient (PPQ5) jitter as a percentage  
- `'jitter_ddp'`: Difference of differences of periods (DDP) jitter as a percentage  

**Example:**

```python
from vocalysis import measure_jitter

stats = measure_jitter(audio_path="path/to/speech.wav")
print(stats["jitter_local"])  # e.g., '4.123%'
```

&nbsp;
## `measure_shimmer()`

Measures shimmer statistics from an audio file (WAV or another format supported by Praat) or precomputed Parselmouth objects.

The function returns a dictionary with the following keys:

- `'shimmer_local'`: Local shimmer as a percentage (e.g., `"8.340%"`)  
- `'shimmer_local_dB'`: Local shimmer in decibels (e.g., `"0.123 dB"`)  
- `'shimmer_apq3'`: 3-point amplitude perturbation quotient (APQ3) as a percentage  
- `'shimmer_apq5'`: 5-point amplitude perturbation quotient (APQ5) as a percentage  
- `'shimmer_apq11'`: 11-point amplitude perturbation quotient (APQ11) as a percentage  
- `'shimmer_dda'`: Difference of differences of amplitudes (DDA) as a percentage  

**Example:**

```python
from vocalysis import measure_shimmer

stats = measure_shimmer(audio_path="path/to/speech.wav")
print(stats["shimmer_local"])  # e.g., '8.340%'
```

&nbsp;
## `measure_intensity()`

Measures intensity statistics (in decibels) from an audio file (WAV or another format supported by Praat) or precomputed Parselmouth objects.

The function returns a dictionary with the following keys:

- `'intensity_median'`: Median intensity  
- `'intensity_mean'`: Mean intensity  
- `'intensity_std'`: Standard deviation of intensity  
- `'intensity_min'`: Minimum intensity  
- `'intensity_max'`: Maximum intensity  

**Example:**

```python
from vocalysis import measure_intensity

stats = measure_intensity(audio_path="path/to/speech.wav")
print(stats["intensity_mean"])  # e.g., '81.833 dB'
```

&nbsp;
## `get_voice_report()`

Generate a voice report, similar to Praat's, from an audio file (WAV or any format supported by Praat).  
The function integrates several lower-level analysis functions provided by `vocalysis`.

### Returns:
- `dict`: A dictionary containing acoustic measurements with keys:
  - `'Pitch'`
  - `'Pulses'`
  - `'Voicing'`
  - `'Jitter'`
  - `'Shimmer'`
  - `'Intensity'`

### Example:
```python
>>> report = get_voice_report(audio_path="path/to/speech.wav")
>>> print(report["Pitch"]["mean"])
'142.537 Hz'
>>> print(report["Jitter"]["local_jitter"])
'4.123 %'
```

&nbsp;
## `measure_spectral_shape()`
This function calculates four commonly used spectral features to describe the shape of the spectrum.

**Returns:**  
A dictionary with the following keys:
- `'center_of_gravity'`: Spectral centroid in Hz (e.g. `"2457.31 Hz"`)
- `'std'`: Spectral standard deviation in Hz (e.g. `"1021.87 Hz"`)
- `'skewness'`: Spectral skewness (unitless)
- `'kurtosis'`: Spectral kurtosis (unitless)

**Example:**
```python
>>> from vocalysis import measure_spectral_shape
>>> stats = measure_spectral_shape(audio_path="path/to/speech.wav")
>>> print(stats["center_of_gravity"])
'2457.31 Hz'
```

&nbsp;
## `measure_spectral_shape()`
This function computes six key statistics for each of the first four formants using Praat's Burg method:

**Returns:**  
A dictionary with the following keys for each formant F1–F4:
- `'F1_mean'`, `'F1_std'`, `'F1_min'`, `'F1_max'`, `'F1_median'`, `'F1_bandwidth_median'`
- `'F2_mean'`, `'F2_std'`, ..., `'F4_bandwidth_median'`  
All values are strings formatted in Hz (e.g. `"563.42 Hz"`).

**Example:**
```python
>>> from vocalysis import measure_formant_statistics
>>> stats = measure_formant_statistics(audio_path="path/to/speech.wav")
>>> print(stats["F2_median"])
'1654.88 Hz'
```