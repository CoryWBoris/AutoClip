import Live
from ableton.v2.control_surface import ControlSurface
from functools import partial
from collections import defaultdict
from ableton.v2.base import liveobj_valid, liveobj_changed

def defer_rename_track(track, clip_slot, i):
    if track.name in ['Audio', 'Midi']:
        track.name = clip_slot.clip.name

def defer_rename_clip(track, clip_slot, i):
    # Use liveobj_valid to check if clip_slot is a valid Live API object
    if liveobj_valid(clip_slot) and clip_slot.has_clip and track.name != 'DefaultBounce':
        clip = clip_slot.clip
        clip.name = f"{clip_slot.canonical_parent.name} {list(clip_slot.canonical_parent.clip_slots).index(clip_slot) + 1}"

def set_clip_names(track, song):
    if track not in song.tracks or not hasattr(track, 'mixer_device') or track.is_foldable or hasattr(track, 'return_track') or hasattr(track, 'master_track') or track.name == 'DefaultBounce':
        return
    for i, clip_slot in enumerate(track.clip_slots, start=1):
        if clip_slot is not None and clip_slot.has_clip and track.name != 'DefaultBounce':
            defer_rename_track(track, clip_slot, i)
            defer_rename_clip(track, clip_slot, i)
    for i, clip in enumerate(track.arrangement_clips, start=1):
        if track.name in ['Audio', 'Midi']:
            track.name = clip.name
        if len(track.arrangement_clips) == 1:
            clip.name = f"{track.name}"
        else:
            clip.name = f"{track.name} {i}"

def init_clip_names_recursive(track, song):
    if not track.is_foldable or track.is_grouped:
        set_clip_names(track, song)
    if hasattr(track, 'is_foldable') and track.is_foldable:
        for sub_track in get_nested_tracks(track):
            init_clip_names_recursive(sub_track, song)

def get_all_tracks(doc):
    return [track for track in doc.tracks if hasattr(track, 'is_foldable') and track.is_foldable]

def get_nested_tracks(group_track):
    return [track for track in group_track.canonical_parent.tracks if hasattr(track, 'is_grouped') and track.is_grouped and track.group_track == group_track]

