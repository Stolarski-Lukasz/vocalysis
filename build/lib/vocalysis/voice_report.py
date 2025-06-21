import parselmouth
import numpy as np


def measure_pitch(audio_path=None, sound_object=None, pitch_object=None, min_pitch=75, max_pitch=500):
    """
    Compute pitch statistics (in Hz) from a WAV file or Parselmouth objects.

    One of `audio_path`, `sound_object`, or `pitch_object` must be provided.
    If multiple are given, the function uses the first available in this order:
    `pitch_object` > `sound_object` > `audio_path`.

    Args:
        audio_path (str, optional): Path to an audio file. It could be a WAV file or any format supported by Parselmouth.
        sound_object (parselmouth.Sound, optional): A precomputed sound object.
        pitch_object (parselmouth.Pitch, optional): A precomputed pitch object.
        min_pitch (float, optional): Minimum pitch in Hz. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz. Defaults to 500.

    Returns:
        dict: A dictionary of pitch statistics based on voiced frames, containing:
            - 'median': Median pitch.
            - 'mean': Mean pitch.
            - 'std': Standard deviation of pitch.
            - 'min': Minimum pitch.
            - 'max': Maximum pitch.

        If no voiced frames are found, all values are `None`.

    Raises:
        ValueError: If none of the input sources (`audio_path`, `sound_object`, or `pitch_object`) is provided.

    Examples:
        Basic usage with a WAV file:

        from vocalysis import measure_pitch

        stats = measure_pitch(audio_path="example.wav")
        print(stats["mean"])  # e.g. '142.537 Hz'
    """

    if pitch_object is not None:
        pitch = pitch_object
    elif sound_object is not None:
        sound = sound_object
        pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
    elif audio_path is not None:
        sound = parselmouth.Sound(audio_path)
        pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
    else:
        raise ValueError("Either 'audio_path', 'sound_object', or 'pitch_object' must be provided.")


    pitch_values = pitch.selected_array['frequency']

    # Remove unvoiced values (0 Hz)
    voiced = pitch_values[pitch_values > 0]

    if len(voiced) == 0:
        return {
            'median': None,
            'mean': None,
            'std': None,
            'min': None,
            'max': None
        }

    stats = {
        'median': f"{np.median(voiced):.3f} Hz",
        'mean': f"{np.mean(voiced):.3f} Hz",
        'std': f"{np.std(voiced):.3f} Hz",
        'min': f"{np.min(voiced):.3f} Hz",
        'max': f"{np.max(voiced):.3f} Hz"
    }

    return stats


def measure_pulses(audio_path=None, sound_object=None, pitch_object=None, point_process=None, min_pitch=75, max_pitch=500):
    """
    Measure pulse-related statistics from a WAV file using Parselmouth.

    Args:
        audio_path (str, optional): Path to an audio file. It could be a WAV file or any format supported by Parselmouth. Used if `sound_object` and `pitch_object` are not provided.
        sound_object (parselmouth.Sound, optional): Precomputed sound object.
        pitch_object (parselmouth.Pitch, optional): Precomputed pitch object.
        point_process (parselmouth.PointProcess, optional): Precomputed point process object.
        min_pitch (float, optional): Minimum pitch in Hz. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz. Defaults to 500.

    Returns:
        dict: A dictionary containing the following keys:
            - 'num_pulses': Number of detected pulses.
            - 'num_periods': Number of periods between pulses.
            - 'mean_period': Mean period (in seconds), or None if not computable.
            - 'std_period': Standard deviation of period (in seconds), or None if not computable.

    Raises:
        ValueError: If neither `point_process` nor a way to compute it (`sound_object` or `audio_path`) is provided.

    Examples:
        Basic usage with a WAV file:

        from vocalysis import measure_pulses

        stats = measure_pulses(audio_path="example.wav")
        print(stats["mean_period"])  # e.g. '0.0050364095 seconds'
    """

    # Step 1: Use the given PointProcess if available
    if point_process is not None:
        pass  # Use it directly
    else:
        # Step 2: Ensure we have a sound object
        if sound_object is not None:
            sound = sound_object
        elif audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        else:
            raise ValueError("To compute point_process, either 'sound_object' or 'audio_path' must be provided.")

        # Step 3: Ensure we have a pitch object
        if pitch_object is None:
            pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
        else:
            pitch = pitch_object

        # Step 4: Compute PointProcess from sound and pitch
        point_process = parselmouth.praat.call([sound, pitch], "To PointProcess (cc)")

    # Step 5: Pulse statistics
    num_pulses = parselmouth.praat.call(point_process, "Get number of points")
    pulse_times = [parselmouth.praat.call(point_process, "Get time from index", i + 1) for i in range(num_pulses)]
    periods = np.diff(pulse_times)
    num_periods = len(periods)

    if num_periods > 0:
        mean_period = parselmouth.praat.call(point_process, "Get mean period", 0, 0, 0.0001, 0.02, 1.3)
        std_period = parselmouth.praat.call(point_process, "Get stdev period", 0, 0, 0.0001, 0.02, 1.3)
    else:
        mean_period = None
        std_period = None

    return {
        'num_pulses': num_pulses,
        'num_periods': num_periods,
        'mean_period': f"{mean_period:.10f} seconds" if mean_period is not None else None,
        'std_period': f"{std_period:.10f} seconds" if std_period is not None else None
    }


