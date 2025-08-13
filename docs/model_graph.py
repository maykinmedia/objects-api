import os

from django.core.management import call_command


def generate_model_graphs(app):
    output_dir = os.path.join(app.srcdir, "_static", "uml")
    os.makedirs(output_dir, exist_ok=True)

    django_app_label = "core"

    png_path = os.path.join(output_dir, f"{django_app_label}.png")
    try:
        call_command(
            "graph_models",
            django_app_label,
            output=png_path,
            rankdir="LR",
            hide_edge_labels=True,
        )
        print(f"Generated diagram for {django_app_label}")
    except Exception as exc:
        print(f"Failed to generate PNG for {django_app_label}: {exc}")
