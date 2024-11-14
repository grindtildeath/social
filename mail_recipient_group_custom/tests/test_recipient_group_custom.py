# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import itertools
from markupsafe import Markup

from odoo_test_helper import FakeModelLoader

from odoo.tests import TransactionCase
from odoo.tools import generate_tracking_message_id


class TestMailRecipientGroupCustom(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.admin_user = cls.env.ref("base.user_admin")
        cls.demo_user = cls.env.ref("base.user_demo")

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .model_test import ModelTest
        cls.loader.update_registry((ModelTest,))
        cls.model_test = cls.env["model.test"]
        cls.model_test_record = cls.model_test.create(
            {
                "name": "Test record",
                "partner_id": cls.demo_user.partner_id.id
            }
        )

        # Mimic what is done in mail.thread.message_notify
        email_from = '"Mitchell Admin" <admin@yourcompany.example.com>'
        cls.test_message_values = {
            "author_id": cls.admin_user.partner_id.id,
            "email_from": email_from,
            "model": "model.test",
            "subject": "Test",
            "body": Markup("<p>This is a test message on a test model</p>"),
            "partner_ids": [cls.demo_user.partner_id.id],
            "subtype_id": cls.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
            "message_id": generate_tracking_message_id('message-notify'),
        }

    def test_group_inactive(self):
        new_message = self.model_test._message_create([self.test_message_values])
        recipients_data = self.model_test._notify_get_recipients(new_message, self.test_message_values, **{})
        res = self.model_test._notify_get_recipients_classify(new_message, recipients_data, self.model_test._description, msg_vals=self.test_message_values)
        self.assertIn("group_test", [group["notification_group_name"] for group in res])
        self.assertIn(self.demo_user.partner_id.id, itertools.chain.from_iterable([group.get("recipients") for group in res if group["notification_group_name"] == "group_test"]))
        # Make group_test inactive
        self.env["ir.config_parameter"].set_param(
            "mail_recipient_group_custom.model_test",
            "{'group_test': {'active': False}}"
        )
        res = self.model_test._notify_get_recipients_classify(new_message, recipients_data, self.model_test._description, msg_vals=self.test_message_values)
        breakpoint()
        self.assertNotIn("group_test", [group["notification_group_name"] for group in res])
        self.assertIn(self.demo_user.partner_id.id, itertools.chain.from_iterable([group.get("recipients") for group in res if group["notification_group_name"] == "user"]))
