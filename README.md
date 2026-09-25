# pyvideotools : Quality Metrics & Video Encoding

WIP

Python utilities for video quality measurement and video encoding using VapourSynth.

Simple metric usage with statistics.
x264 and SVT-AV1 bindings.

## Features
- Quality metrics
    - SSIMULACRA2
    - XPSNR
    - Butteraugli
    - CVVDP
- CPU and GPU implementations
- x264 and SVT-AV1 encoding (WIP)

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