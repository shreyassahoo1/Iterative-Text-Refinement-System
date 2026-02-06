import tkinter as tk
from tkinter import scrolledtext
from main_showcase import run_refinement
from tkinter import filedialog, messagebox


# ------------------ THEME ------------------
BG_MAIN = "#121212"
BG_PANEL = "#1E1E1E"
BG_TEXT = "#1B1B1B"
FG_TEXT = "#EAEAEA"
ACCENT = "#E53935"
BTN_BG = "#2A2A2A"
BTN_HOVER = "#3A3A3A"
FONT_MAIN = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI", 12, "bold")
FONT_MONO = ("Consolas", 10)

# ------------------ LOGIC ------------------
def draw_circular_list(canvas, zones, active_zone=None, refined_zones=None):
    canvas.delete("all")

    if refined_zones is None:
        refined_zones = set()

    # ---- Canvas sizing ----
    width = canvas.winfo_width()
    if width < 600:
        width = 600

    node_radius = 28
    spacing = width // (zones + 1)
    center_y = 70

    forward_arrow_offset = 18   # arrows just below nodes
    back_arrow_offset = 42      # separate lane for circular arrow

    node_positions = []

    # ---- Draw ALL nodes ----
    for i in range(zones):
        x = spacing * (i + 1)
        y = center_y

        if i + 1 == active_zone:
            color = "#FBC02D"      # Active
        elif i + 1 in refined_zones:
            color = "#2ECC71"      # Refined
        else:
            color = "#555555"      # Unvisited

        canvas.create_oval(
            x - node_radius, y - node_radius,
            x + node_radius, y + node_radius,
            fill=color,
            outline="#888888",
            width=2
        )

        canvas.create_text(
            x, y,
            text=f"N{i+1}",
            fill="black",
            font=("Segoe UI", 10, "bold")
        )

        node_positions.append((x, y))

    # ---- Draw forward arrows (N1 -> N2 -> ... -> Nn) ----
    for i in range(zones - 1):
        x1, y1 = node_positions[i]
        x2, y2 = node_positions[i + 1]

        canvas.create_line(
            x1 + node_radius, y1 + forward_arrow_offset,
            x2 - node_radius, y2 + forward_arrow_offset,
            arrow=tk.LAST,
            fill="#AAAAAA",
            width=2
        )

    # ---- Draw ONE circular back arrow (Nn -> N1) ----
    if zones > 1:
        x_start, y_start = node_positions[-1]
        x_end, y_end = node_positions[0]

        canvas.create_line(
            x_start, y_start + back_arrow_offset,
            x_end, y_end + back_arrow_offset,
            smooth=True,
            arrow=tk.LAST,
            fill="#AAAAAA",
            width=2
        )

    # ---- Label ----
    canvas.create_text(
        width // 2,
        15,
        text="next pointer",
        fill="#777777",
        font=("Segoe UI", 9)
    )

def upload_txt_file():
    file_path = filedialog.askopenfilename(
        title="Select a text file",
        filetypes=[("Text files", "*.txt")]
    )

    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        if not content.strip():
            messagebox.showwarning("Empty File", "Selected file is empty.")
            return

        input_box.config(state="normal")
        input_box.delete("1.0", tk.END)
        input_box.insert(tk.END, content)
        input_box.config(state="disabled")

    except Exception as e:
        messagebox.showerror("File Error", f"Could not read file:\n{e}")


def run_pipeline():
    input_box.config(state="normal")
    raw_text = input_box.get("1.0", tk.END)
    input_box.config(state="disabled")
    if not raw_text:
        return
    refined_nodes = set()   # 🔴 NEW: track refined nodes visually


    logs, final_output, metrics = run_refinement(raw_text)
    zones_count = metrics["zones"]

    # Initial draw (all nodes unrefined)
    draw_circular_list(
        list_canvas,
        zones=zones_count,
        active_zone=1,
        refined_zones=set()
    )
    root.update_idletasks()

    stages_box.config(state="normal")
    output_box.config(state="normal")

    stages_box.delete("1.0", tk.END)
    output_box.delete("1.0", tk.END)

    # --------- ANIMATE CIRCULAR LINKED LIST TRAVERSAL ---------
    for entry in logs:

        # Only process structured traversal logs
        if isinstance(entry, dict):

            # 🔁 Node visit
            if entry["event"] == "visit":
                draw_circular_list(
                    list_canvas,
                    zones_count,
                    active_zone=entry["zone"],
                    refined_zones=refined_nodes
                )

                stages_box.insert(
                    tk.END,
                    f"→ Visiting Node {entry['zone']}\n"
                )

                root.update()
                root.after(300)

            # ✅ Node refined
            elif entry["event"] == "refined":
                refined_nodes.add(entry["zone"])

                draw_circular_list(
                    list_canvas,
                    zones_count,
                    active_zone=None,
                    refined_zones=refined_nodes
                )

                stages_box.insert(
                    tk.END,
                    f"✓ Node {entry['zone']} refined — skipping in next cycles\n"
                )

                root.update()
                root.update_idletasks()
                root.after(300)


    stages_box.insert(tk.END, "CIRCULAR LINKED LIST NODES\n")
    stages_box.insert(tk.END, "-------------------------\n\n")


    stages_box.insert(
        tk.END,
        "Traversal completed using Circular Linked List\n"
        "Only unrefined nodes revisited in each cycle\n\n"
    )

    stages_box.insert(tk.END, "--- Efficiency Metrics ---\n")
    stages_box.insert(tk.END, f"Total passes: {metrics['total_passes']}\n")
    stages_box.insert(tk.END, f"Total changes: {metrics['total_changes']}\n")
    stages_box.insert(tk.END, f"Efficiency gain: {metrics['efficiency_gain']:.1f}%\n")


    stages_box.insert(
        tk.END,
        "\nIteration completed using Circular Linked List traversal.\n"
        "Only unrefined zones were revisited in each cycle.\n"
    )

    output_box.insert(tk.END, final_output)

    stages_box.config(state="disabled")
    output_box.config(state="disabled")

