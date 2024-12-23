{
    'name': 'Attendance Import',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Attendances',
    'summary': 'Import attendance records from Excel files',
    'description': """
        This module allows you to:
        * Import attendance records from Excel files
        * Visualize attendance data before import
        * Create missing employees automatically
        * View import history and statistics
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_import_views.xml',
        'views/attendance_import_templates.xml',
        'wizard/import_attendance_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'attendance_import/static/src/js/attendance_import.js',
            'attendance_import/static/src/css/attendance_import.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
