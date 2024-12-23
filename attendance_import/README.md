# Odoo Attendance Import Module

An Odoo 18 module for importing attendance records from Excel files with automatic employee creation and data visualization.

## Features

- Import attendance records from Excel files
- Automatically create missing employees
- View import history and statistics
- Error handling and logging
- User-friendly interface
- Detailed progress tracking
- Import validation and error reporting

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/odoo-attendance-import.git
```

2. Copy the `attendance_import` folder to your Odoo addons directory:
```bash
cp -r attendance_import /path/to/odoo/addons
```

3. Update your Odoo apps list and install the module:
   - Go to Apps
   - Click "Update Apps List"
   - Search for "Attendance Import"
   - Click Install

## Usage

1. Go to Attendance > Import Attendance
2. Upload your Excel file
3. Choose whether to create missing employees automatically
4. Click Import and review the results

### Excel File Format

Required columns:
- `AC-No.`: Employee badge number
- `Time`: Date and time of the attendance
- `State`: Check-in (C/In) or Check-out (C/Out)

Example:
```
AC-No. | Time                | State
-------------------------------------
102    | 2024-11-24 08:00:00| C/In
102    | 2024-11-24 16:00:00| C/Out
```

## Configuration

No special configuration is needed. The module will work with default settings.

## Security

The module uses Odoo's standard security groups:
- HR Attendance User: Can import attendance records and view import history

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the LGPL-3 License - see the LICENSE file for details.

## Support

For support, please create an issue in the GitHub repository or contact the maintainers.

## Authors

- Your Name - Initial work - [YourGitHub](https://github.com/yourusername)

## Acknowledgments

- Thanks to the Odoo community for their excellent documentation
- Inspired by the need for efficient attendance data import solutions