def measure_voicing(audio_path=None, sound_object=None, pitch_object=None, point_process=None, min_pitch=75, max_pitch=500):
    """
    Analyze voicing characteristics in a WAV file using Parselmouth.

    This function measures the proportion of unvoiced frames, detects voice breaks,
    and calculates the degree of voice breaks based on inter-pulse intervals derived 
    from a PointProcess representation of the signal.
    
    You must either:
    - Provide only `audio_path` (recommended for typical usage), in which case all necessary objects will be computed internally, OR
    - Provide all of the following: `sound_object`, `pitch_object`, and `point_process`.

    Args:
        audio_path (str, optional): Path to an audio file (WAV or other formats supported by Parselmouth).
        sound_object (parselmouth.Sound, optional): Pre-loaded Parselmouth Sound object.
        pitch_object (parselmouth.Pitch, optional): Pitch object corresponding to the sound.
        point_process (parselmouth.PointProcess, optional): PointProcess object for glottal pulses.
        min_pitch (float, optional): Minimum pitch in Hz used for pitch tracking and determining the threshold 
            for voice breaks. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz for pitch tracking. Defaults to 500.

    Returns:
        dict: A dictionary with the following voicing statistics:
            - 'unvoiced_fraction' (str): Percentage of frames that are unvoiced, formatted to three decimal places (e.g., '12.345%').
            - 'num_voice_breaks' (int): Number of detected voice breaks (i.e., silent intervals between consecutive pulses
            longer than 1.25 divided by `min_pitch`).
            - 'degree_voice_breaks' (str): Total duration of voice breaks divided by total duration of the signal,
            formatted as a percentage to three decimal places (e.g., '4.789%').

    Notes:
        - Voice breaks are detected based on the threshold `1.25 / min_pitch`, following standard practice in voice quality analysis.
        - If the audio file is empty or contains no frames, voicing measures will be returned as `None` or `0`.

    Examples:
        Basic usage with a WAV file:

        from vocalysis import measure_voicing

        stats = measure_voicing(audio_path="example.wav")
        print(stats["num_voice_breaks"])  # e.g. '15'
    """
    if point_process is not None:
        if pitch_object is None:
            raise ValueError("If 'point_process' is provided, 'pitch_object' must also be provided.")
        # Assume sound is needed for total duration
        if sound_object is None:
            if audio_path is None:
                raise ValueError("If 'point_process' is provided, either 'sound_object' or 'audio_path' must also be provided.")
            sound = parselmouth.Sound(audio_path)
        else:
            sound = sound_object
        pitch = pitch_object
    else:
        if sound_object is not None:
            sound = sound_object
        elif audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        else:
            raise ValueError("To compute 'point_process', either 'sound_object' or 'audio_path' must be provided.")

        pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
        point_process = parselmouth.praat.call([sound, pitch], "To PointProcess (cc)")

    # Fraction of unvoiced frames
    total_frames = pitch.get_number_of_frames()
    voiced_frames = pitch.count_voiced_frames()
    unvoiced_fraction = (1 - (voiced_frames / total_frames)) * 100 if total_frames > 0 else None

    # Pulse times
    num_pulses = parselmouth.praat.call(point_process, "Get number of points")
    pulse_times = [parselmouth.praat.call(point_process, "Get time from index", i + 1) for i in range(num_pulses)]

    # Intervals
    inter_pulse_intervals = [
        pulse_times[i+1] - pulse_times[i] for i in range(len(pulse_times) - 1)
    ]

    voice_break_threshold = 1.25 / min_pitch
    num_voice_breaks = sum(interval > voice_break_threshold for interval in inter_pulse_intervals)
    total_break_duration = sum(interval for interval in inter_pulse_intervals if interval > voice_break_threshold)

    analysis_duration = sound.get_total_duration()
    degree_voice_breaks = (total_break_duration / analysis_duration) * 100 if analysis_duration > 0 else None

    return {
        'unvoiced_fraction': f"{unvoiced_fraction:.3f}%" if unvoiced_fraction is not None else None,
        'num_voice_breaks': num_voice_breaks,
        'degree_voice_breaks': f"{degree_voice_breaks:.3f}%" if degree_voice_breaks is not None else None,
    }


