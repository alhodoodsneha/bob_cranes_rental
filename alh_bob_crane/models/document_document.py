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
from datetime import date, timedelta


class DocumentsDocument(models.Model):
    _inherit = "documents.document"

    is_expiry = fields.Boolean(
        string="Has Expiry",
        default=False,
        help="Check if this document has an expiry date"
    )

    expiry_date = fields.Date(
        string="Expiry Date",
        help="The date when this document will expire",
    )

    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.today,
        help="Date of issued",
        copy=False
    )

    before_days = fields.Integer(
        string="Days",
        help="How many number of days before to get the notification email."
    )

    notification_type = fields.Selection([
        ('single', 'Notification on expiry date'),
        ('multi', 'Notification before few days'),
        ('everyday', 'Everyday till expiry date'),
        ('everyday_after', 'Notification on and after expiry')
    ],
        string='Notification Type',
        help="Select type of the documents expiry notification."
    )

    notification_to = fields.Many2many(
        'res.partner',
        string='Notification To'
    )

    def mail_reminder(self):
        """Sending document expiry notification to employees."""
        for record in self.search([('expiry_date', '!=', False),('is_expiry','=',True)]):
            exp_date = fields.Date.from_string(record.expiry_date)
            days_before = timedelta(days=record.before_days or 0)
            is_expiry_today = fields.Date.today() == exp_date
            is_notification_day = any([record.notification_type == 'single'
                                       and is_expiry_today,
                                       record.notification_type == 'multi'
                                       and (fields.Date.today() == fields.Date.
                                            from_string(
                                           record.expiry_date) - days_before
                                            or is_expiry_today),
                                       record.notification_type == 'everyday'
                                       and fields.Date.today() >= fields.Date.
                                      from_string(
                                           record.expiry_date) - days_before,
                                       record.notification_type ==
                                       'everyday_after'
                                       and fields.Date.today() <=
                                       fields.Date.from_string(
                                           record.expiry_date) + days_before,
                                       not record.notification_type and
                                       fields.Date.today() == fields.Date.
                                      from_string(
                                           record.expiry_date) - timedelta(
                                           days=7), ])
            if is_notification_day and record.notification_to:
                employee_name = record.partner_id.name
                document_name = record.name
                document_type = record.name
                expiry_date_str = str(record.expiry_date)
                emails = record.notification_to.mapped("email")
                emails = [e for e in emails if e]
                email_list = ",".join(emails)
                mail_content = (
                    f"Hi,<br><br>"
                    f"Customer <b>{employee_name}</b>'s document <b>{document_type}</b> "
                    f"is going to expire on <b>{expiry_date_str}</b>. "
                    "Please renew it before the expiry date."
                )
                subject = _('Document-%s %s Expired On %s') % (document_type,
                                                               document_name,
                                                               expiry_date_str)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': email_list,
                }
                self.env['mail.mail'].create(main_content).send()

