# PC Specs Checker

A beginner-friendly, open-source Python command-line tool that displays basic Windows PC specifications.

## Features

- Operating system and architecture
- CPU name, physical/logical core counts, and current usage
- RAM total, used, available, and percentage
- GPU names reported by Windows
- Disk total, used, free space, and usage
- Export a report to a timestamped TXT file

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- Internet connection for the initial dependency installation

## Setup

1. Install Python from <https://www.python.org/downloads/windows/>.
2. During installation, enable **Add Python to PATH**.
3. Open Command Prompt in this project folder.
4. Install the dependency:

   ```bat
   py -m pip install -r requirements.txt
   ```

5. Run the app:

   ```bat
   py pc_specs_checker.py
   ```

If `py` is unavailable, try `python` instead.

## Notes

- GPU names are read from Windows via PowerShell/CIM. Some driver or hardware details may not be available.
- CPU usage is a short sample, not a benchmark.
- Disk information includes partitions Windows allows the current user to access.
- The program only reads system information and writes a report when you choose the export menu. It does not intentionally send data over the internet.

## Contributing

Issues and pull requests are welcome. Please describe changes clearly and test them on Windows before submitting a pull request.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