# ------------------ ROOT ------------------
root = tk.Tk()
root.title("Iterative Text Refinement System")
root.geometry("1100x720")
root.configure(bg=BG_MAIN)

# ------------------ HEADER ------------------
header = tk.Frame(root, bg=ACCENT, height=45)
header.pack(fill="x")

tk.Label(
    header,
    text="Iterative Text Refinement System",
    bg=ACCENT,
    fg="white",
    font=("Segoe UI", 14, "bold")
).pack(pady=8)

# ------------------ INPUT ------------------
input_frame = tk.Frame(root, bg=BG_MAIN)
input_frame.pack(fill="x", padx=12, pady=10)

tk.Label(
    input_frame,
    text="RAW Input Text",
    bg=BG_MAIN,
    fg=FG_TEXT,
    font=FONT_TITLE
).pack(anchor="w")

input_box = scrolledtext.ScrolledText(
    input_frame,
    height=7,
    wrap=tk.WORD,
    bg=BG_TEXT,
    fg=FG_TEXT,
    insertbackground="white",
    font=FONT_MAIN
)
input_box.pack(fill="x", pady=6)
input_box.config(state="disabled")


# ------------------ UPLOAD BUTTON ------------------
upload_btn = tk.Button(
    root,
    text="Upload .txt File",
    command=upload_txt_file,
    bg="#4A90E2",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    padx=16,
    pady=5
)
upload_btn.pack(pady=(10, 0))


# ------------------ BUTTON ------------------
btn = tk.Button(
    root,
    text="Run Refinement",
    command=run_pipeline,
    bg="#2ECC71",
    fg="#000000",
    font=FONT_TITLE,
    relief="flat",
    padx=20,
    pady=6
)
btn.pack(pady=10)

# Hover effect
btn.bind("<Enter>", lambda e: btn.config(bg="#27AE60"))
btn.bind("<Leave>", lambda e: btn.config(bg="#2ECC71"))

# ------------------ OUTPUT PANELS ------------------
panel = tk.Frame(root, bg=BG_MAIN)
panel.pack(fill="both", expand=True, padx=12, pady=10)

# LEFT: STAGES
left = tk.Frame(panel, bg=BG_PANEL)
left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

# --------- CIRCULAR LINKED LIST VISUAL ---------
tk.Label(
    left,
    text="Circular Linked List View",
    bg=BG_PANEL,
    fg=FG_TEXT,
    font=FONT_TITLE
).pack(anchor="w", padx=8, pady=(6, 2))

canvas_frame = tk.Frame(left, bg=BG_PANEL)
canvas_frame.pack(fill="x", padx=8)

list_canvas = tk.Canvas(
    canvas_frame,
    height=140,
    bg="#111111",
    highlightthickness=1,
    highlightbackground="#333333"
)
list_canvas.pack(fill="x")

tk.Label(
    left,
    text="Refinement STAGES:-",
    bg=BG_PANEL,
    fg=FG_TEXT,
    font=FONT_TITLE
).pack(anchor="w", padx=8, pady=(6, 2))

stages_box = scrolledtext.ScrolledText(
    left,
    wrap=tk.WORD,
    bg=BG_TEXT,
    fg="#CCCCCC",
    font=FONT_MONO,
    state="disabled"
)
stages_box.pack(fill="both", expand=True, padx=8, pady=6)

# RIGHT: FINAL OUTPUT
right = tk.Frame(panel, bg=BG_PANEL)
right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

tk.Label(
    right,
    text="FINAL Output:-",
    bg=BG_PANEL,
    fg=FG_TEXT,
    font=FONT_TITLE
).pack(anchor="w", padx=8, pady=(6, 2))

output_box = scrolledtext.ScrolledText(
    right,
    wrap=tk.WORD,
    bg=BG_TEXT,
    fg=FG_TEXT,
    font=FONT_MAIN,
    state="disabled"
)
output_box.pack(fill="both", expand=True, padx=8, pady=6)

panel.columnconfigure(0, weight=1)
panel.columnconfigure(1, weight=1)
panel.rowconfigure(0, weight=1)

root.mainloop()
