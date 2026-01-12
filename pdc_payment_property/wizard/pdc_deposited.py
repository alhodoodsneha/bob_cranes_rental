from odoo import api, models, fields


class PdcDepositedWizard(models.TransientModel):
    _name = 'pdc.deposited.wizard'
    _description = "PDC Deposited"

    deposited = fields.Many2one('account.journal', string='Deposited',
                                domain="[('type', '=', 'bank')]")
    deposited_on = fields.Date(string='Deposited On')

    def action_add_done(self):
       pdc_id =  self.env['pdc.payment.received'].search(
            [('id', '=', self.env.context.get('active_id'))])
       if pdc_id:
           pdc_id.deposited = self.deposited
           pdc_id.deposited_on = self.deposited_on
           pdc_id.status = 'deposited'



