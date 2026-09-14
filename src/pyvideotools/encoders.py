import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path


class CommandBuilder(ABC):
    _input_path: Path
    _output_path: Path

    _bitrate: str

    @abstractmethod
    def bitrate(self, _bitrate: str) -> None:
        """"""

    @abstractmethod
    def input(self, path: str) -> None:
        """"""

    @abstractmethod
    def output(self, path: str, overwrite: bool = False) -> None:
        """"""

    @abstractmethod
    def get_command(self) -> list[str]:
        """"""

    @abstractmethod
    def get_2pass_commands(self) -> list[list[str]]:
        """"""

    @abstractmethod
    def passes(self, _passes: int) -> None:
        """"""

    @abstractmethod
    def run(self) -> None:
        """"""


class x264CommandBuilder(CommandBuilder):
    _input_path: Path
    _output_path: Path

    _bitrate: str
    _preset: str

    def input(self, path: str):
        input_path = Path(path)

        if not input_path.exists() or not input_path.is_file():
            raise Exception()

        self.input_path = input_path

    def output(self, path: str, overwrite: bool = False):
        output_path = Path(path)

        if output_path.exists() and not overwrite:
            raise Exception()

        self.output_path = output_path

    def bitrate(self, _bitrate: str):
        self._bitrate = _bitrate

    def preset(self, _preset: str):
        if _preset not in (
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
        ):
            raise SyntaxError(_preset + " preset not available")
        self._preset = _preset

    def passes(self, _passes: int) -> None:
        self._passes = _passes

    def get_command(self) -> list[str]:
        command: list[str] = ["x264"]

        # Options
        if hasattr(self, "_bitrate"):
            command += ["--bitrate", self._bitrate]

        if hasattr(self, "_preset"):
            command += ["--preset", self._preset]

        # Output file
        if not self.output_path:
            raise Exception()
        command += ["-o", str(self.output_path)]

        # Input file
        if not self.input_path:
            raise Exception()
        command += [str(self.input_path)]

        return command

    def get_2pass_commands(self) -> list[list[str]]:
        command = self.get_command()
        command.insert(1, "--pass")

        pass1 = command.copy()
        pass1.insert(2, "1")

        pass2 = command.copy()
        pass2.insert(2, "2")

        return [pass1, pass2]

    def run(self) -> None:
        if hasattr(self, "_passes"):
            commands: list[list[str]] = self.get_2pass_commands()
        else:
            commands: list[list[str]] = [self.get_command()]

        for command in commands:
            try:
                subprocess.run(command, text=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"x264 encountered an error:\n{e}")
                sys.exit(1)


class SVTAV1CommandBuilder: ...

