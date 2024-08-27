/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _lt } from "@web/core/l10n/translation";

export class ConfirmPopup extends AbstractAwaitablePopup {
    static template = "point_of_sale.ConfirmPopup";
    static defaultProps = {
        confirmText: _lt("Ok"),
        cancelText: _lt("Cancel"),
        title: _lt("Confirm?"),
        body: "",
    };
}
