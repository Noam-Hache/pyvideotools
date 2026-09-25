# Note in the get_command() methods, i used 'command = command + [...]' and not 'command += [...]' because my static type checker doesn't work with the second way.

import subprocess
import sys

import vapoursynth as vs  # pyright: ignore[reportMissingTypeStubs]

from ..command_builder import CommandBuilder

core = vs.core
core.max_cache_size = 1024


class SVTAV1CommandBuilder(CommandBuilder):
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

    def get_command(self) -> list[str]:
        """Returns a valid command"""
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

        if len(self.additional_parameters) > 0:
            command = command + self.additional_parameters

        # Output
        if not self.output_path:
            raise ValueError("Output path was not set.")
        command += ["-b", str(self.output_path)]

        # Input
        if not self.input_path:
            raise ValueError("Input path was not set.")
        command += ["-i", "-"]

        return command

    def _load_vs_source(self):
        """Loads the source file in a VS object"""
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
                process.wait()

            except subprocess.CalledProcessError as e:
                print(f"Encoder encountered an error:\n{e}")
                sys.exit(1)
