import tkinter as tk
from tkinter import colorchooser, messagebox
import time

# ============================================================
# CHROMATIC STUDIO - Interactive Graph Colouring Simulator
# Editable graph + RGB colour picker + Backtracking algorithm
# ============================================================

BG = "#0B1120"
PANEL = "#151F32"
CARD = "#1C2940"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"
ACCENT = "#38BDF8"
GREEN = "#34D399"
RED = "#FB7185"

# The palette stores RGB colours as hexadecimal strings.
palette = ["#22D3EE", "#A78BFA", "#4ADE80", "#FB923C"]

nodes = {}                 # Example: {"N1": (x, y), "N2": (x, y)}
edges = set()              # Example: {("N1", "N2")}
next_node_id = 1
selected_node = None
edge_start = None
assignment = {}
search_steps = 0
step_solution = None
step_index = 0


def normalized_edge(a, b):
    """Store an edge in a consistent order."""
    return tuple(sorted((a, b)))


def neighbors(node):
    """Return nodes directly connected to node."""
    result = []
    for a, b in edges:
        if a == node:
            result.append(b)
        elif b == node:
            result.append(a)
    return result


def clear_colouring(redraw=True):
    """Clear colours while keeping nodes and edges."""
    global assignment, step_solution, step_index
    assignment = {}
    step_solution = None
    step_index = 0
    result_var.set("Colours cleared. Your graph is still here.")
    if redraw:
        draw_graph()


def is_valid(node, colour, current):
    """A node cannot share a colour with a connected neighbour."""
    return all(current.get(other) != colour for other in neighbors(node))


def backtracking_solve(current):
    """Find a valid colouring using recursive backtracking."""
    global search_steps

    if len(current) == len(nodes):
        return current.copy()

    # Choose the first node that has not been coloured yet.
    node = next(n for n in nodes if n not in current)

    for colour in palette:
        search_steps += 1
        if is_valid(node, colour, current):
            current[node] = colour
            result = backtracking_solve(current)
            if result is not None:
                return result
            del current[node]  # Backtrack

    return None


def find_node(x, y):
    """Return the node under the mouse pointer, if any."""
    for node, (nx, ny) in nodes.items():
        if (x - nx) ** 2 + (y - ny) ** 2 <= 31 ** 2:
            return node
    return None


def update_stats():
    node_stat.config(text=str(len(nodes)))
    edge_stat.config(text=str(len(edges)))
    colour_stat.config(text=str(len(set(assignment.values()))))
    step_stat.config(text=str(search_steps))


def draw_graph():
    canvas.delete("all")
    width = max(canvas.winfo_width(), 650)
    height = max(canvas.winfo_height(), 450)

    # Background grid
    for x in range(0, width, 30):
        canvas.create_line(x, 0, x, height, fill="#172238")
    for y in range(0, height, 30):
        canvas.create_line(0, y, width, y, fill="#172238")

    # Draw edges behind nodes
    for a, b in sorted(edges):
        if a in nodes and b in nodes:
            x1, y1 = nodes[a]
            x2, y2 = nodes[b]
            canvas.create_line(x1, y1, x2, y2, fill="#94A3B8", width=3)

    # Draw nodes
    for node, (x, y) in nodes.items():
        colour = assignment.get(node)
        fill = colour if colour else CARD
        outline = ACCENT if node in (selected_node, edge_start) else "#64748B"

        if colour:
            canvas.create_oval(
                x - 33, y - 33, x + 33, y + 33,
                fill="#24364D", outline=""
            )

        canvas.create_oval(
            x - 27, y - 27, x + 27, y + 27,
            fill=fill, outline=outline, width=3
        )
        canvas.create_text(
            x, y, text=node,
            fill=BG if colour else TEXT,
            font=("Segoe UI", 11, "bold")
        )

    update_stats()


