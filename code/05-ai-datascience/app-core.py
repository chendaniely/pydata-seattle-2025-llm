from pathlib import Path

import faicons as fa
import plotly.express as px
import pandas as pd

import seaborn as sns
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_plotly
import chatlas
import querychat

tips = sns.load_dataset("tips")

greeting = Path(__file__).parent / "greeting.md"
data_desc = Path(__file__).parent / "data_description.md"


def use_github_models(system_prompt: str) -> chatlas.Chat:
    # GitHub models give us free rate-limited access to the latest LLMs
    # you will need to have GITHUB_PAT defined in your environment
    return chatlas.ChatGithub(
        model="gpt-4.1",
        system_prompt=system_prompt,
    )


qc_config = querychat.init(
    tips,
    "tips",
    greeting=greeting,
    data_description=data_desc,
    client=use_github_models,
)


bill_rng = (
    tips["total_bill"].min(),
    tips["total_bill"].max(),
)

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

# Add page title and sidebar
app_ui = ui.page_sidebar(
    querychat.sidebar("chat"),
    ui.layout_columns(
        ui.value_box(
            "Total tippers",
            ui.output_ui("total_tippers"),
            showcase=ICONS["user"],
        ),
        ui.value_box(
            "Average tip",
            ui.output_ui("average_tip"),
            showcase=ICONS["wallet"],
        ),
        ui.value_box(
            "Average bill",
            ui.output_ui("average_bill"),
            showcase=ICONS["currency-dollar"],
        ),
        fill=False,
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Tips data"),
            ui.output_data_frame("table"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header(
                "Total bill vs tip",
                ui.popover(
                    ICONS["ellipsis"],
                    ui.input_radio_buttons(
                        "scatter_color",
                        None,
                        ["none", "sex", "smoker", "day", "time"],
                        inline=True,
                    ),
                    title="Add a color variable",
                    placement="top",
                ),
                class_="d-flex justify-content-between align-items-center",
            ),
            output_widget("scatterplot"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header(
                "Tip percentages",
                ui.popover(
                    ICONS["ellipsis"],
                    ui.input_radio_buttons(
                        "tip_perc_y",
                        "Split by:",
                        ["sex", "smoker", "day", "time"],
                        selected="day",
                        inline=True,
                    ),
                    title="Add a color variable",
                ),
                class_="d-flex justify-content-between align-items-center",
            ),
            output_widget("tip_perc"),
            full_screen=True,
        ),
        col_widths=[6, 6, 12],
    ),
    title="Restaurant tipping",
    fillable=True,
)


def server(input, output, session):
    qc = querychat.server("chat", qc_config)

    @reactive.calc
    def filtered_data():
        return qc.df()

    @render.ui
    def total_tippers():
        return len(filtered_data())

    @render.ui
    def average_tip():
        df = filtered_data()
        if len(df) > 0:
            d = (df["tip"] / df["total_bill"]).mean()
            return f"{d:.1%}"
        else:
            return "N/A"

    @render.ui
    def average_bill():
        df = filtered_data()
        if len(df) > 0:
            d = df["total_bill"].mean()
            return f"${d:.2f}"
        else:
            return "N/A"

    @render.data_frame
    def table():
        return render.DataGrid(filtered_data())

    @render_plotly
    def scatterplot():
        color = input.scatter_color()
        return px.scatter(
            filtered_data(),
            x="total_bill",
            y="tip",
            color=None if color == "none" else color,
            trendline="lowess",
        )

    @render_plotly
    def tip_perc():
        from ridgeplot import ridgeplot

        filtered_data()["percent"] = (
            filtered_data().tip / filtered_data().total_bill
        )

        uvals = filtered_data().day.unique()
        samples = [
            [filtered_data().percent[filtered_data().day == val]]
            for val in uvals
        ]

        plt = ridgeplot(
            samples=samples,
            labels=uvals,
            bandwidth=0.01,
            colorscale="viridis",
            colormode="row-index",
        )

        plt.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
            )
        )

        return plt

    @reactive.effect
    @reactive.event(input.reset)
    def _():
        ui.update_slider("total_bill", value=bill_rng)
        ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])


app = App(app_ui, server)
