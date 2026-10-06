# Note in the get_command() methods, i used 'command = command + [...]' and not 'command += [...]' because my static type checker doesn't work with the second way.

import subprocess
import sys

import vapoursynth as vs  # pyright: ignore[reportMissingTypeStubs]

from ..encoders import VideoEncoder

core = vs.core
core.max_cache_size = 1024

DEFAULT_VPY = """from vstools import vs, core, depth, DitherType
core.max_cache_size = 1024
src = core.ffms2.Source(source=r"<input>", cachefile=r"cache.ffindex")
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
src.set_output()"""


class SVTAV1(VideoEncoder):
    _vs_input: vs.VideoNode

    def __init__(self) -> None:
        super().__init__()

        self._encoder = "SvtAv1EncApp"

    def preset(self, _preset: str):
        """Validates and sets the preset"""
        svtav1_presets = (
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
        )
        if _preset not in svtav1_presets:
            raise ValueError(f"'{_preset}' not in {', '.join(svtav1_presets)}")
        self._preset = _preset

    def crf(self, _crf: float):
        """Sets the CRF rounded to nearest int"""
        super().crf(_crf)
        self._crf = round(self._crf)

    def _cmd_add_generic_parameters(self, command):
        # Options
        if hasattr(self, "_bitrate"):
            command = command + ["--tbr", str(self._bitrate), "--rc", "1"]

        if hasattr(self, "_crf"):
            command = command + ["--crf", str(self._crf)]

        if hasattr(self, "_tune"):
            command = command + ["--tune", self._tune]

        if hasattr(self, "_preset"):
            command = command + ["--preset", self._preset]

        if len(self._additional_parameters) > 0:
            command = command + self._additional_parameters

        return command

    def get_command(self) -> list[str]:
        """Returns a valid command"""
        command: list[str] = [self._encoder]

        command = self._cmd_add_generic_parameters(command)

        # Output
        if not self.output_path:
            raise ValueError("Output path was not set.")
        command += ["-b", str(self.output_path)]

        # Input
        if not self.input_path:
            raise ValueError("Input path was not set.")
        command += ["-i", "-"]

        return command

    def _write_default_vpy(self):
        with open("script.vpy", "w") as f:
            f.write(DEFAULT_VPY.replace("<input>", str(self.input_path)))

    def _load_vs_source(self):
        """Loads the source file in a VS object"""
        if self._is_input_vpy:
            if self._use_default_vpy:
                self._write_default_vpy()
                vpy_file = "script.vpy"
            else:
                vpy_file = self.input_path

            vpy_vars = {}
            exec(open(vpy_file).read(), globals(), vpy_vars)
            self._vs_input = vpy_vars["src"]
        else:
            self._vs_input: vs.VideoNode = core.lsmas.LWLibavSource(  # type: ignore
                source=self.input_path, cache=0
            )

    def validate_command(self) -> bool:
        """Validates the command"""
        raise NotImplementedError  # TODO Implement

    def get_2pass_commands(self) -> list[list[str]]:
        """Returns 2 valid commands : first pass, second pass"""
        command = self.get_command()
        command.insert(1, "--pass")

        pass1 = command.copy()
        pass1.insert(2, "1")

        pass2 = command.copy()
        pass2.insert(2, "2")

        return [pass1, pass2]

    def run(self):
        """Runs the command"""
        # if not self.validate_command():
        #     raise Exception  # TODO Add correct err

        self._load_vs_source()

        # TODO make sure the source was loaded correctly ?

        if hasattr(self, "_passes"):
            commands: list[list[str]] = self.get_2pass_commands()
        else:
            commands: list[list[str]] = [self.get_command()]

        for command in commands:
            try:
                process = subprocess.Popen(command, stdin=subprocess.PIPE)
                self._vs_input.output(process.stdin, y4m=True)  # pyright: ignore[reportArgumentType]
                # process.wait()

            except subprocess.CalledProcessError as e:
                print(f"Encoder encountered an error:\n{e}")
                sys.exit(1)


class SVTAV1Essential(SVTAV1):
    _speed: str
    _quality: str

    def speed(self, _speed: str):
        """Validates and sets the speed"""
        speeds = ("slower", "slow", "medium", "fast", "faster")
        if _speed not in speeds:
            f"'{_speed}' not in {', '.join(speeds)}"
        self._speed = _speed

    def quality(self, _quality: str):
        """Validates and sets the quality"""
        qualities = ("higher", "high", "medium", "low", "lower")
        if _quality not in qualities:
            raise ValueError(f"'{_quality}' not in {', '.join(qualities)}")
        self._quality = _quality

    def _cmd_add_generic_parameters(self, command):
        command = super()._cmd_add_generic_parameters(command)

        if hasattr(self, "_speed"):
            command = command + ["--speed", self._speed]

        if hasattr(self, "_quality"):
            command = command + ["--quality", self._quality]

        return command
