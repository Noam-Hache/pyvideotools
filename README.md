# pyvideotools : Quality Metrics & Video Encoding

WIP

Python utilities for video quality measurement and video encoding using VapourSynth.

Simple metric usage with statistics.
x264 and SVT-AV1 bindings.

## Features
### Quality metrics
- CPU and/or GPU implementations depending on metric
    - SSIMULACRA2 (CPU, GPU)
    - XPSNR (CPU)
    - Butteraugli (GPU)
    - CVVDP (GPU)

### Encoding
- x264 and SVT-AV1 bindings
- Common bindings for :
    - input/output
    - bitrate
    - crf
    - preset
    - tune
    - passes
    - encoder path
    - other (for parameters not implemented)
- SVT-AV1 supports .vpy input script


## Requirements

- Python
- [VapourSynth](https://www.vapoursynth.com/)
- [L-SMASH Works](https://github.com/HomeOfAviSynthPlusEvolution/L-SMASH-Works)
- [VS-ZIP](https://github.com/dnjulek/vapoursynth-zip) and/or [VSHIP](https://codeberg.org/Line-fr/Vship)
- [FFmpeg](https://ffmpeg.org/), [x264](https://www.videolan.org/developers/x264.html), [SVT-AV1](https://gitlab.com/AOMediaCodec/SVT-AV1), or [Turbo-Metrics](https://github.com/Gui-Yom/turbo-metrics) depending on the features used

## Examples
### Quality metrics examples

```python
from pathlib import Path

from pyvideotools import metrics

metric = metrics.VSzipSSIMULACRA2(
    source=Path("source.mkv"),
    distorted=Path("encoded.mkv"),
    skip=3,
)

metric.run()

print(metric.scores_standard_deviation)
print(metric.scores_median)
```

### Encoding examples

SVT-AV1 CRF Encoding
```python
from pyvideotools.encoders import AV1

cmd = AV1.SVTAV1CommandBuilder()
cmd.input("input.mkv")
cmd.preset("4")
cmd.crf(30)
cmd.output("output.mkv")
cmd.run()
```

SVT-AV1 VPY input with CRF encoding\
VPY script taken from [Auto-Boost-Essential](https://github.com/nekotrix/auto-boost-algorithm/blob/main/Auto-Boost-Essential/Auto-Boost-Essential.py) by [nekotrix](https://github.com/nekotrix)
```python
"""script.vpy"""
from vstools import vs, core, depth, DitherType
core.max_cache_size = 1024
src = core.ffms2.Source(source=r"input.mkv", cachefile=r"cache.ffindex")
bit_to_format = {
    8: vs.YUV420P8,
    10: vs.YUV420P10,
    12: vs.YUV420P12
}
bit_to_dither = {
    8: DitherType.NONE,
    10: DitherType.NONE,
    12: DitherType.RANDOM
}
fmt = bit_to_format.get(src.format.bits_per_sample, vs.YUV420P16)
dt = bit_to_dither.get(src.format.bits_per_sample, DitherType.RANDOM)
src = depth(src.resize.Bilinear(format=fmt), 10, dither_type=dt)
src.set_output()
```
```python
"""main.py"""
from pyvideotools.encoders import AV1

cmd = AV1.SVTAV1CommandBuilder()
cmd.input("script.vpy", is_input_vpy=True)
cmd.preset("4")
cmd.crf(30)
cmd.output("output.mkv", overwrite=True)
cmd.run()
```

x264 2-pass target bitrate
```python
from pyvideotools.encoders import H264

cmd = H264.x264CommandBuilder()
cmd.input("input.mp4")
cmd.preset("faster")
cmd.bitrate(682)
cmd.passes(2)
cmd.output("target.mkv", overwrite=True)
cmd.run()
```


## Supported Implementations

| Metric      | CPU                    | GPU   |
| ----------- | ---------------------- | ----- |
| SSIMULACRA2 | VS-ZIP / Turbo-Metrics | VSHIP |
| XPSNR       | VS-ZIP / FFmpeg        | -     |
| Butteraugli | -                      | VSHIP |
| CVVDP       | -                      | VSHIP |