def canvas_click(event):
    """Normal mode: add/select nodes. Edge mode: click two nodes to connect."""
    global next_node_id, selected_node, edge_start

    hit = find_node(event.x, event.y)

    if edge_mode.get():
        if hit is None:
            result_var.set("Add Edge mode: click directly on an existing node.")
            return

        if edge_start is None:
            edge_start = hit
            selected_node = hit
            result_var.set(f"First node: {hit}. Now click a second node.")
            draw_graph()
            return

        if hit == edge_start:
            result_var.set("Choose a different node for the second end of the edge.")
            return

        edge = normalized_edge(edge_start, hit)
        if edge in edges:
            result_var.set(f"{edge_start} and {hit} are already connected.")
        else:
            edges.add(edge)
            clear_colouring(redraw=False)
            result_var.set(f"Connected {edge_start} — {hit}.")
        edge_start = None
        selected_node = None
        draw_graph()
        return

    # Normal mode: clicking an existing node selects it.
    if hit is not None:
        selected_node = hit
        result_var.set(f"Selected {hit}. Use Delete Selected Node to remove it.")
        draw_graph()
        return

    # Clicking empty canvas creates a node.
    node_name = f"N{next_node_id}"
    next_node_id += 1
    nodes[node_name] = (event.x, event.y)
    selected_node = node_name
    edge_start = None
    clear_colouring(redraw=False)
    result_var.set(f"Added {node_name}. Enable Add Edge Mode to connect nodes.")
    draw_graph()


def delete_selected_node():
    global selected_node, edge_start
    if selected_node is None:
        messagebox.showinfo("Select a node", "Click a node first, then choose Delete Selected Node.")
        return

    removed = selected_node
    nodes.pop(removed, None)
    edges.difference_update({edge for edge in edges if removed in edge})
    selected_node = None
    edge_start = None
    clear_colouring(redraw=False)
    result_var.set(f"Deleted {removed} and its connections.")
    draw_graph()


def delete_selected_edge():
    """Remove an edge by selecting its two endpoints in Add Edge mode."""
    global edge_start, selected_node

    if edge_start is None or selected_node is None or edge_start == selected_node:
        messagebox.showinfo(
            "Delete Edge",
            "Turn on Add Edge Mode, click the first endpoint, then click the second endpoint. "
            "To delete an edge, use the dedicated 'Delete Last Edge' button instead."
        )
        return

    edge = normalized_edge(edge_start, selected_node)
    if edge in edges:
        edges.remove(edge)
        clear_colouring(redraw=False)
        result_var.set(f"Removed edge {edge[0]} — {edge[1]}.")
    else:
        result_var.set("Those nodes are not connected.")
    edge_start = None
    selected_node = None
    draw_graph()


def delete_last_edge():
    global edge_start, selected_node
    if not edges:
        result_var.set("There are no edges to delete.")
        return
    edge = sorted(edges)[-1]
    edges.remove(edge)
    edge_start = None
    selected_node = None
    clear_colouring(redraw=False)
    result_var.set(f"Deleted connection {edge[0]} — {edge[1]}.")
    draw_graph()


def add_custom_colour():
    """Choose a colour and show its RGB values."""
    chosen = colorchooser.askcolor(title="Choose an RGB colour")
    rgb, hex_colour = chosen

    if not hex_colour:
        return

    hex_colour = hex_colour.upper()
    if hex_colour not in [c.upper() for c in palette]:
        palette.append(hex_colour)
        refresh_palette()
        clear_colouring(redraw=False)

    r, g, b = [int(value) for value in rgb]
    result_var.set(f"Selected RGB({r}, {g}, {b})  |  HEX {hex_colour}")
    draw_graph()


def refresh_palette():
    for widget in palette_frame.winfo_children():
        widget.destroy()

    for colour in palette:
        # Convert HEX to RGB for display.
        r = int(colour[1:3], 16)
        g = int(colour[3:5], 16)
        b = int(colour[5:7], 16)

        row = tk.Frame(palette_frame, bg=PANEL)
        row.pack(fill="x", pady=2)

        tk.Label(
            row, text="   ", bg=colour, width=3
        ).pack(side="left", padx=(0, 6))

        tk.Label(
            row, text=f"{colour}  RGB({r},{g},{b})",
            bg=PANEL, fg=TEXT, font=("Segoe UI", 8)
        ).pack(side="left")


def solve_graph():
    global assignment, search_steps, step_solution, step_index

    if not nodes:
        messagebox.showinfo("Empty Graph", "Click the canvas to add at least one node.")
        return

    search_steps = 0
    start = time.perf_counter()
    result = backtracking_solve({})
    elapsed = (time.perf_counter() - start) * 1000

    if result is None:
        assignment = {}
        draw_graph()
        result_var.set("No valid colouring with the current palette. Add another colour.")
        messagebox.showwarning(
            "No Valid Colouring",
            "The graph cannot be coloured with the available palette. "
            "Choose Add RGB Colour and try again."
        )
        return

    assignment = result
    step_solution = result.copy()
    step_index = len(nodes)
    draw_graph()
    used = len(set(result.values()))
    result_var.set(f"Solution found: {used} colour(s), {search_steps} search steps, {elapsed:.2f} ms.")