def measure_jitter(audio_path=None, sound_object=None, pitch_object=None, point_process=None, min_pitch=75, max_pitch=600):
    """
    Measure jitter statistics from a sound or PointProcess using Parselmouth.

    One of `audio_path`, `sound_object`, or `point_process` must be provided.
    If multiple are given, the function uses the first available in this order:
    `point_process` > `sound_object` > `audio_path`.

    Args:
        audio_path (str, optional): Path to an audio file. It could be a WAV file or any format supported by Parselmouth. Used if `sound_object` is not provided.
        sound_object (parselmouth.Sound, optional): A precomputed sound object.
        pitch_object (parselmouth.Pitch, optional): A precomputed pitch object.
        point_process (parselmouth.PointProcess, optional): A precomputed point process object.
        min_pitch (float, optional): Minimum pitch in Hz for pitch analysis. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz for pitch analysis. Defaults to 600.

    Returns:
        dict: A dictionary containing the following jitter measures:
            - 'jitter_local' (str): Local jitter as a percentage string.
            - 'jitter_local_absolute' (str): Absolute local jitter (in seconds).
            - 'jitter_rap' (str): Relative average perturbation (as percentage string).
            - 'jitter_ppq5' (str): Five-point period perturbation quotient (as percentage string).
            - 'jitter_ddp' (str): Difference of differences of periods (as percentage string).

    Raises:
        ValueError: If neither `point_process` nor any combination of `sound_object` or `audio_path` is provided.

    Examples:
        Basic usage with a WAV file:

        from vocalysis import measure_jitter

        stats = measure_jitter(audio_path="example.wav")
        print(stats["jitter_local"])  # e.g. '4.123%'
    """

    # Step 1: Use provided PointProcess if available
    if point_process is not None:
        pass  # Use directly
    else:
        # Step 2: Ensure we have a sound object
        if sound_object is not None:
            sound = sound_object
        elif audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        else:
            raise ValueError("To compute point_process, either 'sound_object' or 'audio_path' must be provided.")

        # Step 3: Ensure we have a pitch object
        if pitch_object is None:
            pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
        else:
            pitch = pitch_object

        # Step 4: Compute PointProcess
        point_process = parselmouth.praat.call([sound, pitch], "To PointProcess (cc)")

    # Step 5: Extract jitter measures
    return {
        'jitter_local': f"{parselmouth.praat.call(point_process, 'Get jitter (local)', 0, 0, 0.0001, 0.02, 1.3) * 100:.3f}%",
        'jitter_local_absolute': f"{parselmouth.praat.call(point_process, 'Get jitter (local, absolute)', 0, 0, 0.0001, 0.02, 1.3):.6f}",
        'jitter_rap': f"{parselmouth.praat.call(point_process, 'Get jitter (rap)', 0, 0, 0.0001, 0.02, 1.3) * 100:.3f}%",
        'jitter_ppq5': f"{parselmouth.praat.call(point_process, 'Get jitter (ppq5)', 0, 0, 0.0001, 0.02, 1.3) * 100:.3f}%",
        'jitter_ddp': f"{parselmouth.praat.call(point_process, 'Get jitter (ddp)', 0, 0, 0.0001, 0.02, 1.3) * 100:.3f}%"
    }


