# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ModelTest(models.Model):
    _name = "model.test"
    _inherit = "mail.thread"
    _description = "Model for testing"

    name = fields.Char()
    partner_id = fields.Many2one("res.partner")

    def _notify_get_recipients_groups(self, message, model_description, msg_vals=None):
        res = super()._notify_get_recipients_groups(message, model_description, msg_vals=msg_vals)
        new_groups = [
            [
                "group_test",
                lambda pdata: True,
                {
                    "active": True,
                    "has_button_access": True,
                }
            ]
        ]
        return new_groups + res
