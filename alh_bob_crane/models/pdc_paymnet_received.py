# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License
#    (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class PdcPaymentReceived(models.Model):
    _inherit = 'pdc.payment.received'

    def action_draft_to_receive(self):
        pdc_journal_id = self.env['account.journal'].search([('is_pdc','=',True)], limit=1)
        if not pdc_journal_id:
            raise UserError(_('Please Configure the PDC Journal'))
        debit_acc_id = pdc_journal_id.debit_account_id
        credit_acc_id = pdc_journal_id.credit_account_id
        journal_entry_lines = [
            (0, 0, {
                'debit': self.amount,
                'credit': 0.0,
                'account_id': debit_acc_id.id,
            }),
            (0, 0, {
                'debit': 0.0,
                'credit': self.amount,
                'account_id': credit_acc_id.id,
            })
        ]
        journal_entry = self.env['account.move'].create({
            'journal_id':pdc_journal_id.id,
            'date': fields.Date.today(),
            'line_ids': journal_entry_lines,
            'ref': f"Journal Entry for PDC {self.cheque_no}",
            'move_type': 'entry',
            'state': 'draft',
            'pdc_received_id': self.id,
        })
        res = super(PdcPaymentReceived, self).action_draft_to_receive()
        return res


    def action_matured(self):
        pdc_journal_id = self.env['account.journal'].search([('is_pdc','=',True)], limit=1)
        if not pdc_journal_id:
            raise UserError(_('Please Configure the PDC Journal'))
        debit_acc_id = pdc_journal_id.credit_account_id
        credit_acc_id = pdc_journal_id.debit_account_id
        journal_entry_lines = [
            (0, 0, {
                'debit': self.amount,
                'credit': 0.0,
                'account_id': debit_acc_id.id,
            }),
            (0, 0, {
                'debit': 0.0,
                'credit': self.amount,
                'account_id': credit_acc_id.id,
            })
        ]
        journal_entry = self.env['account.move'].create({
            'journal_id':pdc_journal_id.id,
            'date': fields.Date.today(),
            'line_ids': journal_entry_lines,
            'ref': f"Journal Entry for PDC {self.cheque_no}",
            'move_type': 'entry',
            'state': 'draft',
            'pdc_received_id': self.id,
        })
        payment_id = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.customer_id.id,
            'amount': self.amount,
            'memo': self.cheque_no,
            'journal_id': self.deposited.id,
            'pdc_received_id': self.id,
        })
        self.payment_id = payment_id.id
        res = super(PdcPaymentReceived, self).action_matured()
        return res

    def action_view_journal_entry(self):
        journal_ids = self.env['account.move'].sudo().search(
            [('pdc_received_id', '=', self.id)])
        if journal_ids:
            return {
                'name': 'Journals',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'account.move',
                'domain': [('id', '=', journal_ids.ids)],
                'type': 'ir.actions.act_window',
                'context': {
                    'create':False,
                    'delete':False,
                }
            }

    def action_view_payment_invoice(self):
        payments = self.env['account.payment'].sudo().search(
            [('pdc_received_id', '=', self.id)])
        if payments:
            return {
                'name': 'Payments',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'account.payment',
                'domain': [('id', '=', payments.ids)],
                'type': 'ir.actions.act_window',
                'context': {
                    'create': False,
                    'delete': False,
                }
            }

    def action_create_legal(self):
        return {
            'name': 'Legal case',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'legal.case',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_project_id':self.project_id.id,
                'default_pdc_received_id':self.id,
                'default_partner_id':self.partner_id.id,
            }
        }

    def action_view_legal_cases(self):
        return {
            'name': 'Legal Cases',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'legal.case',
            'domain': [('pdc_received_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False,
                'default_project_id':self.project_id.id,
                'default_pdc_received_id':self.id,
                'default_partner_id': self.partner_id.id,

            }
        }