def measure_shimmer(audio_path=None, sound_object=None, pitch_object=None, point_process=None, min_pitch=75, max_pitch=500):
    """
    Measure shimmer statistics from a sound and PointProcess using Parselmouth.

    One of `audio_path`, `sound_object`, or `point_process` must be provided.
    If multiple are given, the function uses the first available in this order:
    `point_process` > `sound_object` > `audio_path`.

    Args:
        audio_path (str, optional): Path to an audio file. It could be a WAV file or any format supported by Parselmouth. Used if `sound_object` is not provided.
        sound_object (parselmouth.Sound, optional): A precomputed sound object.
        pitch_object (parselmouth.Pitch, optional): A precomputed pitch object.
        point_process (parselmouth.PointProcess, optional): A precomputed point process object.
        min_pitch (float, optional): Minimum pitch in Hz for pitch analysis. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz for pitch analysis. Defaults to 500.

    Returns:
        dict: A dictionary containing the following shimmer measures:
            - 'shimmer_local' (str): Local shimmer as a percentage string.
            - 'shimmer_local_dB' (str): Local shimmer in decibels.
            - 'shimmer_apq3' (str): Amplitude perturbation quotient (3-point, as percentage string).
            - 'shimmer_apq5' (str): Amplitude perturbation quotient (5-point, as percentage string).
            - 'shimmer_apq11' (str): Amplitude perturbation quotient (11-point, as percentage string).
            - 'shimmer_dda' (str): Difference of differences of amplitudes (as percentage string).

    Raises:
        ValueError: If necessary input is missing:
            - When computing `point_process` but neither `sound_object` nor `audio_path` is provided.
            - When using a provided `point_process` but neither `sound_object` nor `audio_path` is provided to supply a sound.

    Examples:
        Basic usage with a WAV file:

        from vocalysis import measure_shimmer

        stats = measure_shimmer(audio_path="example.wav")
        print(stats["shimmer_local"])  # e.g. '8.340%'
    """
    # Step 1: Use provided PointProcess if available
    if point_process is not None:
        if sound_object is None and audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        elif sound_object is not None:
            sound = sound_object
        else:
            raise ValueError("When providing a point_process, either 'sound_object' or 'audio_path' must also be provided.")
    else:
        # Step 2: Ensure we have a sound object
        if sound_object is not None:
            sound = sound_object
        elif audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        else:
            raise ValueError("To compute point_process, either 'sound_object' or 'audio_path' must be provided.")

        # Step 3: Ensure we have a pitch object
        if pitch_object is None:
            pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
        else:
            pitch = pitch_object

        # Step 4: Compute PointProcess
        point_process = parselmouth.praat.call([sound, pitch], "To PointProcess (cc)")

    # Step 5: Extract shimmer measures
    shimmer_measures = {
        'shimmer_local': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (local)', 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100:.3f}%",
        'shimmer_local_dB': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (local_dB)', 0, 0, 0.0001, 0.02, 1.3, 1.6):.3f} dB",
        'shimmer_apq3': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (apq3)', 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100:.3f}%",
        'shimmer_apq5': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (apq5)', 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100:.3f}%",
        'shimmer_apq11': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (apq11)', 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100:.3f}%",
        'shimmer_dda': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (dda)', 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100:.3f}%"
    }

    return shimmer_measures


