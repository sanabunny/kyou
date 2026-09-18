from gettext import gettext as _
from typing import Any

from gi.repository import Adw, Gdk, Gtk

from kyou.config import PREFIX
from kyou.models import Item, ItemKind, Priority


def _get_priority_label(priority: Priority) -> str:
    match priority:
        case Priority.HIGH:
            return _("⚡ High")
        case Priority.MEDIUM:
            return _("● Medium")
        case Priority.LOW:
            return _("▾ Low")
        case _:
            return "—"


def _fmt_dt(dt: Any) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%a, %-d %b %Y  %H:%M")


def _fmt_offset(td: Any) -> str:
    if td is None:
        return "—"
    total = int(td.total_seconds())
    hours, rem = divmod(abs(total), 3600)
    mins = rem // 60
    if hours and mins:
        return _("{}h {}m before").format(hours, mins)
    if hours:
        return _("{}h before").format(hours)
    return _("{}m before").format(mins)


def _make_group(title: str, rows: list[tuple[str, str]]) -> Adw.PreferencesGroup:
    group = Adw.PreferencesGroup(title=title)
    for label, value in rows:
        row = Adw.ActionRow(title=label, subtitle=value or "—")
        if label == "URL" and value and (value.startswith("http://") or value.startswith("https://")):
            row.set_activatable(True)
            row.set_cursor_from_name("pointer")
            row.connect("activated", lambda _r, u=value: Gtk.show_uri(None, u, Gdk.CURRENT_TIME))
        else:
            row.set_activatable(False)
            row.set_selectable(False)
        group.add(row)
    return group


@Gtk.Template(resource_path=f"{PREFIX}/reminder-info-dialog.ui")
class ReminderInfoDialog(Adw.Dialog):
    __gtype_name__ = "ReminderInfoDialog"

    rows_box: Gtk.Box = Gtk.Template.Child()

    def __init__(self, item: Item, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title(item.title)

        if item.kind == ItemKind.EVENT:
            details: list[tuple[str, str]] = [
                (_("Calendar"), item.list_name or "—"),
                (_("Start"), _fmt_dt(item.start)),
                (_("End"), _fmt_dt(item.end)),
            ]
            if item.location:
                details.append((_("Location"), item.location))
        else:
            details: list[tuple[str, str]] = [
                (_("List"), item.list_name or "—"),
                (_("Priority"), _get_priority_label(item.priority)),
                (_("Due"), _fmt_dt(item.due_date)),
                (_("Status"), _("✓ Completed") if item.completed else _("Pending")),
            ]
            if item.completed_date:
                details.append((_("Completed on"), _fmt_dt(item.completed_date)))
            if item.flagged:
                details.append((_("Flagged"), _("Yes ⚑")))
            if item.location:
                details.append((_("Location"), item.location))

        self.rows_box.append(_make_group(_("Details"), details))

        if item.notes:
            notes_group = Adw.PreferencesGroup(title=_("Notes"))
            label = Gtk.Label(
                label=item.notes,
                wrap=True,
                xalign=0,
                selectable=False,
                margin_top=8,
                margin_bottom=8,
                margin_start=12,
                margin_end=12,
            )
            label.add_css_class("dim-label")
            notes_group.add(label)
            self.rows_box.append(notes_group)

        if item.alarms:
            alarm_rows = [
                (
                    _("Alarm {}").format(i + 1),
                    _fmt_dt(a.trigger_date) if a.trigger_date else _fmt_offset(a.relative_offset),
                )
                for i, a in enumerate(item.alarms)
            ]
            self.rows_box.append(_make_group(_("Reminders"), alarm_rows))

        if item.recurrence_rules:
            rec_rows = [
                (
                    _("Repeat {}").format(i + 1),
                    f"{(r.frequency or 'unknown').capitalize()}"
                    + (f", every {r.interval}" if r.interval and r.interval > 1 else "")
                    + (f", until {_fmt_dt(r.end_date)}" if r.end_date else "")
                    + (f", {r.occurrence_count}×" if r.occurrence_count else ""),
                )
                for i, r in enumerate(item.recurrence_rules)
            ]
            self.rows_box.append(_make_group(_("Recurrence"), rec_rows))

        meta: list[tuple[str, str]] = [
            (_("Created"), _fmt_dt(item.created_date)),
            (_("Modified"), _fmt_dt(item.last_modified_date)),
        ]
        if item.url:
            meta.append((_("URL"), item.url))
        self.rows_box.append(_make_group(_("Info"), meta))

    @Gtk.Template.Callback()
    def on_close_clicked(self, *_args: Any) -> None:
        self.close()
