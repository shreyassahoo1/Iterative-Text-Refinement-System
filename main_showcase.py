from zone_manager import ZoneManager
from smart_refiners import predict_zone_action, apply_zone_action, polish_zone

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_progress_bar(progress, total):
    """Print progress bar"""
    percentage = int((progress / total) * 100) if total > 0 else 100
    filled = int((progress / total) * 40) if total > 0 else 40
    bar = "█" * filled + "░" * (40 - filled)
    return f"[{bar}] {percentage}%"

def visualize_zone_status(zones):
    """Show visual status of each zone"""
    print("\n  ZONE STATUS:")
    for zone in zones:
        status = "✓" if zone.is_refined else "⚡"
        heat = "🔥" * min(zone.changes_made, 5)
        print(f"    Zone {zone.zone_id} ({zone.zone_type:>10}): {status} {zone.refinement_passes} passes  {heat}")

def run_refinement(text):
    """
    Backend entry-point for UI.
    Executes the refinement pipeline and returns logs + final output.
    """
    logs = []

    # Capture print output
    def capture_print(*args):
        logs.append(" ".join(str(a) for a in args))

    import builtins
    original_print = builtins.print
    builtins.print = capture_print

    try:
        from zone_manager import ZoneManager
        from smart_refiners import predict_zone_action, apply_zone_action, polish_zone

        manager = ZoneManager()
        num_zones = manager.split_into_zones(text)

        MAX_CYCLES = 10
        zones_needing_work = list(manager.get_all_zones())
        cycle = 0

        while zones_needing_work and cycle < MAX_CYCLES:
            cycle += 1

            for zone in zones_needing_work[:]:

                # 🔴 NEW: log traversal (node visit)
                logs.append({
                    "event": "visit",
                    "zone": zone.zone_id,
                    "refined": zone.is_refined
                })

                if zone.is_refined:
                    zones_needing_work.remove(zone)
                    continue

                action = predict_zone_action(zone)

                if action == "no change":
                    if zone.text.strip().endswith(('.', '!', '?')):
                        zone.is_refined = True
                        zones_needing_work.remove(zone)

                        # 🟢 NEW: log refinement completion
                        logs.append({
                            "event": "refined",
                            "zone": zone.zone_id
                        })

                        continue
                    else:
                        zone.text = zone.text.strip() + "."
                        zone.mark_change()
                        zone.increment_pass()
                        continue

                zone.increment_pass()
                apply_zone_action(zone, action)
                polish_zone(zone)

                # 🟢 NEW: if zone got refined after changes
                if zone.is_refined:
                    logs.append({
                        "event": "refined",
                        "zone": zone.zone_id
                    })

        final_text = manager.get_combined_text()
        metrics = manager.get_metrics()

        return logs, final_text, metrics

    finally:
        builtins.print = original_print

def main():
    # ---- USER INPUT ----
    print("\n🚀 ADVANCED TEXT REFINEMENT SYSTEM")
    print("   Using Circular Linked List with Zonal Processing\n")
    
    text = input("Enter text to refine:\n> ")
    
    if not text.strip():
        print("No text provided!")
        return
    
    print_header("INITIALIZATION")
    
    # Initialize zone manager
    manager = ZoneManager()
    num_zones = manager.split_into_zones(text)
    
    print(f"\n  ✓ Text split into {num_zones} zones")
    print(f"  ✓ Circular linked list created")
    print(f"  ✓ Original text: {len(text)} characters, {len(text.split())} words")
    
    # Show zone breakdown
    print("\n  ZONE BREAKDOWN:")
    for zone in manager.get_all_zones():
        print(f"    Zone {zone.zone_id} ({zone.zone_type}): {len(zone.text)} chars")
    
    print_header("REFINEMENT PROCESS")
    print("\n  Strategy: Process only zones that need refinement")
    print("  Advantage: Skip already-refined zones (unlike traditional re-processing)\n")
    
    MAX_CYCLES = 10
    zones_needing_work = list(manager.get_all_zones())
    cycle = 0
    
    while zones_needing_work and cycle < MAX_CYCLES:
        cycle += 1
        print(f"\n  ─── Cycle {cycle} ─────")
        
        zones_changed = []
        
        for zone in zones_needing_work[:]:
            # Skip if already refined
            if zone.is_refined:
                zones_needing_work.remove(zone)
                continue

            # PREDICT
            action = predict_zone_action(zone)

            # If nothing to do, check if really complete
            if action == "no change":
                # Check if text ends with punctuation
                if zone.text.strip().endswith(('.', '!', '?')):
                    zone.is_refined = True
                    zones_needing_work.remove(zone)
                    continue
                else:
                    # Text doesn't end with punctuation - force add it
                    print(f"    Zone {zone.zone_id}: add period (forced)  → {zone.text.strip()[:60]}...")
                    zone.text = zone.text.strip() + "."
                    zone.mark_change()
                    zone.increment_pass()
                    zones_changed.append(zone.zone_id)
                    
                    # Now check if complete
                    if zone.text.strip().endswith(('.', '!', '?')):
                        zone.is_refined = True
                    continue

            # APPLY refinement
            zone.increment_pass()
            changed = apply_zone_action(zone, action)

            # POLISH
            polish_changed = polish_zone(zone)

            if changed or polish_changed:
                zones_changed.append(zone.zone_id)
                print(f"    Zone {zone.zone_id}: {action:20} → {zone.text[:60]}...")
            
            
        
        # Show progress
        progress = print_progress_bar(num_zones - len(zones_needing_work), num_zones)
        print(f"\n  Progress: {progress} ({num_zones - len(zones_needing_work)}/{num_zones} zones refined)")
        
        if not zones_needing_work or all(zone.is_refined for zone in manager.get_all_zones()):
            print(f"\n  ✓ All zones refined! Stopping early at cycle {cycle}")
            break
    
    print_header("RESULTS")
    
    # Show zone details
    visualize_zone_status(manager.get_all_zones())
    
    # Get metrics
    metrics = manager.get_metrics()
    
    print("\n  EFFICIENCY METRICS:")
    print(f"    Traditional Approach: {metrics['tokens_traditional']:,} tokens processed")
    print(f"    Zonal Approach:       {metrics['tokens_actual']:,} tokens processed")
    print(f"    Efficiency Gain:      {metrics['efficiency_gain']:.1f}%")
    print(f"    Total Changes:        {metrics['total_changes']}")
    
    print_header("COMPARISON: TRADITIONAL vs ZONAL")
    
    print("\n  Traditional LLM Approach:")
    print("    ❌ Re-reads entire text every iteration")
    print("    ❌ Processes already-correct sections repeatedly")
    print(f"    ❌ Would process: {metrics['tokens_traditional']:,} tokens")
    
    print("\n  Our Zonal Linked List Approach:")
    print("    ✓ Processes only zones needing refinement")
    print("    ✓ Skips already-refined sections")
    print(f"    ✓ Actually processed: {metrics['tokens_actual']:,} tokens")
    print(f"    ✓ Saved: {metrics['tokens_traditional'] - metrics['tokens_actual']:,} token operations")
    
    print_header("FINAL OUTPUT")
    
    final_text = manager.get_combined_text()
    print(f"\n{final_text}\n")
    
    print(f"  Original: {len(text)} characters")
    print(f"  Refined:  {len(final_text)} characters")
    print(f"  Cycles:   {cycle}/{MAX_CYCLES}")

if __name__ == "__main__":
    main()