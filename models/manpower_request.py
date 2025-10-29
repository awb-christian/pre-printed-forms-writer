# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date


class ManpowerRequest(models.Model):
    _name = 'manpower.request'
    _description = 'Manpower Request'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Requisition ID',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    date_requested = fields.Date(
        string='Date Requested',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    
    duration_days = fields.Integer(
        string='Duration (Days)',
        compute='_compute_duration_days',
        store=True,
        help='Number of days since the request was created'
    )
    
    request_type = fields.Selection([
        ('new_position', 'New Position'),
        ('replacement', 'Replacement'),
        ('additional_headcount', 'Additional Headcount'),
        ('project_based', 'Project-based')
    ], string='Request Type', required=True, tracking=True)
    
    request_status = fields.Selection([
        ('draft', 'Draft'),
        ('for_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('on_hold', 'On Hold')
    ], string='Request Status', default='draft', required=True, tracking=True)
    
    urgency_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Urgency/Priority Level', required=True, tracking=True)
    
    # Additional fields for better tracking
    requested_by = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        tracking=True
    )
    
    position_title = fields.Char(
        string='Position Title',
        required=True,
        tracking=True
    )
    
    job_description = fields.Text(
        string='Job Description',
        tracking=True
    )
    
    required_skills = fields.Text(
        string='Required Skills',
        tracking=True
    )
    
    experience_required = fields.Char(
        string='Experience Required',
        tracking=True
    )
    
    education_required = fields.Char(
        string='Education Required',
        tracking=True
    )
    
    expected_start_date = fields.Date(
        string='Expected Start Date',
        tracking=True
    )
    
    budget_allocated = fields.Monetary(
        string='Budget Allocated',
        currency_field='currency_id',
        tracking=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    justification = fields.Text(
        string='Justification',
        required=True,
        tracking=True,
        help='Business justification for this manpower request'
    )
    
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        tracking=True
    )
    
    approval_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        tracking=True
    )
    
    rejection_reason = fields.Text(
        string='Rejection Reason',
        readonly=True,
        tracking=True
    )
    
    notes = fields.Text(
        string='Notes',
        tracking=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('manpower.request') or _('New')
        return super(ManpowerRequest, self).create(vals)

    @api.depends('date_requested')
    def _compute_duration_days(self):
        for record in self:
            if record.date_requested:
                today = date.today()
                delta = today - record.date_requested
                record.duration_days = delta.days
            else:
                record.duration_days = 0

    def action_submit_for_approval(self):
        self.write({
            'request_status': 'for_approval'
        })
        return True

    def action_approve(self):
        self.write({
            'request_status': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
        return True

    def action_reject(self):
        return {
            'name': 'Reject Request',
            'type': 'ir.actions.act_window',
            'res_model': 'manpower.request.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id}
        }

    def action_hold(self):
        self.write({'request_status': 'on_hold'})
        return True

    def action_reset_to_draft(self):
        self.write({
            'request_status': 'draft',
            'approved_by': False,
            'approval_date': False,
            'rejection_reason': False
        })
        return True

    @api.model
    def _get_urgency_color(self):
        color_map = {
            'low': 0,      # No color
            'medium': 1,   # Green
            'high': 2,     # Orange
            'critical': 3  # Red
        }
        return color_map.get(self.urgency_level, 0)

    @api.model
    def _get_status_color(self):
        color_map = {
            'draft': 0,        # No color
            'for_approval': 1, # Green
            'approved': 2,     # Blue
            'rejected': 3,     # Red
            'on_hold': 4       # Orange
        }
        return color_map.get(self.request_status, 0)


class ManpowerRequestRejectWizard(models.TransientModel):
    _name = 'manpower.request.reject.wizard'
    _description = 'Manpower Request Rejection Wizard'

    request_id = fields.Many2one('manpower.request', string='Request', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True)

    def action_reject(self):
        self.request_id.write({
            'request_status': 'rejected',
            'rejection_reason': self.rejection_reason
        })
        return {'type': 'ir.actions.act_window_close'}