from pathlib import Path
from typing import List, Optional
import fnmatch
import colorama
from datetime import datetime


class TreeDrawer:
    """
    A class to draw a tree structure of files and directories with additional details
    such as modified time, size, and hidden files handling.

    Attributes:
        path (Path): The directory to generate the tree structure from.
        ignored_patterns (set): A list of file patterns to ignore.
        show_files (bool): Flag to show files in the tree.
        show_modified_time (bool): Flag to show last modified time for files and directories.
        show_size (bool): Flag to show the size of files and directories.
        show_hidden (bool): Flag to show hidden files (files starting with a dot).
    """

    __FORK_STRING = colorama.Fore.WHITE + '├──'
    __CORNER_STRING = colorama.Fore.WHITE + '└──'
    __WALL_STRING = colorama.Fore.WHITE + '│  '
    __SPACE_STRING = '   '

    def __init__(
            self,
            path: Path = Path('.'),
            ignored: List[str] = [],
            show_files: bool = True,
            show_modified_time: bool = False,
            show_size: bool = False,
            show_hidden: bool = False
    ):
        """
        Initializes the TreeDrawer instance with the given options.

        Args:
            path (Path): The directory to draw the tree structure for (defaults to the current directory).
            ignored (List[str]): List of patterns for files and directories to ignore.
            show_files (bool): Whether to include files in the tree structure (default is True).
            show_modified_time (bool): Whether to show the last modified time of files (default is False).
            show_size (bool): Whether to show the size of files and directories (default is False).
            show_hidden (bool): Whether to show hidden files (default is False).
        """
        self.path = path
        self.show_files = show_files
        self.ignored_patterns = set(ignored)
        self.show_modified_time = show_modified_time
        self.show_size = show_size
        self.show_hidden = show_hidden
        colorama.init(autoreset=True)

    def _is_ignored(self, name: str) -> bool:
        """
        Check if a given file or directory should be ignored based on the ignored patterns.

        Args:
            name (str): The name of the file or directory to check.

        Returns:
            bool: True if the file or directory matches any ignored pattern, False otherwise.
        """
        return any(fnmatch.fnmatch(name, pattern) for pattern in self.ignored_patterns)

    @staticmethod
    def _is_hidden(name: str) -> bool:
        """
        Check if a file or directory is hidden (i.e., starts with a dot).

        Args:
            name (str): The name of the file or directory to check.

        Returns:
            bool: True if the file or directory is hidden, False otherwise.
        """
        return name.startswith('.')

    @staticmethod
    def _get_size(size: int) -> str:
        """
        Convert a file size (in bytes) to a human-readable string.

        Args:
            size (int): The size of the file in bytes.

        Returns:
            str: The size formatted as bytes (B), kilobytes (KB), or megabytes (MB).
        """
        if size < 1024:
            return f'({size} B)'
        elif size < 1024 * 1024:
            return f'({size / 1024:.1f} KB)'
        else:
            return f'({size / (1024 * 1024):.1f} MB)'

    def _get_directory_size(self, path: Path) -> str:
        """
        Calculate the total size of a directory, including all files inside it.

        Args:
            path (Path): The path to the directory.

        Returns:
            str: The total size of the directory.
        """
        total_size = sum(file.stat().st_size for file in path.rglob('*') if file.is_file())
        return self._get_size(total_size)

    def _tree_structure(self, path: Path, prefix: str = '') -> List[str]:
        """
        Recursively build the tree structure for the specified directory.

        Args:
            path (Path): The current directory to process.
            prefix (str): The prefix to use for each line, indicating tree structure depth.

        Returns:
            List[str]: A list of strings representing the tree structure.
        """
        entries = [e for e in path.iterdir() if not self._is_ignored(e.name)]

        if not self.show_files:
            entries = [e for e in entries if e.is_dir()]

        if not self.show_hidden:
            entries = [e for e in entries if not self._is_hidden(e.name)]

        entries.sort(key=lambda x: (x.is_file(), x.name))

        result = []
        for i, entry in enumerate(entries):
            connector = self.__CORNER_STRING if i == len(entries) - 1 else self.__FORK_STRING
            if entry.is_dir():
                modified_time = datetime.fromtimestamp(entry.stat().st_mtime).strftime(
                    '%Y-%m-%d %H:%M') if self.show_modified_time else ''
                size = self._get_directory_size(entry) if self.show_size else ''
                line = f'{prefix}{connector} {colorama.Fore.BLUE}{entry.name}/'
                if modified_time or size:
                    if modified_time:
                        line += f' {colorama.Fore.WHITE}[Modified: {modified_time}]'
                    if size:
                        line += f' {colorama.Fore.WHITE}[Size: {size}]'
            else:
                line = f'{prefix}{connector} {colorama.Fore.GREEN}{entry.name}'

                if self.show_modified_time:
                    modified_time = datetime.fromtimestamp(entry.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                    line += f' {colorama.Fore.WHITE}[Modified: {modified_time}]'

                if self.show_size and entry.is_file():
                    size = self._get_size(entry.stat().st_size)
                    line += f' {colorama.Fore.WHITE}[Size: {size}]'

            result.append(line)

            if entry.is_dir():
                result.extend(self._tree_structure(entry, prefix + (
                    self.__SPACE_STRING if i == len(entries) - 1 else self.__WALL_STRING)))
        return result

    def draw(self, as_string: bool = True, save_path: Optional[Path] = None) -> str:
        """
        Generate the tree structure for the directory and print/save it.

        Args:
            as_string (bool): Whether to return the result as a string (default is True).
            save_path (Optional[Path]): If provided, the output will be saved to the specified path.

        Returns:
            str: The tree structure output as a string if `as_string` is True.
        """
        if not self.path.is_dir():
            raise ValueError('The specified path is not a directory.')

        root_modified_time = datetime.fromtimestamp(self.path.stat().st_mtime).strftime(
            '%Y-%m-%d %H:%M') if self.show_modified_time else ''
        root_size = self._get_directory_size(self.path) if self.show_size else ''

        result = [colorama.Fore.BLUE + self.path.name + '/']
        if root_modified_time or root_size:
            if root_modified_time:
                result[0] += f' {colorama.Fore.WHITE}[Modified: {root_modified_time}]'
            if root_size:
                result[0] += f' {colorama.Fore.WHITE}[Size: {root_size}]'

        result.extend(self._tree_structure(self.path))

        output = '\n'.join(result)
        if save_path:
            save_path = save_path / 'tree_structure.txt'
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(
                    output.replace(colorama.Fore.BLUE, '').replace(colorama.Fore.GREEN, '').replace(colorama.Fore.WHITE, ''))
            print(f'Tree structure saved to {save_path}')

        if as_string:
            return output
        print(output)
        return ''
