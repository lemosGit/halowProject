# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import random
import re

from odoo import api, Command, fields, models, modules, _


class ImLivechatChannel(models.Model):
    """ Livechat Channel
        Define a communication channel, which can be accessed with 'script_external' (script tag to put on
        external website), 'script_internal' (code to be integrated with odoo website) or via 'web_page' link.
        It provides rating tools, and access rules for anonymous people.
    """

    _name = 'im_livechat.channel'
    _inherit = ['rating.parent.mixin']
    _description = 'Livechat Channel'
    _rating_satisfaction_days = 14  # include only last 14 days to compute satisfaction

    def _default_user_ids(self):
        return [(6, 0, [self._uid])]

    def _default_button_text(self):
        return _('Have a Question? Chat with us.')

    def _default_default_message(self):
        return _('How may I help you?')

    # attribute fields
    name = fields.Char('Channel Name', required=True)
    button_text = fields.Char('Text of the Button', default=_default_button_text,
        help="Default text displayed on the Livechat Support Button", translate=True)
    default_message = fields.Char('Welcome Message', default=_default_default_message,
        help="This is an automated 'welcome' message that your visitor will see when they initiate a new conversation.", translate=True)
    input_placeholder = fields.Char('Chat Input Placeholder', help='Text that prompts the user to initiate the chat.', translate=True)
    header_background_color = fields.Char(default="#875A7B", help="Default background color of the channel header once open")
    title_color = fields.Char(default="#FFFFFF", help="Default title color of the channel once open")
    button_background_color = fields.Char(default="#875A7B", help="Default background color of the Livechat button")
    button_text_color = fields.Char(default="#FFFFFF", help="Default text color of the Livechat button")

    # computed fields
    web_page = fields.Char('Web Page', compute='_compute_web_page_link', store=False, readonly=True,
        help="URL to a static page where you client can discuss with the operator of the channel.")
    are_you_inside = fields.Boolean(string='Are you inside the matrix?',
        compute='_are_you_inside', store=False, readonly=True)
    available_operator_ids = fields.Many2many('res.users', compute='_compute_available_operator_ids')
    script_external = fields.Html('Script (external)', compute='_compute_script_external', store=False, readonly=True, sanitize=False)
    nbr_channel = fields.Integer('Number of conversation', compute='_compute_nbr_channel', store=False, readonly=True)

    image_128 = fields.Image("Image", max_width=128, max_height=128)

    # relationnal fields
    user_ids = fields.Many2many('res.users', 'im_livechat_channel_im_user', 'channel_id', 'user_id', string='Operators', default=_default_user_ids)
    channel_ids = fields.One2many('discuss.channel', 'livechat_channel_id', 'Sessions')
    chatbot_script_count = fields.Integer(string='Number of Chatbot', compute='_compute_chatbot_script_count')
    rule_ids = fields.One2many('im_livechat.channel.rule', 'channel_id', 'Rules')

    def _are_you_inside(self):
        for channel in self:
            channel.are_you_inside = bool(self.env.uid in [u.id for u in channel.user_ids])

    @api.depends('user_ids.im_status')
    def _compute_available_operator_ids(self):
        for record in self:
            record.available_operator_ids = record.user_ids.filtered(lambda user: user.im_status == 'online')

    @api.depends('rule_ids.chatbot_script_id')
    def _compute_chatbot_script_count(self):
        data = self.env['im_livechat.channel.rule']._read_group(
            [('channel_id', 'in', self.ids)], ['channel_id'], ['chatbot_script_id:count_distinct'])
        mapped_data = {channel.id: count_distinct for channel, count_distinct in data}
        for channel in self:
            channel.chatbot_script_count = mapped_data.get(channel.id, 0)

    def _compute_script_external(self):
        values = {
            "dbname": self._cr.dbname,
        }
        for record in self:
            values["channel_id"] = record.id
            values["url"] = record.get_base_url()
            record.script_external = self.env['ir.qweb']._render('im_livechat.external_loader', values) if record.id else False

    def _compute_web_page_link(self):
        for record in self:
            record.web_page = "%s/im_livechat/support/%i" % (record.get_base_url(), record.id) if record.id else False

    @api.depends('channel_ids')
    def _compute_nbr_channel(self):
        data = self.env['discuss.channel']._read_group([
            ('livechat_channel_id', 'in', self.ids),
        ], ['livechat_channel_id'], ['__count'])
        channel_count = {livechat_channel.id: count for livechat_channel, count in data}
        for record in self:
            record.nbr_channel = channel_count.get(record.id, 0)

    # --------------------------
    # Action Methods
    # --------------------------
    def action_join(self):
        self.ensure_one()
        return self.write({'user_ids': [(4, self._uid)]})

    def action_quit(self):
        self.ensure_one()
        return self.write({'user_ids': [(3, self._uid)]})

    def action_view_rating(self):
        """ Action to display the rating relative to the channel, so all rating of the
            sessions of the current channel
            :returns : the ir.action 'action_view_rating' with the correct context
        """
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('im_livechat.rating_rating_action_livechat')
        action['context'] = {'search_default_parent_res_name': self.name}
        return action

    def action_view_chatbot_scripts(self):
        action = self.env['ir.actions.act_window']._for_xml_id('im_livechat.chatbot_script_action')
        chatbot_script_ids = self.env['im_livechat.channel.rule'].search(
            [('channel_id', 'in', self.ids)]).mapped('chatbot_script_id')
        if len(chatbot_script_ids) == 1:
            action['res_id'] = chatbot_script_ids.id
            action['view_mode'] = 'form'
            action['views'] = [(False, 'form')]
        else:
            action['domain'] = [('id', 'in', chatbot_script_ids.ids)]
        return action

    # --------------------------
    # Channel Methods
    # --------------------------
    def _get_livechat_discuss_channel_vals(self, anonymous_name, operator=None, chatbot_script=None, user_id=None, country_id=None):
        # partner to add to the discuss.channel
        operator_partner_id = operator.partner_id.id if operator else chatbot_script.operator_partner_id.id
        members_to_add = [Command.create({'partner_id': operator_partner_id, 'is_pinned': False})]
        visitor_user = False
        if user_id:
            visitor_user = self.env['res.users'].browse(user_id)
            if visitor_user and visitor_user.active and operator and visitor_user != operator:  # valid session user (not public)
                members_to_add.append(Command.create({'partner_id': visitor_user.partner_id.id}))

        if chatbot_script:
            name = chatbot_script.title
        else:
            name = ' '.join([
                visitor_user.display_name if visitor_user else anonymous_name,
                operator.livechat_username if operator.livechat_username else operator.name
            ])

        return {
            'channel_member_ids': members_to_add,
            'livechat_active': True,
            'livechat_operator_id': operator_partner_id,
            'livechat_channel_id': self.id,
            'chatbot_current_step_id': chatbot_script._get_welcome_steps()[-1].id if chatbot_script else False,
            'anonymous_name': False if user_id else anonymous_name,
            'country_id': country_id,
            'channel_type': 'livechat',
            'name': name,
        }

    def _open_livechat_discuss_channel(self, anonymous_name, previous_operator_id=None, chatbot_script=None, user_id=None, country_id=None, persisted=True, lang=None):
        """ Return a livechat session. If the session is persisted, creates a discuss.channel record with a connected operator or with Odoobot as
            an operator if a chatbot has been configured, or return false otherwise
            :param anonymous_name : the name of the anonymous person of the session
            :param previous_operator_id : partner_id.id of the previous operator that this visitor had in the past
            :param chatbot_script : chatbot script if there is one configured
            :param user_id : the id of the logged in visitor, if any
            :param country_code : the country of the anonymous person of the session
            :param persisted: whether or not the session should be persisted
            :param lang: code of the preferred lang of the visitor.
            :type anonymous_name : str
            :return : channel header
            :rtype : dict

            If this visitor already had an operator within the last 7 days (information stored with the 'im_livechat_previous_operator_pid' cookie),
            the system will first try to assign that operator if he's available (to improve user experience).
        """
        self.ensure_one()
        user_operator = False
        if chatbot_script:
            if chatbot_script.id not in self.env['im_livechat.channel.rule'].search(
                    [('channel_id', 'in', self.ids)]).mapped('chatbot_script_id').ids:
                return False
        elif previous_operator_id:
            # previous_operator_id is the partner_id of the previous operator, need to convert to user
            if previous_operator_id in self.available_operator_ids.mapped('partner_id').ids:
                user_operator = next(available_user for available_user in self.available_operator_ids if available_user.partner_id.id == previous_operator_id)
        if not user_operator and not chatbot_script:
            user_operator = self._get_random_operator(lang=lang, country_id=country_id)
        if not user_operator and not chatbot_script:
            # no one available
            return False
        discuss_channel_vals = self._get_livechat_discuss_channel_vals(anonymous_name, user_operator, chatbot_script, user_id=user_id, country_id=country_id)
        if persisted:
            # create the session, and add the link with the given channel
            discuss_channel = self.env["discuss.channel"].with_context(mail_create_nosubscribe=False).sudo().create(discuss_channel_vals)
            if user_operator:
                discuss_channel._broadcast([user_operator.partner_id.id])
            return discuss_channel.sudo()._channel_info()[0]
        else:
            operator_partner_id = user_operator.partner_id if user_operator else chatbot_script.operator_partner_id
            display_name = operator_partner_id.user_livechat_username or operator_partner_id.display_name
            return {
                'name': discuss_channel_vals['name'],
                'chatbot_current_step_id': discuss_channel_vals['chatbot_current_step_id'],
                'state': 'open',
                'operator_pid': (operator_partner_id.id, display_name.replace(',', '')),
                'chatbot_script_id': chatbot_script.id if chatbot_script else None
            }

    def _get_less_active_operator(self, active_channels, operators):
        """ Get the operator with the less active conversations.
        :param active_channels: list of active livechats (with at least
            one message within the last 30 minutes)
        :param operators: list of operators to choose from
        """
        if not operators:
            return False
        active_channels = [active_channel for active_channel in active_channels if active_channel['livechat_operator_id'] in operators.mapped('partner_id').ids]
        active_operators = [active_channel['livechat_operator_id'] for active_channel in active_channels]
        inactive_operators = [operator for operator in operators if operator.partner_id.id not in active_operators]
        if inactive_operators:
            return random.choice(inactive_operators)

        # Get the less active operator using the active_channels first element's count (since they are sorted 'ascending')
        lowest_number_of_conversations = active_channels[0]['count']
        less_active_operator = random.choice([
            active_channel['livechat_operator_id'] for active_channel in active_channels
            if active_channel['count'] == lowest_number_of_conversations])

        # convert the selected 'partner_id' to its corresponding res.users
        return next(operator for operator in operators if operator.partner_id.id == less_active_operator)

    def _get_random_operator(self, lang=None, country_id=None):
        """ Return a random operator from the available users of the channel that have the lowest number of active livechats.
        A livechat is considered 'active' if it has at least one message within the 30 minutes.
        This method will try to match the given lang and country_id.

        (Some annoying conversions have to be made on the fly because this model holds 'res.users' as available operators
        and the discuss_channel model stores the partner_id of the randomly selected operator)

        :param lang: code of the preferred lang of the visitor.
        :param country_id: id of the country of the visitor.
        :return : user
        :rtype : res.users
        """
        if not self.available_operator_ids:
            return False

        self.env.cr.execute("""SELECT COUNT(DISTINCT c.id), c.livechat_operator_id
            FROM discuss_channel c
            LEFT OUTER JOIN mail_message m ON c.id = m.res_id AND m.model = 'discuss.channel'
            WHERE c.channel_type = 'livechat'
            AND c.livechat_operator_id in %s
            AND m.create_date > ((now() at time zone 'UTC') - interval '30 minutes')
            GROUP BY c.livechat_operator_id
            ORDER BY COUNT(DISTINCT c.id) asc""", (tuple(self.available_operator_ids.mapped('partner_id').ids),))
        active_channels = self.env.cr.dictfetchall()
        operator = None
        # Try to match an operator with the same lang as the visitor
        if lang:
            same_lang_operator_ids = self.available_operator_ids.filtered(lambda operator: operator.partner_id.lang == lang)
            if same_lang_operator_ids:
                operator = self._get_less_active_operator(active_channels, same_lang_operator_ids)
        # Try to match an operator with the same country as the visitor
        if country_id and not operator:
            same_country_operator_ids = self.available_operator_ids.filtered(lambda operator: operator.partner_id.country_id.id == country_id)
            if same_country_operator_ids:
                operator = self._get_less_active_operator(active_channels, same_country_operator_ids)
        # Try to get a random operator, regardless of the lang or the country
        if not operator:
            operator = self._get_less_active_operator(active_channels, self.available_operator_ids)
        return operator

    def _get_channel_infos(self):
        self.ensure_one()

        return {
            'header_background_color': self.header_background_color,
            'button_background_color': self.button_background_color,
            'title_color': self.title_color,
            'button_text_color': self.button_text_color,
            'button_text': self.button_text,
            'input_placeholder': self.input_placeholder,
            'default_message': self.default_message,
            "channel_name": self.name,
            "channel_id": self.id,
        }

    def get_livechat_info(self, username=None):
        self.ensure_one()

        if username is None:
            username = _('Visitor')
        info = {}
        info['available'] = self.chatbot_script_count or len(self.available_operator_ids) > 0
        info['server_url'] = self.get_base_url()
        if info['available']:
            info['options'] = self._get_channel_infos()
            info['options']['current_partner_id'] = (
                self.env.user.partner_id.id if not self.env.user._is_public() else None
            )
            info['options']["default_username"] = username
        return info