class AutoClip(ControlSurface):
    def __init__(self, c_instance):
        super().__init__(c_instance)
        self._clip_slots_listeners = {}
        self.song.add_tracks_listener(self.on_tracks_changed)
        self.song.add_tracks_listener(self.on_tracks_added)
        self._clip_slot_listeners = defaultdict(lambda: None)
        self._track_listeners = defaultdict(lambda: None)
        self._name_listeners = defaultdict(lambda: None)
        app = Live.Application.get_application()
        self.doc = app.get_document()
        self.num_tracks = len(self.doc.tracks)
        self.processed_tracks = set(self.doc.tracks)  # Define processed_tracks here
        for track in self.song.tracks:
            self.add_clip_slot_listeners(track)
            self.on_tracks_changed()
            set_clip_names(track, self.song)
        self.add_clip_listeners()
        self._clip_slot_listeners = defaultdict(lambda: None)
        self.add_track_listeners(get_all_tracks(self.doc))
        self.doc.add_tracks_listener(self.tracks_added_listener)
        self.doc.add_tracks_listener(self.tracks_removed_listener)

    def add_clip_listeners(self):
        for track in self.song.tracks:
            for clip_slot in track.clip_slots:
                if clip_slot is not None and clip_slot.has_clip:
                    clip_slot.add_has_clip_listener(self.clip_slot_changed_listener(clip_slot))

    def on_tracks_added(self):
        for track in self.song.tracks:
            if track not in self._name_listeners and track.name != 'DefaultBounce':
                self.add_track_listeners([track])

    def disconnect(self):
        self.doc.remove_tracks_listener(self.tracks_added_listener)
        self.remove_track_listeners(get_all_tracks(self.doc))
        super().disconnect()

    def init_clip_names(self):
        for track in get_all_tracks(self.doc):
            init_clip_names_recursive(track, self.song)

    def on_tracks_changed(self):
        print('Tracks changed is reached')
        for track in self.song.tracks:
            if track.name != 'DefaultBounce':
                self.tracks_added_listener()
                self.add_track_listeners([track])
                self.add_clip_slot_listeners(track)
                self.add_arrangement_clips_listener(track)
                if track.is_grouped:
                    self.add_group_track_listeners(track)
                for i, clip_slot in enumerate(track.clip_slots, start=1):
                    self.schedule_message(0, partial(defer_rename_clip, track, clip_slot, i))

    def add_group_track_listeners(self, track):
        name_listener = partial(self.track_name_changed_listener, track)
        self._name_listeners[track] = name_listener
        track.add_name_listener(name_listener)
        track.add_clip_slots_listener(lambda: self.track_clip_slots_changed_listener(track))
        self.add_clip_slot_listeners(track)

    def add_track_listeners(self, tracks):
        print('Add track listeners is reached')
        for track in tracks:
            if track.is_grouped:
                self.add_group_track_listeners(track)
                self.add_arrangement_clips_listener(track)
            elif not track.is_foldable:
                name_listener = partial(self.track_name_changed_listener, track)
                self._name_listeners[track] = name_listener
                track.add_name_listener(name_listener)
                self.add_clip_slot_listeners(track)
                self.add_arrangement_clips_listener(track)
            if track not in self._clip_slots_listeners:
                self._clip_slots_listeners[track] = self.on_clip_slots_changed
                track.add_clip_slots_listener(self._clip_slots_listeners[track])

    def on_clip_slots_changed(self):
        for track in self.song.tracks:
            if track.name != 'DefaultBounce':
                for i, clip_slot in enumerate(track.clip_slots, start=1):
                    if clip_slot is not None and clip_slot.has_clip and clip_slot not in self._clip_slot_listeners:
                        self.add_clip_slot_listeners(track)
                        self.schedule_message(0, partial(defer_rename_clip, track, clip_slot, i))

    def add_clip_slot_listeners(self, track):
        for clip_slot in track.clip_slots:
            if clip_slot not in self._clip_slot_listeners:
                clip_slot_listener = partial(self.clip_slot_changed_listener, clip_slot)
                self._clip_slot_listeners[clip_slot] = clip_slot_listener
                clip_slot.add_has_clip_listener(clip_slot_listener)
                if clip_slot.has_clip:
                    self.clip_slot_changed_listener(clip_slot)

    def remove_track_listeners(self, tracks):
        if tracks is None:
            return
        for track in tracks:
            if not track.is_foldable and not track.is_grouped:
                name_listener = self._name_listeners[track]
                track.remove_color_listener(color_listener)
                for clip_slot in track.clip_slots:
                    clip_slot_listener = self._clip_slot_listeners.get(clip_slot)
                    if clip_slot_listener is not None:
                        clip_slot.remove_has_clip_listener(clip_slot_listener)

    def track_name_changed_listener(self, track):
        if track.name == 'DefaultBounce' or track.name in ['Audio', 'Midi']:  # Assuming 'Audio' and 'Midi' are the default names
            pass
        else:
            self.schedule_message(0, lambda: self.deferred_track_name_changed_listener(track))

    def deferred_track_name_changed_listener(self, track):
        set_clip_names(track, self.song)

    def clip_slot_changed_listener(self, clip_slot):
        if clip_slot.canonical_parent.name == 'DefaultBounce':
            return
        self.schedule_message(0, partial(self.deferred_clip_slot_changed_listener, clip_slot))

    def deferred_clip_slot_changed_listener(self, clip_slot):
        if clip_slot.has_clip:
            clip = clip_slot.clip
            track = clip_slot.canonical_parent
            if track.name in ['Audio', 'Midi']:
                track.name = clip.name
            clip.name = f"{track.name} {list(track.clip_slots).index(clip_slot) + 1}"
            self.schedule_message(0, partial(set_clip_names, track, self.song))

    def track_clip_slots_changed_listener(self, track):
        if track.name == 'DefaultBounce':
            return
        for clip_slot in track.clip_slots:
            if not clip_slot in self._clip_slot_listeners:
                clip_slot_listener = partial(self.clip_slot_changed_listener, clip_slot)
                self._clip_slot_listeners[clip_slot] = clip_slot_listener
                clip_slot.add_has_clip_listener(clip_slot_listener)
                if clip_slot.has_clip:
                    self.clip_slot_changed_listener(clip_slot)
                clip_slot.add_clip_slot_listener(clip_slot_listener)

    def tracks_added_listener(self):
        current_tracks = set(self.doc.tracks)
        new_tracks = current_tracks - self.processed_tracks
        for track in new_tracks:
            if track.name != 'DefaultBounce':
                self._track_listeners[track] = self.on_tracks_changed 
                self.add_track_listeners([track])
                self.add_clip_slot_listeners(track)
                self.add_arrangement_clips_listener(track)
                if track.is_grouped:
                    self.add_group_track_listeners(track)
                self.schedule_message(0, lambda track=track: set_clip_names(track, self.song))
        self.processed_tracks = current_tracks

    def arrangement_clip_tracks_changed_listener(self, track):
        if track.name == 'DefaultBounce':
            return
        self.schedule_message(0, lambda: self.deferred_arrangement_clip_tracks_changed_listener(track))

    def deferred_arrangement_clip_tracks_changed_listener(self, track):
        set_clip_names(track, self.song)
        grouped_tracks = get_nested_tracks(track.group_track) if track.is_grouped else []
        for grouped_track in grouped_tracks:
            set_clip_names(grouped_track, self.song)

    def add_arrangement_clips_listener(self, track):
        if hasattr(track, 'mixer_device') and not (track.is_foldable or hasattr(track, 'return_track') or hasattr(track, 'master_track')):
            track.add_arrangement_clips_listener(partial(self.arrangement_clip_tracks_changed_listener, track))

    def tracks_removed_listener(self):
        current_tracks = set(self.doc.tracks)
        removed_tracks = self.processed_tracks - current_tracks
        for track in removed_tracks:
            if track and track.canonical_parent:
                self.remove_track_listeners([track])
                self.remove_clip_slot_listeners(track)  # Add this line
        self.processed_tracks = current_tracks
    
    def remove_clip_slot_listeners(self, track):
        for clip_slot in track.clip_slots:
            clip_slot_listener = self._clip_slot_listeners.get(clip_slot)
            if clip_slot_listener is not None and clip_slot.has_clip_has_listener(clip_slot_listener):
                clip_slot.remove_has_clip_listener(clip_slot_listener)
                del self._clip_slot_listeners[clip_slot]  # Remove the listener from the dictionary
    
    def disconnect(self):
        self.song.remove_tracks_listener(self.on_tracks_changed)
        self.song.remove_tracks_listener(self.on_tracks_added)
        self.doc.remove_tracks_listener(self.tracks_added_listener)
        self.doc.remove_tracks_listener(self.tracks_removed_listener)
        super().disconnect()