def start_step_by_step():
    global step_solution, step_index, assignment, search_steps

    if not nodes:
        messagebox.showinfo("Empty Graph", "Add at least one node first.")
        return

    search_steps = 0
    step_solution = backtracking_solve({})
    if step_solution is None:
        result_var.set("No solution with current palette. Add another RGB colour.")
        messagebox.showwarning("No Solution", "Add another colour or change the graph.")
        draw_graph()
        return

    step_index = 0
    assignment = {}
    result_var.set("Step-by-step mode started. Click Next Step.")
    draw_graph()


def next_step():
    global step_index, assignment

    if step_solution is None:
        start_step_by_step()
        if step_solution is None:
            return

    node_order = list(nodes.keys())
    if step_index >= len(node_order):
        result_var.set("Step-by-step colouring is complete.")
        return

    node = node_order[step_index]
    assignment[node] = step_solution[node]
    step_index += 1
    draw_graph()
    result_var.set(f"Step {step_index}/{len(node_order)}: coloured {node}.")


def check_conflicts():
    conflicts = []
    for a, b in edges:
        if assignment.get(a) and assignment.get(a) == assignment.get(b):
            conflicts.append((a, b))

    if conflicts:
        messagebox.showwarning(
            "Colour Conflicts",
            "Conflicts found:\n" + "\n".join(f"{a} — {b}" for a, b in conflicts)
        )
        result_var.set(f"Found {len(conflicts)} conflict(s).")
    else:
        messagebox.showinfo("Conflict Check", "No colour conflicts found.")
        result_var.set("Conflict check passed.")


def minimum_colour_count():
    """Find the smallest palette size that can colour this graph."""
    if not nodes:
        return 0, 0

    original_palette = palette[:]
    total_steps = 0
    try:
        # Each node can have a different colour in the worst case.
        generated = []
        for i in range(len(nodes)):
            generated.append(f"#{(i * 2654435 + 0x123456) % 0xFFFFFF:06X}")

        for k in range(1, len(nodes) + 1):
            palette[:] = (original_palette + generated)[:k]
            global search_steps
            search_steps = 0
            result = backtracking_solve({})
            total_steps = search_steps
            if result is not None:
                return k, total_steps
        return len(nodes), total_steps
    finally:
        palette[:] = original_palette
        refresh_palette()


def show_minimum_colours():
    start = time.perf_counter()
    k, steps = minimum_colour_count()
    elapsed = (time.perf_counter() - start) * 1000
    messagebox.showinfo(
        "Minimum Colour Estimate",
        f"Minimum colours needed: {k}\nSearch steps: {steps}\nTime: {elapsed:.2f} ms"
    )
    result_var.set(f"Minimum colour count: {k} (estimated by backtracking).")


def reset_graph():
    global nodes, edges, next_node_id, selected_node, edge_start
    nodes = {}
    edges = set()
    next_node_id = 1
    selected_node = None
    edge_start = None
    clear_colouring(redraw=False)
    result_var.set("New graph. Click empty canvas to add nodes.")
    draw_graph()


# -------------------- USER INTERFACE --------------------

root = tk.Tk()
root.title("Chromatic Studio | Interactive Graph Colouring")
root.geometry("1180x760")
root.minsize(980, 650)
root.configure(bg=BG)

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=22, pady=(16, 10))

tk.Label(
    header, text="CHROMATIC STUDIO",
    font=("Segoe UI", 22, "bold"), bg=BG, fg=ACCENT
).pack(side="left")

tk.Label(
    header, text="INTERACTIVE GRAPH COLOURING  •  BACKTRACKING",
    font=("Segoe UI", 9, "bold"), bg=BG, fg=MUTED
).pack(side="right", pady=8)

stats = tk.Frame(root, bg=BG)
stats.pack(fill="x", padx=18, pady=5)


