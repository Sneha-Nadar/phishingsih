# stego_check.py
import sys
from PIL import Image, ExifTags
import numpy as np
from math import log2
from scipy.stats import chi2

def shannon_entropy(pixels):
    vals, counts = np.unique(pixels, return_counts=True)
    probs = counts / counts.sum()
    return -np.sum(probs * np.log2(probs + 1e-12))

def lsb_uniformity(img_arr):
    # flatten LSBs of all color channels
    bits = (img_arr & 1).flatten()
    ones = bits.sum()
    zeros = bits.size - ones
    prop = abs(ones - zeros) / bits.size
    return {'ones': int(ones), 'zeros': int(zeros), 'prop_diff': prop}

def chi_square_lsb_test(img_arr):
    # For each channel compute chi-square on even/odd pairs
    stats = {}
    for ci, name in enumerate(['R','G','B'][:img_arr.shape[2]]):
        channel = img_arr[:,:,ci].flatten()
        # pair values (0,1),(2,3),... map to pair index v//2
        pair_idx = channel // 2
        evens = np.bincount(pair_idx, minlength=256//2)  # counts for pairs
        # within each pair, count even vs odd occurrences
        # reconstruct expected even/odd assuming LSB randomization: each pair splits evenly
        odds = np.bincount(pair_idx + (channel % 2==1)*0, minlength=256//2) # simpler: check bias separately
        # simpler chi2 across parity:
        even_counts = np.bincount(channel[::2] % 2, minlength=2) # fallback
        # We'll do a simple parity chi2:
        evens_total = np.sum(channel % 2 == 0)
        odds_total = np.sum(channel % 2 == 1)
        total = evens_total + odds_total
        if total == 0:
            stats[name] = {'chi2': None, 'p': None}
            continue
        # expected equal
        expected = total / 2.0
        chi2val = ((evens_total - expected)**2 + (odds_total - expected)**2) / expected
        p = 1 - chi2.cdf(chi2val, df=1)
        stats[name] = {'chi2': float(chi2val), 'p': float(p)}
    return stats

def read_metadata(img):
    meta = {}
    try:
        info = img._getexif()
        if info:
            for k,v in info.items():
                tag = ExifTags.TAGS.get(k, k)
                meta[tag] = v
    except Exception:
        pass
    return meta

def analyze(path):
    img = Image.open(path).convert('RGB')
    arr = np.array(img, dtype=np.uint8)
    height, width = arr.shape[:2]
    entropy = shannon_entropy(arr.flatten())
    lsb = lsb_uniformity(arr)
    chi = chi_square_lsb_test(arr)
    meta = read_metadata(Image.open(path))
    print(f"File: {path}")
    print(f"Size: {width}x{height}  |  Entropy: {entropy:.4f}")
    print("LSB ones vs zeros:", lsb['ones'], lsb['zeros'], f"| prop_diff = {lsb['prop_diff']:.6f}")
    print("Chi-square parity test (per channel):")
    for c,v in chi.items():
        print(" ", c, "chi2=", v['chi2'], " p=", v['p'])
    if meta:
        print("Metadata keys:", list(meta.keys())[:10])
    # Simple heuristic decision
    reasons = []
    # if LSB prop_diff small (close to 0) -> likely randomization/embedding
    if lsb['prop_diff'] < 0.03:
        reasons.append("LSB distribution near 50:50 → possible LSB embedding")
    if entropy > 7.8:
        reasons.append("High entropy → possible embedded data or heavy compression/noise")
    for c,v in chi.items():
        if v['p'] is not None and v['p'] < 0.05:
            reasons.append(f"Chi-square parity anomaly on {c} (p={v['p']:.3f})")
    if reasons:
        print("\nHEURISTIC RESULT: SUSPICIOUS")
        for r in reasons:
            print(" -", r)
    else:
        print("\nHEURISTIC RESULT: probably clean (no obvious stego)")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python stego_check.py image.png")
        sys.exit(1)
    analyze(sys.argv[1])
