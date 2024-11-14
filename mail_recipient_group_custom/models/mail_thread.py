# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import models
from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_get_recipients_groups_fillup(self, groups, model_description, msg_vals=None):
        res = super()._notify_get_recipients_groups_fillup(groups, model_description, msg_vals=msg_vals)
        custom_params = self._get_recipients_groups_customizations()
        for custom_param in custom_params:
            custom_param_value = safe_eval(custom_param.value)
            for group in res:
                for group_name, changes in custom_param_value.items():
                    if group[0] == group_name:
                        group[2].update(changes)
        return res

    def _get_recipients_groups_customizations(self):
        res = {}
        generic = self.env["ir.config_parameter"].search([("key", "=", "mail_recipient_group_custom")])
        model_specific = self.env["ir.config_parameter"].search([("key", "like", "mail_recipient_group_custom.%s" % self._name.replace(".", "_"))])
        return generic | model_specific
