from graphviz import Digraph


def generate_architecture_flowchart():
    # Initialize the main directed graph
    dot = Digraph(comment="Space Debris ML Pipeline", format="png")
    dot.attr(rankdir="TB", dpi="300")
    dot.attr(
        "node", shape="box", style="rounded,filled", fontname="Helvetica", fontsize="12"
    )

    # --- CLUSTER 1: Data Sources ---
    c1 = Digraph(name="cluster_sources")
    c1.attr(style="filled", color="#e1f5fe")
    c1.attr(label="Step 1: Data Aggregation", fontname="Helvetica-Bold")
    c1.node("TLE", "CelesTrak\n(Two-Line Elements)", fillcolor="#b3e5fc")
    c1.node("NASA", "NASA APIs\n(DONKI, NeoWs)", fillcolor="#b3e5fc")
    dot.subgraph(c1)

    # --- CLUSTER 2: Backend ML Pipeline ---
    c2 = Digraph(name="cluster_backend")
    c2.attr(style="filled", color="#e8f5e9")
    c2.attr(label="Step 2 & 3: FastAPI Backend & ML Engine", fontname="Helvetica-Bold")
    c2.node(
        "Preprocess",
        "Data Preprocessing\n(Extract Keplerian Elements)",
        fillcolor="#c8e6c9",
    )
    c2.node(
        "Feature",
        "Feature Engineering\n(Scalar Velocity, Altitude)",
        fillcolor="#a5d6a7",
    )
    c2.node(
        "RF",
        "Random Forest Classifier\n(Active, Derelict, Debris)",
        fillcolor="#81c784",
        shape="Mdiamond",
    )
    c2.node(
        "Math", "Covariance Matrices &\nMahalanobis Distance (Pc)", fillcolor="#c8e6c9"
    )
    c2.edge("Preprocess", "Feature")
    c2.edge("Feature", "RF")
    c2.edge("RF", "Math")
    dot.subgraph(c2)

    # --- CLUSTER 3: Frontend Visualization ---
    c3 = Digraph(name="cluster_frontend")
    c3.attr(style="filled", color="#fff3e0")
    c3.attr(label="Step 4: WebGL Frontend", fontname="Helvetica-Bold")
    c3.node(
        "SGP4", "SGP4 Kinematic Propagation\n(Native Client GPU)", fillcolor="#ffe0b2"
    )
    c3.node("Render", "60 FPS 3D Render\n(React-Three-Fiber)", fillcolor="#ffcc80")
    c3.node(
        "Alert", "Critical Conjunction Alert\n& Kessler Swarm UI", fillcolor="#ffb74d"
    )
    c3.edge("SGP4", "Render")
    c3.edge("Render", "Alert")
    dot.subgraph(c3)

    # --- Connect the Clusters ---
    dot.edge("TLE", "Preprocess")
    dot.edge("NASA", "Preprocess")
    dot.edge(
        "Math",
        "SGP4",
        label=" Standardized Geodetic Vectors",
        fontname="Helvetica-Oblique",
        fontsize="10",
    )

    # Render and save the file
    dot.render("Space_Debris_Architecture", view=True)
    print("Flowchart successfully generated as 'Space_Debris_Architecture.png'")


if __name__ == "__main__":
    generate_architecture_flowchart()
