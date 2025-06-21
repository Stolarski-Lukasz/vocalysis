def measure_centroid(audio_path: str) -> dict:
    """
    Measure the spectral centroid of an audio file.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        dict: A dictionary containing the spectral centroid statistics.
    """
    import librosa
    import numpy as np

    # Load the audio file
    y, sr = librosa.load(audio_path, sr=None)

    # Calculate the spectral centroid
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)

    # Calculate statistics
    mean_centroid = np.mean(spectral_centroid)
    median_centroid = np.median(spectral_centroid)
    std_centroid = np.std(spectral_centroid)

    return {
        'mean': mean_centroid,
        'median': median_centroid,
        'std': std_centroid
    }