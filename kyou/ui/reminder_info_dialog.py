from typing import Any

from gi.repository import Adw, Gtk

from kyou.config import PREFIX
from kyou.models import Item


@Gtk.Template(resource_path=f"{PREFIX}/reminder-info-dialog.ui")
class ReminderInfoDialog(Adw.Dialog):
    __gtype_name__ = "ReminderInfoDialog"
    
    info_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, item: Item, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.set_title(item.title)
        
        info_text = f"--- {item.title!r} ---\n"
        info_text += f"id: {item.id}\n"
        info_text += f"kind: {item.kind.name}\n"
        info_text += f"start: {item.start}\n"
        info_text += f"end: {item.end}\n"
        info_text += f"due_date: {item.due_date}\n"
        info_text += f"all_day: {item.all_day}\n"
        info_text += f"completed: {item.completed}\n"
        info_text += f"completed_date: {item.completed_date}\n"
        info_text += f"priority: {item.priority.name}\n"
        info_text += f"flagged: {item.flagged}\n"
        info_text += f"notes: {item.notes!r}\n"
        info_text += f"location: {item.location!r}\n"
        info_text += f"url: {item.url!r}\n"
        info_text += f"list_name: {item.list_name!r}\n"
        info_text += f"list_color: {item.list_color!r}\n"
        info_text += f"created_date: {item.created_date}\n"
        info_text += f"last_modified_date: {item.last_modified_date}\n"
        info_text += f"has_recurrence_rules: {item.has_recurrence_rules}\n"
        
        for rule in item.recurrence_rules:
            info_text += f"  recurrence: freq={rule.frequency} interval={rule.interval} end_date={rule.end_date} occurrence_count={rule.occurrence_count}\n"
        for alarm in item.alarms:
            info_text += f"  alarm: trigger_date={alarm.trigger_date} relative_offset={alarm.relative_offset}\n"
            
        self.info_label.set_label(info_text)

    @Gtk.Template.Callback()
    def on_close_clicked(self, *_args: Any) -> None:
        self.close()
