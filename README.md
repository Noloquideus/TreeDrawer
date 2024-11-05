# TreeDrawer
Draws the file structure of a directory as a tree

# Example Usage
```python
ignored = ['.idea', 'venv', '__pycache__', '.git', '.vscode', '.vscode-insiders', '.github', 'build/', 'dist/']
drawer = TreeDrawer(path=Path('C:/Users/alexm/Documents/!python/Application'), ignored=ignored,
                show_files=True, show_modified_time=True, show_size=True, show_hidden=True)
drawer.draw(as_string=False, save_path=Path('C:/Users/alexm/Documents/!python/TreeCmd'))
```
