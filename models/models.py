# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import re


class ContractManagement(models.Model):
    _name = 'contract.management'
    _description = 'Table Header for Contract Management'

    name = fields.Char(string='Nama Pekerjaan', required=True)
    parent_id = fields.Many2one(
        'contract.management', string='Parent', ondelete='restrict')
    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='restrict', required=True)
    total = fields.Monetary(string='Nilai', required=True)

    state = fields.Selection([('cancel', 'Cancel'), ('draft', 'Draft'), ('confirm', 'Confirm'), (
        'running', 'Running'), ('close', 'Close')], string='State', default='draft', required=True)

    #######################
    #       BUTTONS       #
    #######################

    def action_confirm(self):
        for rec in self:
            rec.write({'state': 'confirm'})

    def action_run(self):
        for rec in self:
            rec.write({'state': 'running'})

    def action_close(self):
        for rec in self:
            rec.write({'state': 'close'})

    def action_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    ######################
    #        DATE        #
    ######################

    start_date = fields.Date(
        string='Start date', default=fields.Date.today(), required=True)
    end_date = fields.Date(
        string='End date', default=fields.Date.today(), required=True)

    @api.onchange('start_date', 'end_date')
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValidationError('The end date must be after the start date.')

    ######################
    #      CURRENCY      # in case you wondering, currency will shown when we save the data
    ######################

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
    )

    @api.depends('company_id')
    def _compute_currency_id(self):
        for statement in self:
            statement.currency_id = statement.company_id.currency_id

    ######################
    #      One2many      #
    ######################

    contract_management_line = fields.One2many(
        'contract.management.line', 'contract_id', string='Contract Management Line')
    contract_management_files = fields.One2many(
        'contract.management.files', 'contract', string='Contract Management Files')


class ContractManagementLine(models.Model):
    _name = 'contract.management.line'
    _description = 'Contract Management Line'

    contract_id = fields.Many2one(
        'contract.management', string='Nama Pekerjaan', required=True, ondelete='cascade')
    name = fields.Many2one('contract.management.termin',
                           string='Termin', required=True, ondelete='restrict')
    date = fields.Date(
        string='Date', default=fields.Date.today(), required=True)

    percent = fields.Float(
        string='Percent', compute='_compute_percent', inverse='_inverse_percent', store=True, required=True)
    amount = fields.Monetary(string='Amount', compute='_compute_amount',
                             inverse='_inverse_amount', store=True, required=True)

    state = fields.Selection(
        [('running', 'Running'), ('close', 'Close')], string='Status', default='running', required=True)
    nota_verif = fields.Char(string='No. Nota Verifikasi')

    notify_before = fields.Selection([('3', '3 hari sebelum'), ('7', '1 minggu sebelum'), ('14', '2 minggu sebelum'), (
        '30', '1 bulan (30 hari) sebelum')], string='Ingatkan sebelum', default='7', required=True)
    email_to = fields.Char(string='Email ke', required=True)
    email_cc = fields.Char(string='CC')

    ########################
    #       VALIDITY       #
    ########################

    @api.constrains('email')
    def _check_valid_email(self):
        for record in self:
            if record.email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.email):
                raise ValidationError("Invalid email format")

    #########################################
    #       PERCENTAGE, AMOUNT, TOTAL       #
    #########################################

    @api.depends('percent', 'contract_id.total')
    def _compute_amount(self):
        for record in self:
            if record.percent:
                record.amount = record.contract_id.total * record.percent
                record._check_total()

    def _inverse_amount(self):
        for record in self:
            if record.amount:
                record.percent = record.amount / record.contract_id.total

    @api.depends('amount', 'contract_id.total')
    def _compute_percent(self):
        for record in self:
            if record.amount:
                record.percent = record.amount / record.contract_id.total

    def _inverse_percent(self):
        for record in self:
            if record.percent:
                record.amount = record.contract_id.total * record.percent
                record._check_total()

    def _check_total(self):
        sum_amount = 0

        for i in self.contract_id.contract_management_line:
            sum_amount += i.amount

        if sum_amount > self.contract_id.total:
            raise ValidationError(
                f'Total amount contract line untuk pekerjaan "{self.contract_id.name}" melebihi total seharusnya')

    #######################
    #       BUTTONS       #
    #######################

    def action_close(self):
        for rec in self:
            if rec.nota_verif:  # close only works when the field 'nota_verif' is filled
                rec.write({'state': 'close'})
            else:
                raise ValidationError(
                    "No Nota Verifikasi harus diisi sebelum close")

    def action_run(self):
        for rec in self:
            rec.write({'state': 'running'})

    ######################
    #      CURRENCY      #
    ######################

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
    )

    @api.depends('company_id')
    def _compute_currency_id(self):
        for statement in self:
            statement.currency_id = statement.company_id.currency_id

    ######################
    # EMAIL NOTIFICATION #
    ######################

    def remind_before_date_termin(self):
        records = self.env['contract.management.line'].search(
            [('state', '=', 'running')])

        for rec in records:
            reminder = int(rec.notify_before)
            date_time = rec.date - timedelta(days=reminder)

            email_template = self.env.ref(
                'contract_management_system.email_notify_termin')

            if date_time == date.today():
                email_template.sudo().send_mail(self.id, force_send=True)

    ### FOR TESTING PURPOSE ONLY ###
    def remind_before_date_termin_TEST(self):

        for rec in self:
            email_template = self.env.ref(
                'contract_management_system.email_notify_termin')

            email_template.sudo().send_mail(rec.id, force_send=True)

######################
#  CONTRACT TERMINS  #
######################


class ContractManagementTermin(models.Model):
    _name = 'contract.management.termin'
    _description = 'Contract Management Termin'
    _sql_constraints = [
        ('unique_name',
         'unique(name)',
         'Choose another value - it has to be unique!')
    ]

    name = fields.Char(string='Nama Termin', required=True)

    contract_management_line = fields.One2many(
        'contract.management.line', 'name', string='Contract Management Line', readonly=True)

######################
#   CONTRACT FILES   #
######################


class ContractFiles(models.Model):
    _name = 'contract.management.files'
    _description = 'Contract Management Files'

    category = fields.Selection([('pengadaan', 'Dokumen Pengadaan'), ('kontrak', 'Dokumen Kontrak'),
                                ('output', 'Dokumen Output')], string='Jenis dokumen', required=True)
    name = fields.Char(string='Nama file')
    notes = fields.Char(string='Keterangan')

    file = fields.Binary(string='File', required=True,
                         attachment=True, button_text='Dokumen PDF')

    @api.constrains('file')
    def _check_attachments(self):
        exceed_limit = []
        limit = eval(self.env['ir.config_parameter'].sudo().get_param(
            'contract_managemet_system.limit_upload_in_MB', '1'))
        for rec in self:
            if rec.file:
                file_data = self.env['ir.attachment'].create({
                    'name': rec.name,
                    'type': 'binary',
                    'datas': rec.file,
                    'res_model': rec._name,
                    'res_id': rec.id,
                })
                if file_data.file_size > limit * 1024 * 1024 or file_data.mimetype != 'application/pdf':
                    exceed_limit.append(f"- {rec.name}")
        if exceed_limit:
            exceed_limit = '\n'.join(exceed_limit)
            raise UserError(
                f"Dokumen berikut melebihi {limit} MB Atau Format yang diupload bukan PDF:\n{exceed_limit}")

    contract = fields.Many2one(
        'contract.management', string='Nama Pekerjaan', required=True, ondelete='cascade')