def measure_intensity(audio_path=None, sound_object=None, intensity_object=None, time_step=0.01, min_pitch=75.0):
    """
    Measure intensity statistics (in dB) using Parselmouth.

    Accepts either an audio file path, a precomputed `Sound` object, or a precomputed
    `Intensity` object. If multiple inputs are provided, priority is given in the
    following order:
    `intensity_object` > `sound_object` > `audio_path`.

    Args:
        audio_path (str, optional): Path to an audio file. It could be a WAV file or any format supported by Parselmouth. Used if `sound_object` is not provided.
        sound_object (parselmouth.Sound, optional): Precomputed sound object.
        intensity_object (parselmouth.Intensity, optional): Precomputed intensity object.
        time_step (float, optional): Time step in seconds for intensity analysis. Defaults to 0.01.
        min_pitch (float, optional): Minimum pitch in Hz for intensity computation. Defaults to 75.0.

    Returns:
        dict: A dictionary of intensity statistics (in decibels), formatted as strings:
            - 'intensity_median': Median intensity.
            - 'intensity_mean': Mean intensity.
            - 'intensity_std': Standard deviation of intensity.
            - 'intensity_min': Minimum intensity.
            - 'intensity_max': Maximum intensity.

            If no valid intensity values are found, all values will be `None`.

    Raises:
        ValueError: If neither `sound_object` nor `audio_path` is provided and no `intensity_object` is available.

    Examples:
        Basic usage with a WAV file:

        from vocalysis import measure_intensity

        stats = measure_intensity(audio_path="example.wav")
        print(stats["intensity_mean"])  # e.g. '81.833 dB'
    """

    # Step 1: Use provided Intensity object if available
    if intensity_object is not None:
        intensity = intensity_object
        if sound_object is None and audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        elif sound_object is not None:
            sound = sound_object
        elif audio_path is None:
            sound = None  # sound is unused if intensity is provided
    else:
        # Step 2: Ensure we have a sound object
        if sound_object is not None:
            sound = sound_object
        elif audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        else:
            raise ValueError("To compute intensity, either 'sound_object' or 'audio_path' must be provided.")

        # Step 3: Compute intensity
        intensity = sound.to_intensity(time_step=time_step, minimum_pitch=min_pitch)

    # Step 4: Extract intensity values and remove NaNs
    values = intensity.values[0]
    values = values[~np.isnan(values)]

    if len(values) == 0:
        return {
            'intensity_median': None,
            'intensity_mean': None,
            'intensity_std': None,
            'intensity_min': None,
            'intensity_max': None
        }

    return {
        'intensity_median': f"{np.median(values):.3f} dB",
        'intensity_mean': f"{np.mean(values):.3f} dB",
        'intensity_std': f"{np.std(values):.3f} dB",
        'intensity_min': f"{np.min(values):.3f} dB",
        'intensity_max': f"{np.max(values):.3f} dB"
    }



def get_voice_report(audio_path, min_pitch=75, max_pitch=500, time_step=0.01):
    """
    Generate a comprehensive voice report from an audio file using Parselmouth.

    This function extracts and summarizes multiple acoustic measures from a speech signal,
    including pitch, jitter, shimmer, harmonicity, intensity, and pulse-based statistics.

    Args:
        audio_path (str, optional): Path to an audio file. It could be a WAV file or any format supported by Parselmouth.
        min_pitch (float, optional): Minimum pitch in Hz used for pitch, jitter, shimmer, and harmonicity analysis.
            Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz used for pitch analysis. Defaults to 500.
        time_step (float, optional): Time step in seconds used for harmonicity and intensity analysis.
            Defaults to 0.01.

    Returns:
        dict: A dictionary containing acoustic measurements with the following keys:
            - 'pitch': Output from `measure_pitch()` (e.g., mean, std, min/max pitch in Hz).
            - 'pulses': Output from `measure_pulses()` (e.g., number of pulses, periods).
            - 'jitter': Output from `measure_jitter()` (e.g., local jitter, RAP, PPQ5, etc.).
            - 'shimmer': Output from `measure_shimmer()` (e.g., shimmer_local, shimmer_apq3, shimmer_apq5, etc.).
            - 'harmonicity': Output from `measure_harmonicity()` (e.g., mean HNR, NHR, autocorrelation).
            - 'intensity': Output from `measure_intensity()` (e.g., mean, median, min/max intensity in dB).

    Notes:
        Internally, this function constructs intermediate Parselmouth objects (Pitch, PointProcess,
        Harmonicity, Intensity) and passes them to respective helper functions to avoid redundant computation.
    """

    sound = parselmouth.Sound(audio_path)
    pitch_object = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
    point_process_object = parselmouth.praat.call([sound, pitch_object], "To PointProcess (cc)")
    harmonicity = sound.to_harmonicity_ac(
            time_step=time_step,
            minimum_pitch=min_pitch,
            silence_threshold=0.1
        )
    intensity = sound.to_intensity(time_step=time_step, minimum_pitch=min_pitch)

    return {
        'Pitch': measure_pitch(pitch_object=pitch_object),
        'Pulses': measure_pulses(point_process=point_process_object),
        'Voicing': measure_voicing(point_process=point_process_object, pitch_object=pitch_object, sound_object=sound),
        'Jitter': measure_jitter(point_process=point_process_object),
        'Shimmer': measure_shimmer(point_process=point_process_object, sound_object=sound),
        'Intensity': measure_intensity(intensity_object=intensity)
    }