class ImLivechatChannelRule(models.Model):
    """ Channel Rules
        Rules defining access to the channel (countries, and url matching). It also provide the 'auto pop'
        option to open automatically the conversation.
    """

    _name = 'im_livechat.channel.rule'
    _description = 'Livechat Channel Rules'
    _order = 'sequence asc'

    regex_url = fields.Char('URL Regex',
        help="Regular expression specifying the web pages this rule will be applied on.")
    action = fields.Selection([
        ('display_button', 'Show'),
        ('display_button_and_text', 'Show with notification'),
        ('auto_popup', 'Open automatically'),
        ('hide_button', 'Hide')], string='Live Chat Button', required=True, default='display_button',
        help="* 'Show' displays the chat button on the pages.\n"\
             "* 'Show with notification' is 'Show' in addition to a floating text just next to the button.\n"\
             "* 'Open automatically' displays the button and automatically opens the conversation pane.\n"\
             "* 'Hide' hides the chat button on the pages.\n")
    auto_popup_timer = fields.Integer('Open automatically timer', default=0,
        help="Delay (in seconds) to automatically open the conversation window. Note: the selected action must be 'Open automatically' otherwise this parameter will not be taken into account.")
    chatbot_script_id = fields.Many2one('chatbot.script', string='Chatbot')
    chatbot_only_if_no_operator = fields.Boolean(
        string='Enabled only if no operator', help='Enable the bot only if there is no operator available')
    channel_id = fields.Many2one('im_livechat.channel', 'Channel',
        help="The channel of the rule")
    country_ids = fields.Many2many('res.country', 'im_livechat_channel_country_rel', 'channel_id', 'country_id', 'Country',
        help="The rule will only be applied for these countries. Example: if you select 'Belgium' and 'United States' and that you set the action to 'Hide', the chat button will be hidden on the specified URL from the visitors located in these 2 countries. This feature requires GeoIP installed on your server.")
    sequence = fields.Integer('Matching order', default=10,
        help="Given the order to find a matching rule. If 2 rules are matching for the given url/country, the one with the lowest sequence will be chosen.")

    def match_rule(self, channel_id, url, country_id=False):
        """ determine if a rule of the given channel matches with the given url
            :param channel_id : the identifier of the channel_id
            :param url : the url to match with a rule
            :param country_id : the identifier of the country
            :returns the rule that matches the given condition. False otherwise.
            :rtype : im_livechat.channel.rule
        """
        def _match(rules):
            for rule in rules:
                # url might not be set because it comes from referer, in that
                # case match the first rule with no regex_url
                if re.search(rule.regex_url or '', url or ''):
                    return rule
            return False
        # first, search the country specific rules (the first match is returned)
        if country_id: # don't include the country in the research if geoIP is not installed
            domain = [('country_ids', 'in', [country_id]), ('channel_id', '=', channel_id)]
            rule = _match(self.search(domain))
            if rule:
                return rule
        # second, fallback on the rules without country
        domain = [('country_ids', '=', False), ('channel_id', '=', channel_id)]
        return _match(self.search(domain))
