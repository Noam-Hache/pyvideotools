from abc import ABC, abstractmethod
from pathlib import Path


class CommandBuilder(ABC):
    _encoder: str

    _input_path: Path
    _output_path: Path
    _is_input_vpy: bool = False

    _bitrate: int
    _crf: float
    _tune: str
    _preset: str
    _passes: int

    _additional_parameters: list[str]

    def __init__(self) -> None:
        self._additional_parameters = []

    def input(self, path: str, is_input_vpy: bool = False) -> None:
        """Validates and sets the input file"""
        input_path = Path(path)

        if not input_path.exists() or not input_path.is_file():
            raise FileNotFoundError(f"The input file does not exist.\n{input_path}")

        self.input_path = input_path
        self._is_input_vpy = is_input_vpy

    def output(self, path: str, overwrite: bool = False) -> None:
        """Validates and sets the output file"""
        output_path = Path(path)

        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"The output file already exists. Use the overwrite flag.\n{output_path}"
            )

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
        """Sets the tune"""
        self._tune = _tune

    def passes(self, _passes: int) -> None:
        """Validates and sets the pass count"""
        if _passes > 2:
            raise ValueError("Pass count cannot exceed 2.")
        self._passes = _passes

    def encoder(self, path: str):
        """Sets the encoder executable path"""
        self._encoder = path

    def other(self, parameter: str, value: str = ""):
        if not parameter:
            raise ValueError()

        self._additional_parameters += [parameter, value]

    @abstractmethod
    def run(self) -> None:
        """Runs the command"""

    @abstractmethod
    def preset(self, _preset: str):
        """Sets the bitrate"""

    @abstractmethod
    def get_command(self) -> list[str]:
        """Returns the command"""

    @abstractmethod
    def validate_command(self) -> bool:
        """Validates the command"""
