# Note in the get_command() methods, i used 'command = command + [...]' and not 'command += [...]' because my static type checker doesn't work with the second way.

import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path

import vapoursynth as vs

core = vs.core
core.max_cache_size = 1024


class CommandBuilder(ABC):
    _encoder: str

    _input_path: Path
    _output_path: Path

    _bitrate: int
    _crf: float
    _tune: str
    _preset: str
    _passes: int

    def input(self, path: str) -> None:
        input_path = Path(path)

        if not input_path.exists() or not input_path.is_file():
            raise FileNotFoundError(
                "The input file does not exist."
            )  # TODO Add file path in err msg

        self.input_path = input_path

    def output(self, path: str, overwrite: bool = False) -> None:
        output_path = Path(path)

        if output_path.exists() and not overwrite:
            raise FileExistsError(
                "The output file already exists. Use the overwrite flag."
            )  # TODO Add the path in err msg

        self.output_path = output_path

    def bitrate(self, _bitrate: int) -> None:
        """Sets the bitrate in kbps"""
        if not isinstance(_bitrate, int):
            raise TypeError(f"_bitrate should be type int not {type(_bitrate)}")

        self._bitrate = _bitrate

    def crf(self, _crf: float):
        """Sets the CRF"""
        self._crf = _crf

    def tune(self, _tune: str):
        self._tune = _tune

    def passes(self, _passes: int) -> None:
        if _passes > 2:
            raise ValueError("Pass count cannot exceed 2.")
        self._passes = _passes

    def encoder(self, path: str):
        self._encoder = path

    @abstractmethod
    def run(self) -> None:
        """"""

    @abstractmethod
    def preset(self, _preset: str):
        """"""

    @abstractmethod
    def get_command(self) -> list[str]:
        """"""

    @abstractmethod
    def validate_command(self) -> bool:
        """"""


class x264CommandBuilder(CommandBuilder):
    _encoder: str = "x264"

    _stats_files: tuple[Path, Path] = (
        Path("x264_2pass.log"),
        Path("x264_2pass.log.mbtree"),
    )

    def preset(self, _preset: str):
        x264_presets = (
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
            "placebo",
        )
        if _preset not in x264_presets:
            print(
                f"Invalid preset: {_preset}\nAvailable presets are : {', '.join(x264_presets)}"
            )
            raise ValueError("Invalid preset")
        self._preset = _preset

    def crf(self, _crf: float):
        """Sets the CRF rounded to nearest int"""
        super().crf(_crf)
        self._crf = round(self._crf)

    def get_command(self) -> list[str]:
        command: list[str] = [self._encoder]

        # Options
        if hasattr(self, "_bitrate"):
            command = command + ["--bitrate", str(self._bitrate)]

        if hasattr(self, "_crf"):
            command = command + ["--crf", str(self._crf)]

        if hasattr(self, "_tune"):
            command = command + ["--tune", self._tune]

        if hasattr(self, "_preset"):
            command = command + ["--preset", self._preset]

        # Output file
        if not self.output_path:
            raise Exception()  # TODO Add the correct err
        command = command + ["-o", str(self.output_path)]

        # Input file
        if not self.input_path:
            raise Exception()  # TODO Add the correct err
        command = command + [str(self.input_path)]

        return command

    def get_2pass_commands(self) -> list[list[str]]:
        command = self.get_command()
        command.insert(1, "--pass")

        pass1 = command.copy()
        pass1.insert(2, "1")

        pass2 = command.copy()
        pass2.insert(2, "2")

        return [pass1, pass2]

    def validate_command(self) -> bool:
        raise NotImplementedError()  # TODO Implement

    def run(self) -> None:
        if hasattr(self, "_passes"):
            commands: list[list[str]] = self.get_2pass_commands()
        else:
            commands: list[list[str]] = [self.get_command()]

        for command in commands:
            try:
                subprocess.run(command, text=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Encoder encountered an error:\n{e}")
                sys.exit(1)

        for file in self._stats_files:
            file.unlink()


class SVTAV1CommandBuilder(CommandBuilder):
    _vs_input: vs.VideoNode

    def __init__(self) -> None:
        super().__init__()

        self._encoder = "SvtAv1EncApp"

    def preset(self, _preset: str):
        if _preset not in (
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
        ):  # TODO Put true presets
            raise ValueError()  # TODO Error message
        self._preset = _preset

    def crf(self, _crf: float):
        """Sets the CRF rounded to nearest int"""
        super().crf(_crf)
        self._crf = round(self._crf)

    def get_command(self) -> list[str]:
        command: list[str] = [self._encoder]

        # Options
        if hasattr(self, "_bitrate"):
            command = command + ["--tbr", str(self._bitrate), "--rc", "1"]

        if hasattr(self, "_crf"):
            command = command + ["--crf", str(self._crf)]

        if hasattr(self, "_tune"):
            command = command + ["--tune", self._tune]

        if hasattr(self, "_preset"):
            command = command + ["--preset", self._preset]

        # Output
        if not self.output_path:
            raise Exception()  # TODO correct err
        command = command + ["-b", str(self.output_path)]

        # Input
        if not self.input_path:
            raise Exception()  # TODO correct err
        command = command + ["-i", "-"]

        return command

    def _load_vs_source(self):
        self._vs_input: vs.VideoNode = core.lsmas.LWLibavSource(  # type: ignore
            source=self.input_path, cache=0
        )

    def validate_command(self) -> bool:
        raise NotImplementedError  # TODO Implement

    def get_2pass_commands(self) -> list[list[str]]:
        command = self.get_command()
        command.insert(1, "--pass")

        pass1 = command.copy()
        pass1.insert(2, "1")

        pass2 = command.copy()
        pass2.insert(2, "2")

        return [pass1, pass2]

    def run(self):
        # if not self.validate_command():
        #     raise Exception  # TODO Add correct err

        self._load_vs_source()

        # TODO make sure the source was loaded correctly

        if hasattr(self, "_passes"):
            commands: list[list[str]] = self.get_2pass_commands()
        else:
            commands: list[list[str]] = [self.get_command()]

        for command in commands:
            try:
                process = subprocess.Popen(command, stdin=subprocess.PIPE)

                self._vs_input.output(process.stdin, y4m=True)  # pyright: ignore[reportArgumentType]
                process.wait()

            except subprocess.CalledProcessError as e:
                print(f"Encoder encountered an error:\n{e}")
                sys.exit(1)
