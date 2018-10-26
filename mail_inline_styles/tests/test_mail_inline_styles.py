# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import lxml.html
from odoo.tests import SavepointCase
import tinycss

# TODO How should we define tinycss dependency if only needed for tests ?


TEMPLATE_STYLES = """
        <style>
          #main_wrapper {
            max-width: 620px;
            margin: 0 auto;
            border: 1px solid #ccc;
            font-size: 18px;
            font-family: verdana;
            color: #6B6E71;
          }
          a { color: #3BA0A6; text-decoration: none }
          #main_header, footer, main > div { padding: 30px 40px }
          #main_header table { width: 100% }
          #main_header table td { width: 50% }
          #main_logo { max-width: 300px }
          #main_header .right {
            text-align: right;
            vertical-align: top;
            font-size: 140%;
          }
          #main_header .date_today { text-transform: uppercase; opacity: 0.7; color: #FF0000 }
          footer { padding-top: 0; font-size: 120% }
          footer address { font-style: normal }
          .greeting { padding-top: 0; padding-bottom: 0 }
          .image-wrapper {
            min-height: 250px;
          }
          .image-wrapper.location-map {
            margin: 0 -40px;
          }
          .pt0 { padding-top: 0 }
          a.contact { cursor: pointer }
        </style>
"""


class TestMailInlineStyles(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mail_template = cls.env.ref(
            'mail_inline_styles.email_template_demo')
        cls.demo_user = cls.env.ref('base.user_demo')
        cls.parser = tinycss.make_parser()

    def parse_style(self, style_string):
        style_attrs = self.parser.parse_style_attr(style_string)
        return (
            # First list contains valid CSS properties (name, value)
            sorted(
                [(decl.name, decl.value.as_css()) for decl in style_attrs[0]],
                key=lambda td: td[0]
            ),
            # Second list contains invalid CSS properties (name, value)
            sorted(
                [(decl.name, decl.value.as_css()) for decl in style_attrs[1]],
                key=lambda td: td[0]
            ),
        )

    def assertIdStyle(self, html, _id, res):
        style = html.get_element_by_id(_id).get('style')
        parsed_style = self.parse_style(style)
        parsed_res = self.parse_style(res)
        self.assertListEqual(parsed_style[0], parsed_res[0])
        self.assertListEqual(parsed_style[1], parsed_res[1])

    def assertXPathStyle(self, html, xpath_expr, res):
        style = html.xpath(xpath_expr)[0].get('style')
        parsed_style = self.parse_style(style)
        parsed_res = self.parse_style(res)
        self.assertListEqual(parsed_style[0], parsed_res[0])
        self.assertListEqual(parsed_style[1], parsed_res[1])

    def test_generate_mail(self):
        res = self.mail_template.generate_email(
            [self.demo_user.id], fields=['body_html']
        )
        body_html_string = res[self.demo_user.id].get('body_html')
        body_html = lxml.html.fromstring(body_html_string)
        # TODO Try to use a tinycss parser to compute applied styles on each
        # element using TEMPLATE_STYLES
        self.assertIdStyle(body_html, 'main_logo', 'max-width:300px')
        self.assertIdStyle(body_html, 'main_wrapper',
                           'max-width: 620px; margin: 0 auto; '
                           'border: 1px solid #ccc; font-size: 18px; '
                           'font-family: verdana; color: #6B6E71;')
        # FIXME using a parser ?
        self.assertXPathStyle(body_html, '//footer',
                              'padding-top: 0; font-size: 120%')
