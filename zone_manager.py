import re
from zone_node import ZoneNode

class ZoneManager:
    """
    Manages text zones using a circular linked list structure.
    Demonstrates efficiency over traditional monolithic text processing.
    """
    def __init__(self):
        self.head = None
        self.zones = []
        self.total_tokens_processed = 0
        self.total_passes = 0
        
    def split_into_zones(self, text):

        # ---- Reset state ----
        self.zones = []
        self.head = None

        """
        Split text into logical zones
        Sentences are grouped into meaningful chunks so that
        node count scales with structure, not raw sentence count.
        """

        # ---- Sentence split ----
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s for s in sentences if s.strip()]  # safety clean

        num_sentences = len(sentences)

        # ---- Adaptive zone sizing ----
        if num_sentences <= 2:
            zone_size = num_sentences        # 1 zone
        elif num_sentences <= 5:
            zone_size = 2                    # small paragraph
        else:
            zone_size = 3                    # large paragraph

        zones_text = []

        # ---- Group sentences into zones ----
        for i in range(0, num_sentences, zone_size):
            zone_text = " ".join(sentences[i:i + zone_size])
            if zone_text.strip():
                zones_text.append(zone_text)

        # ---- Create zone nodes ----
        prev_node = None

        for i, zone_text in enumerate(zones_text):
            if i == 0:
                zone_type = "intro"
            elif i == len(zones_text) - 1:
                zone_type = "conclusion"
            else:
                zone_type = "body"

            node = ZoneNode(i + 1, zone_text, zone_type)
            self.zones.append(node)

            if prev_node:
                prev_node.next = node
            else:
                self.head = node

            prev_node = node

        # ---- Make circular ----
        if prev_node and self.head:
            prev_node.next = self.head

        return len(self.zones)

    
    def get_all_zones(self):
        """Return all zones as a list"""
        return self.zones
    
    def get_combined_text(self):
        """Reconstruct text from all zones"""
        return ' '.join(zone.text for zone in self.zones)
    
    def get_metrics(self):
        """Get efficiency metrics"""
        total_changes = sum(zone.changes_made for zone in self.zones)
        total_passes = sum(zone.refinement_passes for zone in self.zones)
        total_tokens = sum(zone.count_tokens() for zone in self.zones)
        
        # Calculate tokens that would be processed in traditional approach
        # (re-process entire text each time)
        traditional_tokens = total_tokens * max(1, max(z.refinement_passes for z in self.zones) if self.zones else 0)
        
        # Calculate actual tokens processed (only zones that needed work)
        actual_tokens = sum(zone.count_tokens() * zone.refinement_passes for zone in self.zones)
        
        efficiency_gain = 0
        if traditional_tokens > 0:
            efficiency_gain = ((traditional_tokens - actual_tokens) / traditional_tokens) * 100
        
        return {
            'zones': len(self.zones),
            'total_changes': total_changes,
            'total_passes': total_passes,
            'tokens_traditional': traditional_tokens,
            'tokens_actual': actual_tokens,
            'efficiency_gain': efficiency_gain
        }
    
    def get_zone_details(self):
        """Get per-zone refinement details"""
        details = []
        for zone in self.zones:
            details.append({
                'zone_id': zone.zone_id,
                'type': zone.zone_type,
                'passes': zone.refinement_passes,
                'changes': zone.changes_made,
                'tokens': zone.count_tokens(),
                'refined': zone.is_refined
            })
        return details