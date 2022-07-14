# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError


class CMSDepartment(models.Model):
    _name = 'cms.department'
    _description = 'Department Information'

    name = fields.Char('Department Name', required=True)
    student_ids = fields.One2many('cms.student', 'department_id', string='Students')


class CMSStudent(models.Model):
    _name = 'cms.student'
    _description = 'Student Information'

    name = fields.Char('Student Name', required=True)
    father_name = fields.Char('Father Name', required=True)
    registration_no = fields.Char(string='Registration No.', required=True)
    department_id = fields.Many2one('cms.department', string='Department')
    cnic = fields.Char(string='Student CNIC')
    contact_phone = fields.Char('Phone no.')
    contact_mobile = fields.Char('Mobile no')
    image = fields.Binary('image')
    admission_date = fields.Date('Admission Date', default=date.today())
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender', states={'done': [('readonly', True)]}, required=True)

    user_id = fields.Many2one('res.users', string='Responsible', readonly=True, default=lambda self: self.env.user)
    date_of_birth = fields.Date('Date of Birth')
    age = fields.Integer(compute='_compute_student_age', string='Age', readonly=True)
    admission_no = fields.Char(string='Admission No.', readonly=True)
    grad_date = fields.Integer(compute= '_compute_grad_date', string='Graduation Date', readonly=True)

    remark = fields.Text('Remark', states={'done': [('readonly', True)]})

    state = fields.Selection([('draft', 'Draft'), ('verified', 'Verified'), ('approved', 'Approved'),
                              ('cancelled', 'Cancelled')], 'Status', readonly=True, default="draft")

    active = fields.Boolean(default=True)

    employee_ids = fields.Many2many('cms.employee', 'cms_student_employee_rel',
        'student_id', 'employee_id', string='Employees')

    @api.depends('date_of_birth')
    def _compute_student_age(self):
        '''Method to calculate student age'''
        current_date = date.today()
        for rec in self:
            if rec.date_of_birth:
                start = rec.date_of_birth
                age = (current_date - start).days / 365
                # Age should be greater than 0
                if age > 0.0:
                    rec.age = age
                else:
                    rec.age = 0
            else:
                rec.age = 0

    @api.depends('admission_date')
    def _compute_grad_date(self):
        '''Method to calculate expected graduation date'''
        for rec in self:
            if rec.admission_date:
                rec.grad_date = (rec.admission_date).year + 4


    def set_to_draft(self):
        '''Method to change state to draft'''
        self.state = 'draft'

    def set_to_verified(self):
        '''Method to change state to verified'''
        self.state = 'verified'

    def set_to_approved(self):
        '''Method to change state to approved'''

        if self.admission_date:
            year = self.admission_date.year
            self.admission_no  = str(year) + "-" + self.env['ir.sequence'].next_by_code('cms.student.code')
        else:
            raise ValidationError(_('Please enter admission date for student %s)', self.name))

        self.state = 'approved'

    def set_to_cancelled(self):
        '''Set the state to cancelled'''
        self.state = 'cancelled'


class CMSEmployee(models.Model):
    _name = 'cms.employee'
    _description = 'Employee Information'

    name = fields.Char('Teacher Name', required=True)
    father_name = fields.Char('Father Name', required=True)
    employee_no = fields.Char('Employee No.', required=True)
    cnic = fields.Char(string='Employee CNIC')
    is_teacher = fields.Boolean("Is Teacher", default=True)
    active = fields.Boolean(default=True)
    schedule_line=fields.One2many('cms.schedulerline','teacher_id')
    

class CMSBlock(models.Model):
    _name = 'cms.block'
    _description = "Block Info"

    name = fields.Char('Block Name', required=True)
    room_id = fields.One2many("cms.room",'block_id')


class CMSRoom(models.Model):
    _name = 'cms.room'
    _description = "Room Info"

    name = fields.Char('Room Name', required=True)
    room_capacity = fields.Integer("Room Capacity", required=True)
    block_id = fields.Many2one('cms.block',string='Block',required=True)
    # cms_schedule_line_room= fields.Char("o2m->schedule.line")
    cms_schedule_line_room=fields.One2many('cms.schedulerline','room_id')

class CMSCourses(models.Model):
    _name = 'cms.courses'
    _description = 'Courses Information'

    name = fields.Char('Course Name', required=True)
    code = fields.Char('Course Code', required=True)
    # name = fields.One2many('cms.offeredcourses', 'name')
    # code = fields.One2many('cms.offeredcourses', 'course_ids')
    schedule_line= fields.One2many('cms.schedulerline','course_id')

class CMSTimeSlot(models.Model):
    _name = 'cms.timeslot'
    _description = 'Timeslot Information'

    @api.depends('start_time', 'end_time')
    def _set_name(self):
        for rec in self:
            rec.name = str(rec.start_time) + " - " + str(rec.end_time)

    name = fields.Char(compute="_set_name", string='Name', required=True)
    # id=fields.Integer("ID")
    # name=fields.Char("TimeSlot")
    start_time = fields.Float('Start Time', required=True)
    end_time = fields.Float('Ending time', required=True)

    @api.depends('start_time', 'end_time')
    def _set_duration(self):
        for rec in self:
            rec.duration = rec.end_time - rec.start_time

    duration = fields.Float(compute="_set_duration", string='Duration', required=True)
    # duration = fields.Char('Duration', required=True)

    cms_scheduled = fields.Many2one('cms.schedule', string='Scheduled')


    schedulerline = fields.One2many('cms.schedulerline', 'timeslot')




class CMSSchedule(models.Model):
    _name = 'cms.schedule'
    _description = 'Scheduling Information'

    name = fields.Char('Exam Name', required=True)
    start_date = fields.Date('Examination Start Date', default=date.today())
    end_date = fields.Date('Examination End Date', default=date.today())

    timeslot = fields.One2many('cms.timeslot','cms_scheduled')
    schedule_line = fields.One2many('cms.schedulerline', 'schedule_id')
    # schedule_line_many = fields.Many2many('cms.schedulerline')


class CMSSchedulerLine(models.Model):
    _name = 'cms.schedulerline'
    _description = 'Scheduling Line Information'

    @api.depends('course_id', 'teacher_id')
    def _set_name(self):
        for rec in self:
            rec.name = str(rec.course_id.name) + " - " + str(rec.teacher_id.name)

    name = fields.Char(compute="_set_name", string='Name', required=True)
    schedule_id = fields.Many2one('cms.schedule', string="Schedule")
    date = fields.Date('Date', required=True)
    course_id = fields.Many2one('cms.courses', string="Course")
    room_id = fields.Many2one('cms.room', string="Room")
    teacher_id = fields.Many2one('cms.employee', string="Instructor")
    invigilator_id = fields.Many2many('cms.employee', string="Invigilator")
    timeslot = fields.Many2one('cms.timeslot', string='Time')
    active = fields.Boolean(default=True)


