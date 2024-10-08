/** @odoo-module */

import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ListRenderer } from '@web/views/list/list_renderer';

const { useEffect } = owl;

export class SubtaskListRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
        useEffect(
            () => this.focusName(this.props.list.editedRecord),
            () => [this.props.list.editedRecord]
        );
    }

    focusName(editedRecord) {
        if (editedRecord?.isNew && !editedRecord.isDirty) {
            const col = this.state.columns.find((c) => c.name === "name");
            this.focusCell(col);
        }
    }

    async onDeleteRecord(record) {
        this.dialog.add(ConfirmationDialog, {
            body: this.env._t("Are you sure you want to delete this record?"),
            confirm: () => super.onDeleteRecord(record),
            cancel: () => {},
        });
    }
}
