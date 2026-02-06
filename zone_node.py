class ZoneNode:
    """
    Represents a text zone (segment) in the refinement system.
    Each zone tracks its own refinement state and metrics.
    """
    def __init__(self, zone_id, text, zone_type="body"):
        self.zone_id = zone_id
        self.text = text
        self.zone_type = zone_type  # "intro", "body", "conclusion"
        self.original_text = text
        self.refinement_passes = 0
        self.changes_made = 0
        self.is_refined = False
        self.next = None
        self.tokens_processed = 0
        
    def mark_change(self):
        """Track that a change was made in this zone"""
        self.changes_made += 1
        
    def increment_pass(self):
        """Track refinement pass"""
        self.refinement_passes += 1
        
    def count_tokens(self):
        """Simple token count (words)"""
        return len(self.text.split())
    
    def __str__(self):
        return f"Zone {self.zone_id} ({self.zone_type}): {len(self.text)} chars, {self.refinement_passes} passes"