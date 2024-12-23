from odoo import models, fields, api
from odoo.exceptions import UserError

class ImportAttendanceWizard(models.TransientModel):
    _name = 'import.attendance.wizard'
    _description = 'Import Attendance Wizard'
    
    excel_file = fields.Binary('Excel File', required=True)
    file_name = fields.Char('File Name')
    create_employees = fields.Boolean('Create Missing Employees', default=True,
        help="Automatically create employees that don't exist in the system")
    
    def action_import(self):
        # Create import record
        import_record = self.env['attendance.import'].create({
            'excel_file': self.excel_file,
            'file_name': self.file_name,
        })
        
        # Analyze file
        import_record.action_analyze_file()
        
        if self.create_employees and import_record.missing_employees:
            # Create missing employees
            for badge in import_record.missing_employees.split('\n'):
                if badge:
                    self.env['hr.employee'].create({
                        'name': f'Employee {badge}',
                        'barcode': badge,
                    })
            
            # Re-analyze after creating employees
            import_record.action_analyze_file()
        
        # Import attendance records
        import_record.action_import_attendance()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Result',
            'res_model': 'attendance.import',
            'res_id': import_record.id,
            'view_mode': 'form',
            'target': 'current',
        }
