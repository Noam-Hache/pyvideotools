# Note in the get_command() methods, i used 'command = command + [...]' and not 'command += [...]' because my static type checker doesn't work with the second way.

import subprocess
import sys
from pathlib import Path

from command_builder import CommandBuilder


class x264CommandBuilder(CommandBuilder):
    _encoder: str = "x264"

    _stats_files: tuple[Path, Path] = (
        Path("x264_2pass.log"),
        Path("x264_2pass.log.mbtree"),
    )

    def preset(self, _preset: str):
        """Validates and sets the preset"""
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
        """Returns a valid command"""
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
            raise ValueError("Output path was not set.")
        command += ["-o", str(self.output_path)]

        # Input file
        if not self.input_path:
            raise ValueError("Input path was not set")
        command += [str(self.input_path)]

        return command

    def get_2pass_commands(self) -> list[list[str]]:
        """Returns 2 valid commands : first pass, second pass"""
        command = self.get_command()
        command.insert(1, "--pass")

        pass1 = command.copy()
        pass1.insert(2, "1")

        pass2 = command.copy()
        pass2.insert(2, "2")

        return [pass1, pass2]

    def validate_command(self) -> bool:
        """Validates the command"""
        raise NotImplementedError()  # TODO Implement

    def run(self) -> None:
        """Runs the command and deletes stats file"""
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
