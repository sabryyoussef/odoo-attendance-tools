from odoo import models, fields, api
from odoo.exceptions import UserError
import pandas as pd
import base64
import io
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class AttendanceImport(models.Model):
    _name = 'attendance.import'
    _description = 'Attendance Import'
    _order = 'create_date desc'

    name = fields.Char('Name', required=True, default=lambda self: self.env['ir.sequence'].next_by_code('attendance.import'))
    excel_file = fields.Binary('Excel File', required=True)
    file_name = fields.Char('File Name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('analyzed', 'Analyzed'),
        ('imported', 'Imported'),
        ('failed', 'Failed')
    ], string='Status', default='draft')
    
    total_records = fields.Integer('Total Records', readonly=True)
    successful_imports = fields.Integer('Successful Imports', readonly=True)
    failed_imports = fields.Integer('Failed Imports', readonly=True)
    
    import_date = fields.Datetime('Import Date', readonly=True)
    imported_by = fields.Many2one('res.users', string='Imported By', readonly=True)
    
    import_log = fields.Text('Import Log', readonly=True)
    error_log = fields.Text('Error Log', readonly=True)
    
    missing_employees = fields.Text('Missing Employees', readonly=True)
    attendance_line_ids = fields.One2many('attendance.import.line', 'import_id', string='Attendance Lines')
    
    def action_analyze_file(self):
        self.ensure_one()
        try:
            # Read Excel file
            excel_data = base64.b64decode(self.excel_file)
            df = pd.read_excel(io.BytesIO(excel_data))
            
            # Validate columns
            required_columns = ['AC-No.', 'Time', 'State']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise UserError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Convert Time column to datetime
            df['Time'] = pd.to_datetime(df['Time'])
            df['Date'] = df['Time'].dt.date
            
            # Process records
            attendance_records = []
            missing_employees = set()
            
            # Group by AC-No. and Date
            for (employee_id, date), group in df.groupby(['AC-No.', 'Date']):
                check_ins = group[group['State'] == 'C/In']['Time']
                check_outs = group[group['State'] == 'C/Out']['Time']
                
                if not check_ins.empty and not check_outs.empty:
                    first_check_in = check_ins.min()
                    last_check_out = check_outs.max()
                    
                    if first_check_in < last_check_out:
                        # Check if employee exists
                        employee = self.env['hr.employee'].search([('barcode', '=', str(employee_id))], limit=1)
                        if not employee:
                            missing_employees.add(str(employee_id))
                        
                        attendance_records.append({
                            'employee_badge': str(employee_id),
                            'check_in': first_check_in,
                            'check_out': last_check_out,
                            'total_hours': (last_check_out - first_check_in).total_seconds() / 3600
                        })
            
            # Create attendance lines
            self.attendance_line_ids.unlink()
            for record in attendance_records:
                self.env['attendance.import.line'].create({
                    'import_id': self.id,
                    'employee_badge': record['employee_badge'],
                    'check_in': record['check_in'],
                    'check_out': record['check_out'],
                    'total_hours': record['total_hours']
                })
            
            # Update import record
            self.write({
                'state': 'analyzed',
                'total_records': len(attendance_records),
                'missing_employees': '\n'.join(missing_employees) if missing_employees else 'All employees found'
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'File analyzed successfully. Found {len(attendance_records)} records.',
                    'sticky': False,
                    'type': 'success'
                }
            }
            
        except Exception as e:
            self.write({
                'state': 'failed',
                'error_log': str(e)
            })
            raise UserError(f"Error analyzing file: {str(e)}")
    
    def action_import_attendance(self):
        self.ensure_one()
        if self.state != 'analyzed':
            raise UserError("Please analyze the file first")
        
        success_count = 0
        error_count = 0
        error_log = []
        
        for line in self.attendance_line_ids:
            try:
                employee = self.env['hr.employee'].search([('barcode', '=', line.employee_badge)], limit=1)
                if not employee:
                    error_count += 1
                    error_log.append(f"Employee with badge {line.employee_badge} not found")
                    continue
                
                # Create attendance record
                self.env['hr.attendance'].create({
                    'employee_id': employee.id,
                    'check_in': line.check_in,
                    'check_out': line.check_out
                })
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_log.append(f"Error for employee {line.employee_badge}: {str(e)}")
        
        self.write({
            'state': 'imported' if error_count == 0 else 'failed',
            'successful_imports': success_count,
            'failed_imports': error_count,
            'import_date': fields.Datetime.now(),
            'imported_by': self.env.user.id,
            'error_log': '\n'.join(error_log) if error_log else ''
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Complete',
                'message': f'Successfully imported {success_count} records. Failed: {error_count}',
                'sticky': False,
                'type': 'success' if error_count == 0 else 'warning'
            }
        }

class AttendanceImportLine(models.Model):
    _name = 'attendance.import.line'
    _description = 'Attendance Import Line'
    
    import_id = fields.Many2one('attendance.import', string='Import', required=True, ondelete='cascade')
    employee_badge = fields.Char('Employee Badge', required=True)
    check_in = fields.Datetime('Check In', required=True)
    check_out = fields.Datetime('Check Out', required=True)
    total_hours = fields.Float('Total Hours', digits=(10, 2))
    
    employee_id = fields.Many2one('hr.employee', string='Employee', compute='_compute_employee')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('imported', 'Imported'),
        ('failed', 'Failed')
    ], string='Status', default='pending')
    
    @api.depends('employee_badge')
    def _compute_employee(self):
        for record in self:
            record.employee_id = self.env['hr.employee'].search([('barcode', '=', record.employee_badge)], limit=1)