def stat_card(parent, title, value, accent):
    card = tk.Frame(parent, bg=PANEL, highlightbackground="#263449", highlightthickness=1)
    card.pack(side="left", fill="x", expand=True, padx=4)
    tk.Label(
        card, text=title.upper(), font=("Segoe UI", 9, "bold"),
        bg=PANEL, fg=MUTED
    ).pack(anchor="w", padx=12, pady=(9, 0))
    label = tk.Label(
        card, text=value, font=("Segoe UI", 19, "bold"),
        bg=PANEL, fg=accent
    )
    label.pack(anchor="w", padx=12, pady=(0, 8))
    return label


node_stat = stat_card(stats, "Nodes", "0", ACCENT)
edge_stat = stat_card(stats, "Edges", "0", GREEN)
colour_stat = stat_card(stats, "Colours Used", "0", "#C4B5FD")
step_stat = stat_card(stats, "Search Steps", "0", "#FBBF24")

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=22, pady=10)

graph_panel = tk.Frame(main, bg=PANEL, highlightbackground="#263449", highlightthickness=1)
graph_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

tk.Label(
    graph_panel, text="  GRAPH CANVAS",
    font=("Segoe UI", 11, "bold"), bg=PANEL, fg=TEXT
).pack(anchor="w", padx=10, pady=10)

canvas = tk.Canvas(graph_panel, bg="#10192A", highlightthickness=0, cursor="crosshair")
canvas.pack(fill="both", expand=True, padx=8, pady=(0, 8))
canvas.bind("<Button-1>", canvas_click)

tools_panel = tk.Frame(main, bg=PANEL, width=270, highlightbackground="#263449", highlightthickness=1)
tools_panel.pack(side="right", fill="y")
tools_panel.pack_propagate(False)

tk.Label(
    tools_panel, text="  GRAPH TOOLS",
    font=("Segoe UI", 11, "bold"), bg=PANEL, fg=TEXT
).pack(anchor="w", padx=10, pady=(12, 8))

edge_mode = tk.BooleanVar(value=False)
tk.Checkbutton(
    tools_panel, text="Add Edge Mode (click 2 nodes)",
    variable=edge_mode, bg=PANEL, fg=ACCENT, selectcolor=CARD,
    activebackground=PANEL, activeforeground=ACCENT,
    font=("Segoe UI", 9, "bold"), anchor="w"
).pack(fill="x", padx=10, pady=3)


def tool_button(text, command, bg="#263449", fg=TEXT):
    tk.Button(
        tools_panel, text=text, command=command,
        bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2",
        font=("Segoe UI", 9, "bold"), pady=7
    ).pack(fill="x", padx=10, pady=3)


tool_button("+  Add RGB Colour", add_custom_colour, ACCENT, BG)
tool_button("Solve Graph", solve_graph, GREEN, BG)
tool_button("Start Step-by-Step", start_step_by_step)
tool_button("Next Step", next_step)
tool_button("Check Conflicts", check_conflicts)
tool_button("Estimate Minimum Colours", show_minimum_colours)
tool_button("Delete Selected Node", delete_selected_node)
tool_button("Delete Last Edge", delete_last_edge)
tool_button("Reset Colours", clear_colouring)
tool_button("New Graph", reset_graph, RED, BG)

tk.Label(
    tools_panel, text="  RGB COLOUR PALETTE",
    font=("Segoe UI", 10, "bold"), bg=PANEL, fg=TEXT
).pack(anchor="w", padx=10, pady=(12, 4))

palette_frame = tk.Frame(tools_panel, bg=PANEL)
palette_frame.pack(fill="x", padx=10)
refresh_palette()

tk.Label(
    tools_panel,
    text="HOW TO USE\n"
         "1. Click empty canvas to add nodes.\n"
         "2. Turn on Add Edge Mode.\n"
         "3. Click two nodes to connect them.\n"
         "4. Add an RGB colour if needed.\n"
         "5. Click Solve Graph.\n\n"
         "Tip: turn off Add Edge Mode to add nodes.",
    justify="left", anchor="w",
    font=("Segoe UI", 8), bg=PANEL, fg=MUTED
).pack(fill="x", padx=12, pady=(12, 6))

footer = tk.Frame(root, bg=BG)
footer.pack(fill="x", padx=24, pady=(0, 12))

result_var = tk.StringVar(value="Graph ready. Click empty canvas to add nodes.")
tk.Label(
    footer, textvariable=result_var, font=("Segoe UI", 9),
    bg=BG, fg=ACCENT, anchor="w"
).pack(fill="x")

root.after(100, draw_graph)
root.mainloop()
